"""Build versioned Morphkit documentation for GitHub Pages."""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
SEMVER_RE = re.compile(r"^v(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)$")


@dataclass(frozen=True)
class ReleaseRef:
    ref: str
    version: str
    slug: str

    @property
    def sort_key(self) -> tuple[int, int, int]:
        major, minor, patch = self.version.split(".")
        return int(major), int(minor), int(patch)


def run(command: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None) -> str:
    completed = subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        env=env,
        check=True,
        text=True,
        capture_output=True,
    )
    return completed.stdout.strip()


def normalize_release_tag(tag: str) -> ReleaseRef | None:
    match = SEMVER_RE.fullmatch(tag)
    if not match:
        return None

    major = int(match.group("major"))
    minor = int(match.group("minor"))
    patch = int(match.group("patch") or 0)
    version = f"{major}.{minor}.{patch}"
    return ReleaseRef(ref=tag, version=version, slug=f"v{version}")


def discover_release_refs() -> list[ReleaseRef]:
    refs_by_slug: dict[str, ReleaseRef] = {}
    tags = run(["git", "tag", "--list", "v*"], cwd=REPO_ROOT).splitlines()

    for tag in tags:
        release_ref = normalize_release_tag(tag.strip())
        if release_ref is None:
            continue
        refs_by_slug[release_ref.slug] = release_ref

    return sorted(refs_by_slug.values(), key=lambda item: item.sort_key)


def discover_current_release() -> ReleaseRef:
    version_ns: dict[str, str] = {}
    exec((REPO_ROOT / "morphkit" / "_version.py").read_text(encoding="utf-8"), version_ns)
    version = version_ns["__version__"]
    return ReleaseRef(ref="HEAD", version=version, slug=f"v{version}")


def build_versions_entries(releases: list[ReleaseRef], current_release: ReleaseRef) -> list[dict[str, str]]:
    versions: list[dict[str, str]] = [{"slug": "dev", "title": "Development"}]

    if releases:
        latest_release = releases[-1]
        versions.insert(0, {"slug": "stable", "title": f"Stable ({latest_release.version})"})
        for release in reversed(releases):
            versions.append({"slug": release.slug, "title": release.slug})
    else:
        versions.insert(0, {"slug": "stable", "title": "Stable (current baseline)"})
        versions.append({"slug": current_release.slug, "title": current_release.slug})

    return versions


def sync_docs_infra(source_root: Path) -> None:
    if source_root == REPO_ROOT:
        return

    current_docs_source = REPO_ROOT / "docs" / "source"
    target_docs_source = source_root / "docs" / "source"

    shutil.copy2(current_docs_source / "conf.py", target_docs_source / "conf.py")
    for docs_page in ("index.rst", "architecture.rst", "license.rst"):
        shutil.copy2(current_docs_source / docs_page, target_docs_source / docs_page)

    target_templates = target_docs_source / "_templates"
    if target_templates.exists():
        shutil.rmtree(target_templates)
    shutil.copytree(current_docs_source / "_templates", target_templates)

    target_static = target_docs_source / "_static"
    target_static.mkdir(parents=True, exist_ok=True)
    for asset_name in ("version-selector.css", "version-selector.js"):
        shutil.copy2(current_docs_source / "_static" / asset_name, target_static / asset_name)


def build_docs(source_root: Path, output_dir: Path, label: str, versions: list[dict[str, str]]) -> None:
    sync_docs_infra(source_root)
    env = os.environ.copy()
    env["MORPHKIT_DOCS_LABEL"] = label
    env["MORPHKIT_DOCS_VERSIONS"] = json.dumps(versions)
    with tempfile.TemporaryDirectory(prefix=f"morphkit-docs-{label}-") as build_dir:
        temp_output_dir = Path(build_dir) / "html"
        doctree_dir = Path(build_dir) / "doctrees"
        run(
            [
                sys.executable,
                "-m",
                "sphinx",
                "-b",
                "html",
                "-d",
                str(doctree_dir),
                str(source_root / "docs" / "source"),
                str(temp_output_dir),
            ],
            cwd=source_root,
            env=env,
        )
        if output_dir.exists():
            shutil.rmtree(output_dir)
        shutil.copytree(temp_output_dir, output_dir)


def build_ref(
    ref: str,
    slug: str,
    output_root: Path,
    worktree_root: Path,
    versions: list[dict[str, str]],
    *,
    label: str | None = None,
) -> None:
    worktree_path = worktree_root / f"{slug}-{label or slug}"
    run(["git", "worktree", "add", "--detach", str(worktree_path), ref], cwd=REPO_ROOT)
    try:
        build_docs(worktree_path, output_root / slug, label or slug, versions)
    finally:
        try:
            run(["git", "reset", "--hard"], cwd=worktree_path)
            run(["git", "clean", "-fd"], cwd=worktree_path)
        except subprocess.CalledProcessError:
            pass
        try:
            run(["git", "worktree", "remove", "--force", str(worktree_path)], cwd=REPO_ROOT)
        except subprocess.CalledProcessError:
            run(["git", "worktree", "prune"], cwd=REPO_ROOT)


def write_redirect(output_root: Path, target_slug: str) -> None:
    redirect = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="refresh" content="0; url=./{target_slug}/">
    <title>Morphkit Documentation</title>
  </head>
  <body>
    <p>Redirecting to <a href="./{target_slug}/">the Morphkit documentation</a>.</p>
  </body>
</html>
"""
    (output_root / "index.html").write_text(redirect, encoding="utf-8")


def write_versions_manifest(output_root: Path, entries: Iterable[dict[str, str]]) -> None:
    versions = []
    for entry in entries:
        version_entry = dict(entry)
        version_entry["url"] = f"../../{entry['slug']}/"
        versions.append(version_entry)

    manifest_text = json.dumps({"versions": versions}, indent=2) + "\n"
    (output_root / "versions.json").write_text(manifest_text, encoding="utf-8")

    for entry in versions:
        static_manifest = output_root / entry["slug"] / "_static" / "versions.json"
        static_manifest.parent.mkdir(parents=True, exist_ok=True)
        static_manifest.write_text(manifest_text, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        default=str(REPO_ROOT / "docs" / "_site"),
        help="Directory where the versioned site should be written.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_root = Path(args.output).resolve()

    if output_root.exists():
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    releases = discover_release_refs()
    current_release = discover_current_release()
    versions = build_versions_entries(releases, current_release)

    with tempfile.TemporaryDirectory(prefix="morphkit-docs-") as temp_dir:
        worktree_root = Path(temp_dir)

        build_docs(REPO_ROOT, output_root / "dev", "dev", versions)
        if releases:
            latest_release = releases[-1]
            build_ref(latest_release.ref, "stable", output_root, worktree_root, versions, label="stable")
            for release in releases:
                build_ref(release.ref, release.slug, output_root, worktree_root, versions)
        else:
            build_docs(REPO_ROOT, output_root / "stable", "stable", versions)
            build_docs(REPO_ROOT, output_root / current_release.slug, current_release.slug, versions)

    write_redirect(output_root, "stable")

    write_versions_manifest(output_root, versions)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

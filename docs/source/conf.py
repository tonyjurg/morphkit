from __future__ import annotations

import json
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

version_ns: dict[str, str] = {}
exec((ROOT / "morphkit" / "_version.py").read_text(encoding="utf-8"), version_ns)

project = "morphkit"
author = "Tony Jurg"
copyright = "2026, Tony Jurg"
master_doc = "index"
version = version_ns["__version__"]
release = version
html_title = f"Morphkit {release} Documentation"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

templates_path = ["_templates"]
html_sidebars = {
    "**": [
        "searchbox.html",
        "version-selector.html",
        "globaltoc.html",
    ]
}
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "api/functions.rst",
    "api/modules.rst",
    "api/morphkit.rst",
    "api/morphkit.analyze_morph_tag.rst",
    "api/morphkit.analyze_pos.rst",
    "api/morphkit.analyze_word_with_morpheus.rst",
    "api/morphkit.annotate_and_sort_analyses.rst",
    "api/morphkit.compare_tags.rst",
    "api/morphkit.decode_tag.rst",
    "api/morphkit.get_word_blocks.rst",
    "api/morphkit.init_compare_tags.rst",
    "api/morphkit.parse_word_block.rst",
    "api/autogen/morphkit.analyze_morph_tag.rst",
    "api/autogen/morphkit.analyze_pos.rst",
    "api/autogen/morphkit.analyze_word_with_morpheus.rst",
]
autosummary_generate = True
napoleon_use_param = True

autodoc_default_options = {
    "member-order": "bysource",
    "undoc-members": True,
}

html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "collapse_navigation": False,
    "navigation_depth": 4,
    "sticky_navigation": True,
    "includehidden": True,
    "titles_only": False,
}
html_logo = "../images/morphkit.png"
html_static_path = ["_static"]
html_css_files = ["version-selector.css"]
html_js_files = ["version-selector.js"]

doc_version_label = os.environ.get("MORPHKIT_DOCS_LABEL", f"v{release}")
docs_versions = json.loads(os.environ.get("MORPHKIT_DOCS_VERSIONS", "[]"))
html_context = {
    "docs_versions": docs_versions,
    "docs_current_label": doc_version_label,
}
rst_epilog = f"""
.. |release_version| replace:: {release}
.. |docs_label| replace:: {doc_version_label}
"""

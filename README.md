[![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)  [![Docs](https://img.shields.io/badge/docs-%F0%9F%93%96-success.svg)](https://tonyjurg.github.io/morphkit/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/tonyjurg/morphkit/blob/main/LICENSE.md) [![DOI](images/zenodo.15920833.svg)](https://doi.org/10.5281/zenodo.15920833) [![SWH](https://archive.softwareheritage.org/badge/origin/https://github.com/tonyjurg/morphkit/)](https://archive.softwareheritage.org/browse/origin/?origin_url=https://github.com/tonyjurg/morphkit)

<img src="docs/images/morphkit.png" width=250 height=250>

Morphkit is a Python toolkit for Greek morphological analysis and tag similarity comparison. It uses the [`betacode`](https://github.com/perseids-tools/beta-code-py) library, the API of Morpheus (e.g., running in a [Docker virtualisation environment](https://hub.docker.com/r/perseidsproject/morpheus-api)) and a porting of the [Sandborg-Petersen morphological decoder](https://github.com/tonyjurg/Sandborg-Petersen-decoder).

In `v1.0.0`, Morphkit should be understood first as a research tool. It acts as a semantic translation layer between two incompatible morphological systems: Morpheus output on the one hand, and the SP / `N1904-TF` conventions used in the Nestle1904 Text-Fabric workflow on the other. The initial release is therefore tightly bound to that project environment and should not be read as a claim that Morphkit is a general-purpose standalone morphology package.

## Documentation

The documentation site is versioned. The stable release docs live at [tonyjurg.github.io/morphkit/stable](https://tonyjurg.github.io/morphkit/stable/), and the site includes a version selector for switching between `stable`, `dev`, and tagged releases.

## Package

For the actual code see [/morphkit](https://github.com/tonyjurg/morphkit/tree/main/morphkit).

## Installation

The `1.0.0` release is packaged as-is for internal and research use. The `pip` installation exists primarily so collaborators can recreate the exact software snapshot used in notebooks, scripts, and data processing runs.

Install the reproducible release snapshot with:

```bash
pip install morphkit==1.0.0
```

This pinned installation is the recommended route when you need reproducibility inside the `N1904-TF` research environment. It does not make the project independent from Morpheus, nor does it remove the project-specific assumptions baked into the translation logic.

For local development from this repository:

```bash
pip install -e .
```

Use the editable install when you are actively modifying the code for the same research workflow or adapting it for closely related internal experiments.

## Configuration

Morphkit supports configurable HTTP timeouts and retry behavior for Morpheus API requests.

**Default timeout:** 30 seconds

**Per-request timeout:**
```Python
response = morphkit.get_word_blocks("tou=", "localhost:1315", timeout=10)
```

**Global configuration:**
```Python
from morphkit.config import config

config.timeout = 45
config.retry_attempts = 3
config.retry_delay = 2.0
```

**Environment variables:**
```bash
export MORPHKIT_TIMEOUT=60
export MORPHKIT_RETRY_ATTEMPTS=2
export MORPHKIT_RETRY_DELAY=1.5
```

## Tools used

The standard set of tools ([Python documentation](https://www.python.org/doc/), tech sites like [stackoverflow](https://stackoverflow.com/), and Python syntax checkers like [Pythonium](https://pythonium.net/linter)) were used to create this package. Furthermore, for the creation of a subset of features, also the [Anaconda Assistant](https://www.anaconda.com/capability/anaconda-assistant) (using [OpenAI](https://openai.com/) as backend) and [GitHub Copilot](https://github.com/features/copilot) in Visual Studio were used to debug and/or optimize parts of the code. Where specified, [OpenAI Codex](https://chatgpt.com/codex) was used to create PRs.

## License

Morphkit uses a split licensing model:

- Source code in `morphkit/` is released under the [MIT License](https://github.com/tonyjurg/morphkit/blob/main/LICENSE.md).
- Documentation, notebooks, and other non-code repository content remain under [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://github.com/tonyjurg/morphkit/blob/main/LICENSE-docs.md), unless stated otherwise in a specific file.

This keeps the software package under a standard OSI-approved software license while preserving CC BY attribution terms for research-oriented non-code materials.


[![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)  [![Docs](https://img.shields.io/badge/docs-%F0%9F%93%96-success.svg)](https://tonyjurg.github.io/morphkit/) [![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/) [![DOI](images/zenodo.15920833.svg)](https://doi.org/10.5281/zenodo.15920833) [![SWH](https://archive.softwareheritage.org/badge/origin/https://github.com/tonyjurg/morphkit/)](https://archive.softwareheritage.org/browse/origin/?origin_url=https://github.com/tonyjurg/morphkit)

<img src="docs/images/morphkit.png" width=250 height=250>

Morphkit is a Python toolkit for Greek morphological analysis and tag similarity comparison. It uses the [`betacode`](https://github.com/perseids-tools/beta-code-py) library, the API of Morpheus (e.g., running in a [Docker virtualisation environment](https://hub.docker.com/r/perseidsproject/morpheus-api)) and a porting of the [Sandborg-Petersen morphological decoder](https://github.com/tonyjurg/Sandborg-Petersen-decoder).

## Documentation

The documentation site is versioned. The stable release docs live at [tonyjurg.github.io/morphkit/stable](https://tonyjurg.github.io/morphkit/stable/), and the site includes a version selector for switching between `stable`, `dev`, and tagged releases.

## Package

For the actual code see [/morphkit](https://github.com/tonyjurg/morphkit/tree/main/morphkit).

## Installation

The current software baseline is frozen as release `1.0.0`, and Morphkit can now be built as a standard Python package.

Install the baseline release with:

```bash
pip install morphkit==1.0.0
```

For local development from this repository:

```bash
pip install -e .
```

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

The morphkit package is released under the [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://github.com/tonyjurg/morphkit/blob/main/LICENSE.md).

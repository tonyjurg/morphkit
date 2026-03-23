# morphkit/__init__.py
# SPDX-License-Identifier: CC-BY-4.0
# Copyright (c) 2026 Tony Jurg
"""Public package interface for Morphkit."""

from ._version import __version__

# 1) Import each function into this namespace
from .analyse_pos                 import analyse_pos
from .analyse_morph_tag           import analyse_morph_tag
from .annotate_and_sort_analyses  import annotate_and_sort_analyses
from .decode_tag                  import decode_tag
from .parse_word_block            import parse_word_block
from .analyse_word_with_morpheus  import analyse_word_with_morpheus
from .get_word_blocks             import (
    get_word_blocks,
    MorpheusAPIError,
    MorpheusTimeoutError,
    MorpheusConnectionError,
)
from .split_into_raw_blocks       import split_into_raw_blocks
from .config                      import config

# 2) Initialize compare_tags right now
from .init_compare_tags import init_compare_tags
compare_tags = init_compare_tags()


# 3) Define __all__ so that `from library import *` also picks them up
__all__ = [
    "compare_tags",
    "analyse_pos",
    "analyse_morph_tag",
    "annotate_and_sort_analyses",
    "decode_tag",
    "parse_word_block",
    "analyse_word_with_morpheus",
    "get_word_blocks",
    "split_into_raw_blocks",
    "config",
    "MorpheusAPIError",
    "MorpheusTimeoutError",
    "MorpheusConnectionError",
]

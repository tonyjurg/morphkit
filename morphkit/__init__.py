# morphkit/__init__.py
# SPDX-License-Identifier: CC-BY-4.0
# Copyright (c) 2025 Tony Jurg
__version__ = "0.0.1"

morphkit_doc = """
This __init__.py file serves as the entry point for the 'morphkit' package, defining its public API and initialization logic.

This library package for morphological analysis consist of:
  - compare_tags
  - analyse_pos
  - analyse_morph_tag
  - decode_tag
  - parse_word_block
  - analyse_word_with_morpheus
  - get_word_blocks
  - split_into_raw_blocks

All of these names will be usable as:

    .. code-block:: python

        import morphkit
        morphkit.compare_tags(...)
        morphkit.analyse_pos(...)
        # etc.
    
"""
__doc__ = morphkit_doc

__all__ = [
    "compare_tags",
    "analyse_pos",
    "analyse_morph_tag",
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


#import importlib

# 1) Import each function into this namespace
from .analyse_pos                 import analyse_pos
from .analyse_morph_tag           import analyse_morph_tag
from .decode_tag                  import decode_tag
from .parse_word_block            import parse_word_block
from .analyse_word_with_morpheus  import analyse_word_with_morpheus
from .get_word_blocks             import (
    get_word_blocks,
    MorpheusAPIError,
    MorpheusTimeoutError,
    MorpheusConnectionError,
)
from .annotate_and_sort_analyses  import annotate_and_sort_analyses
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

# This is in here for now. It should be removed once this becomes a real package
print('morphkit loaded')

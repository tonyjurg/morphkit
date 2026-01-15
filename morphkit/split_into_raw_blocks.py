# morphkit/decode_tag.py
# SPDX-License-Identifier: CC-BY-4.0
# Copyright (c) 2026 Tony Jurg
__version__ = "1.0.1"

# import required packages
import re
from typing import Callable, Dict, Any, List, Tuple

def split_into_raw_blocks(text: str, debug: bool = False) -> List[List[str]]:
    """
    Split the input text into blocks at each ':raw' header using multiline regex.

    Args:
    -----

        :text (str):    The input text to be split.

        :debug (bool):  Optional argument. Defaults to `False`. If set to `True` the function print some debug information. 

    Returns:
    --------

        :List[List[str]]: A list of raw blocks, where each block is a list of lines.

    Example:
    --------

        .. code-block:: python
        
            raw_text=morphkit.get_word_blocks("tou",api_endpoint)
            blocks=morphkit.split_into_raw_blocks(raw_text)
            for block in blocks:
                # Process each individual block

    """

    if debug:
         print ('[split_into_raw_blocks] function called')

    # Split the input text into chunks at each ':raw' header
    raw_chunks = re.split(r'(?m)(?=^:raw)', text)[1:]  # [1:] to exclude the empty string at the beginning

    # Split each chunk into lines and keep the ':raw' line
    blocks = [chunk.splitlines() for chunk in raw_chunks]

    # Print debug information if requested
    if debug:
        print(f"Received {len(blocks)} raw blocks")

    return blocks
# morphkit/analyse_word_with_morpheus.py
# SPDX-License-Identifier: CC-BY-4.0
# Copyright (c) 2026 Tony Jurg
__version__ = "1.0.1"

# Import required packages
from typing import Callable, Dict, Any, List, Optional, Tuple
import re
import urllib.parse
import beta_code
import requests
import textwrap

# Bring in other sibling modules
from .decode_tag            import decode_tag
from .get_word_blocks       import get_word_blocks
from .parse_word_block      import parse_word_block
from .analyse_pos           import analyse_pos
from .analyse_morph_tag     import analyse_morph_tag
from .split_into_raw_blocks import split_into_raw_blocks

def analyse_word_with_morpheus(
    word_beta:    str,
    api_endpoint: str,
    language:     str='greek',
    add_pos:      bool = True,
    add_morph:    bool = True,
    debug:        bool = False,
    timeout:      Optional[float] = None,
    retry_attempts: Optional[int] = None,
    retry_delay:  Optional[float] = None,
) -> Dict[str, Any]:

    """
    Query the Morpheus morphological analyser for a Greek word in Betacode and parse its analyses.

    Args:
    -----

        :word_beta (str):     The input word in beta-code format to look up.
                              Backslashes in the input need to be escaped: e.g., 'a)nh/r\' -> 'a)nh/r\\'.

        :api_endpoint (str):  IP adress & port of the  Morpheus API endpoint (e.g., 192.168.0.5:1315).

        :language (str):      Optional argument. Defaults to `greek`. The other option is 'latin'. 
                              If set to 'latin' no POS and morph field will be added.

        :add_pos (bool):      Optional argument. Defaults to `True`. If set to `False` no POS field will be added to the parse.

        :add_morph (bool):    Optional argument. Defaults to `True`. If set to `False` no morph field will be added to the parse.

        :debug (bool):        Optional argument. Defaults to `False`. If set to `True` the function print some debug information.
        :timeout (float|None): Optional argument. Defaults to config.timeout. Timeout in seconds for the request.
        :retry_attempts (int): Optional argument. Defaults to config.retry_attempts. Number of retries on timeout/connection errors.
        :retry_delay (float): Optional argument. Defaults to config.retry_delay. Delay between retries in seconds.

    Returns:
    --------
    
        :Dict[str, Any]:   A dictionary with the following structure:

            .. code-block:: python

                {
                    'word': str,            # Normalized Betacode key returned by Morpheus
                    'raw_uni': str,         # Unicode Greek of raw format (not returned when 'language=latin')
                    'blocks': int,          # Number of blocks parsed
                    'analyses': List[dict], # Parsed analyses from each block
                }
  
    Steps:
    ------

      1. Fetch raw Morpheus output using function :py:func:`~morphkit.get_word_blocks`.
      2. Split the response into analysis blocks at each ':raw' marker using function :py:func:`~morphkit.split_into_raw_blocks`.
      3. For each block, call :py:func:`~morphkit.parse_word_block` to create a parse dictionairy.
      4. Add Part of Speech tag to the parse dictionairy by calling :py:func:`~morphkit.analyse_pos`.
      5. Add the SP morph-tag to the parse dictionairy by calling :py:func:`~morphkit.analyse_morph_tag`.
      6. Return a structured result.

    Raises:
    -------

    :ValueError: If the language parameter is invalid (only 'greek' and 'latin' are allowed).

    :ValueError: If the api_endpoint parameter is malformed (format should be 'host(IP or name):port').

    Example:
    --------

        .. code-block:: python

            api_endpoint="192.168.0.5:1315" 
            result=morphkit.analyse_word_with_morpheus('au(/th',api_endpoint)
   
     
    Flow diagram:
    -------------

    .. code-block:: none

        +------------------------------+
        | analyse_word_with_morpheus() |
        +--------------+---------------+
                       |
                       v
        +-----------------------+   HTTP request  +--------------------+
        |  1. get word blocks   +<--------------->+  Morpheus endpoint |
        +--------------+--------+  HTTP response  +--------------------+
                       |
                       v
        +--------------+----------------+
        | 2. Split into blocks          |
        +-------------------------------+
                       |
                       v
        +--------------+----------------+
        | 3. for each block:            |
        |     +----------------------+  |
        |     | analyse_pos          |  |
        |     | analyse_morph        |  |
        |     +----------------------+  |
        +--------------+----------------+
                       |
                       v
        +--------------+----------------+
        | 4. Return combined analyses   |
        +-------------------------------+
    
    """

    # A very basic check that `endpoint` contains a ':' and that the part after it is all digits.
    if ":" not in api_endpoint:
        message=f"[analyse_word_with_morpheus] Invalid api_endpoint '{api_endpoint}'. Missing ':' separator. Format should be 'host(IP or name):port'"
        if debug:
            raise ValueError(message)
        else:
            print(message)

    host, port_str = api_endpoint.split(":", 1)
    if not port_str.isdigit():
        message=f"[analyse_word_with_morpheus] Invalid api_endpoint '{api_endpoint}': port '{port_str}' is not numeric."
        "Format should be 'host(IP or name):port'"
        if debug:
            raise ValueError(message)
        else:
            print(message)

    # Tailor to the language
    if language not in ('greek','latin'):
        message=f"[analyse_word_with_morpheus] Unknown language format {language!r}. "
        "Choose from {'greek', 'latin'}."
        if debug:
            raise ValueError(message)
        else:
            print(message)

    if language == 'latin':
        add_pos=False
        add_morph=False
        uc_itm=False
    else:
        uc_itm=True
    
    # 1. Fetch raw Morpheus output
    if debug:
        print(
            "[analyse_word_with_morpheus] Calling function get_word_blocks("
            f"{word_beta=},{api_endpoint=},{language=},{debug=},"
            f"{timeout=},{retry_attempts=},{retry_delay=})"
        )
    text=get_word_blocks(
        word_beta,
        api_endpoint,
        language=language,
        debug=debug,
        timeout=timeout,
        retry_attempts=retry_attempts,
        retry_delay=retry_delay,
    )

    # 2. Split into blocks at each ':raw' header 
    blocks = split_into_raw_blocks(text,debug=debug)

    # 3. Parse each block and perform analyses
    analyses : List[Dict[str, Any]] = []
    raw_beta = None

    # initialize idx so it always exists (which may be the case when no analysis results are found)
    idx = 0
    for block_idx, block in enumerate(blocks, start=1):

        idx=block_idx
        if debug:
            print(f"[analyse_word_with_morpheus] Calling function parse_word_block(block,{language=},{debug=}) for block #{idx}")
        raw_beta, parses = parse_word_block(block, language=language, debug=debug)

        # Perform part-of-speech and morphological tag analysis on each parse
        for p in parses:
            if add_pos:
                if debug:
                    print(f"[analyse_word_with_morpheus] Calling analyse_pos on parse: {p.get('raw_beta')}")
                p['pos'] = analyse_pos(p, debug=debug)

            if add_morph:
                if debug:
                    print(f"[analyse_word_with_morpheus] Calling analyse_morph_tag on parse")
                p['morph'] = analyse_morph_tag(p, debug=debug)

        # Accumulate all parses
        analyses.extend(parses)
        if debug:
            print(f"[analyse_word_with_morpheus] Parsed block {idx} for betacode {word_beta}")

    # 4. Return the aggregated result (only include 'raw_uc' when relevant, i.e., when 'language'='greek')
    return {
        "raw_bc": raw_beta or "",
        **({"raw_uc": beta_code.beta_code_to_greek(raw_beta or "")} if uc_itm else {}),
        "blocks":   idx,
        "analyses": analyses
    }

    # End of function analyse_word_with_morpheus()

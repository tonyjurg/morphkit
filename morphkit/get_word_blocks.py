# morphkit/get_word_blocks.py
# SPDX-License-Identifier: CC-BY-4.0
# Copyright (c) 2025 Tony Jurg
__version__ = "0.0.1"

# import required packages
from typing import Callable, Dict, Any, List, Tuple
import beta_code
import urllib.parse
import requests
import time

def get_word_blocks(
    word_beta         : str, 
    api_endpoint      : str,                     # IP adress & port of Morpheus API endpoint
    language          : str = "greek",           # Language: 'greek' (default) or 'latin' 
    output            : str = "full",            # Output format: "full" (default) or "compact"
    debug             : bool = False
)-> str:

    """Retrieve the raw word blocks data for a given beta-code word from a Morpheus endpoint.

    Args:
    -----

        :word_beta (str):        The input word in beta-code format to look up. 
                                 Backslashes in the input string need to be escaped: e.g., 'a)nh/r\' -> 'a)nh/r\\'

        :api_endpoint (str):  IP adress & port of the  Morpheus API endpoint (e.g., '192.168.0.5:1315').
         
        :language (str):    Optional argument. Defaults to `greek`. Sets the language of the word to analyse. It can be set to `greek` or `latin`.
        
        :output {str}:      Optional argument. Defaults to `full`. Output format of the Analytic block. Either `full` for the internal database format, or `compact` for a brief output.

        :debug (bool):      Optional argument. Defaults to `False`. If set to `True`, prints the constructed URL and response size. 

    Returns:
    --------

        :str: The plain text response containing the word blocks for the requested beta-code form.

    Raises:
    -------

        :ValueError: The language parameter is invalid (only 'greek' and 'latin' are allowed).

        :ValueError: The api_endpoint parameter is malformed (format should be 'host(IP or name):port').

        :requests.HTTPError: HTTP request failed (non-2xx status code).

    Example:
    --------

         .. code-block:: python

            api_endpoint = "10.10.0.10:1315" 
            blocs=morphkit.get_word_blocks('sune/rxomai', api_endpoint)


    """

    # A very basic check that `endpoint` contains a ':' and that the part after it is all digits.
    if ":" not in api_endpoint:
        raise ValueError(
        f"[get_word_blocks] Invalid api_endpoint '{api_endpoint}'. Missing ':' separator."
        "Format should be 'host(IP or name):port'")
    host, port_str = api_endpoint.split(":", 1)
    if not port_str.isdigit():
        raise ValueError(
        f"[get_word_blocks] Invalid api_endpoint '{api_endpoint}': port '{port_str}' is not numeric."
        "Format should be 'host(IP or name):port'")

    # Define the mapping from value of argumet 'language' to actual API path
    lang_args_list = {
        'greek'      : '/greek',
        'latin'      : '/latin',
    }

    if language in lang_args_list:
        api_path=lang_args_list[language]
    else:
        raise ValueError(
        f"[get_word_blocks] Unknown language format {language!r}. "
        "Choose from {'greek', 'latin'}."
        )

    # Start timer
    start = time.perf_counter()

    # Define the mapping from value of argumet 'output' to actual API arguments
    api_args_list = {
        'compact'   : '?opts=n',
        'full'      : '?opts=d?opts=n',
    }

    if output in api_args_list:
        api_args=api_args_list[output]
    else:
        raise ValueError(
        f"[get_word_blocks] Unknown output format {output!r}. "
        "Choose from {'full', 'compact'}."
)
        print(f"Unknown output format: {output}")
        exit()

    # 1. Encode the Betacode word for safe URL inclusion
    encoded = urllib.parse.quote(word_beta, safe='')
    url= f"http://{api_endpoint}{api_path}/{encoded}{api_args}"
    if debug==True:
        print(f"[get_word_blocks] Sending GET request: {url}")

    # 2. Perform the HTTP GET request
    resp = requests.get(url)
    elapsed = time.perf_counter() - start

    if debug==True:
        # Status and timing
        print(f"[get_word_blocks] Received status code: {resp.status_code}")
        print(f"[get_word_blocks] Response time: {elapsed:.3f}s")
        # Request headers
        print(f"[get_word_blocks] Request headers: {resp.request.headers}")
        # Response headers
        print(f"[get_word_blocks] Response headers: {resp.headers}")

    # 3. Check for HTTP errors
    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"[get_word_blocks] HTTP error: {e} (status code: {resp.status_code})")

    text = resp.text

    if debug==True:
        # Show the first 100 characters (or whole thing if smaller)
        snippet = text[:100] + ("..." if len(text) > 100 else "")
        print(f"[get_word_blocks] Response snippet (max 100 bytes):\n{snippet}")

    return text
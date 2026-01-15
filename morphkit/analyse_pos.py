# morphkit/analyse_pos.py
# SPDX-License-Identifier: CC-BY-4.0
# Copyright (c) 2026 Tony Jurg
__version__ = "1.0.1"

# import required packages
from typing import Callable, Dict, Any, List, Tuple
import re
import beta_code
import pprint
import textwrap

"""
The grammar used for this analysis is taken from these books:
 - Daniel B. Wallace. The Basics of New Testament Syntax (Grand Rapids, MI: Zondervan, 2009),
   shortened in this file to BNT.
 - Daniel B. Wallace. Greek Grammar beyon the Basics (Grand Rapids, MI: Zondervan, 2009),
   shortened in this file to GGBB.
""" 

                                                                              
def analyse_pos(parse: Dict[str, Any] ,debug: bool=False) -> str:
    """ analyse a single Morpheus parse record and determine its part of speech.
    
    Args:
    -----

        :parse (dict): A parse dictionary with the following structure:

            .. code-block:: python

                {
                    'raw_uc': '...', 
                    'stam_codes': [...],
                    ...
                    'morph_flags': [...], 
                    'tense': 'present',
                    ...
               }

        :debug (bool): Optional argument. Defaults to `False`. If set to `True` the function print some debug information.
    
    Returns:
    --------

        :str: The determined `Part of Speech` label (e.g. `'noun'`, `'verb'`, `'adverb'`, ...),
             or `'unknown'` if no rule applies.

    Steps:
    ------

         The analysis consist of the following major steps:
 
            1. Verbs (presence of 'tense' or 'mood' keys).

                **Note:** one could argue for two dedicated POS classes, for participle and infinitive, 
                c.f Wallace GGBB p.613 & p.588. This was NOT done in order to stay in line with the
                current N1904-TF classification used by feature `sp`. The differentation between 
                participle, infinitive and 'other' verb types is done in module 'init_compare_tags'.

            2. Specific morph codes and flags → mapped POS (e.g. 'conj' → conjunction).

            3. Indeclinable forms ('indeclform' flag):

                - Neuter-singular nom/acc → adverb.

                - Numeral indecl → numeral.

                - Proper noun indecl if gender/number present → proper noun.

                - Otherwise → other indeclinable noun.

            4. Proclitic or enclitic forms → particle.

            5. Anything with case or gender → noun.

            7. If other_end_token == adverbial → adverb.

            8. Fallback → unknown.
    
    Example:
    --------

        .. code-block:: python

            parse = {'raw_uc':'λέγω','tense':'present','mood':'indicative', ...}
            morphkit.analyse_pos(parse)
            'verb'

    """

    # If debug is set, print this function name (the return value will be printed later)
    if debug: print (f'[analyse_pos] betacode {parse.get("raw_bc")}:  ',end='')

    # 1. Verbs: presence of any tense/mood is a very good indication to directly annotate as verb
    if "tense" in parse or "mood" in parse:
        # see docblock regarding the participium and the infinitive (GGBB, p.588&613)
        if debug: print('tense or mood 🠢 verb ~ V-')
        return "verb"

    # 2. Specific codes and flags mappings (combined in ordered_items)
    #
    # Merge morphological codes and flags into a single sequence for downstream analysis.
    # Order is significant: codes define broad categories first, and flags provide
    # finer annotations (e.g., “indeclform”) when the codes alone aren’t conclusive.
    # Conclusive codes and flags are in the code_map below with its proper pos.
    # We allow duplicates, since it has no logical impact while deduplicating 
    # delivers minimal benefit relative to its cost and additional complexity.
    ordered_items = parse.get("end_codes", []) + parse.get("stem_codes", []) + parse.get("end_flags", []) + parse.get("stem_flags", [])
    if debug: print(f'word={parse.get("work_bc")} {ordered_items=}\n[analyse_pos] ',end='') # we are not yet done

    code_map: Dict[str, str] = {
        "conj"        : "conjunction",
        "aor1"        : "verb",
        "aor2"        : "verb",
        "aor2_pass"   : "verb",
        "irreg_adj3"  : "adjective",
        "verb_adj2"   : "adjective",
        "demonstr"    : "demonstrative pronoun",
        "prep"        : "preposition",
        "particle"    : "particle",
        "numeral"     : "numeral",
        "relative"    : "relative pronoun",
        "pron1"       : "personal pronoun",
        "pron2"       : "personal pronoun",
        "pron3"       : "personal pronoun",
        "indef"       : "indefinite pronoun",
        "interrog"    : "interrogative pronoun",
        "article"     : "article",
        "adverb"      : "adverb",        # adverbs that aren’t neut-sg indecl
        "adverbial"   : "adverb", 
        "irreg_mi"    : "verb",
        "art_adj"     : "personal pronoun",
        "pron_adj1"   : "demonstrative pronoun",
        "wn_on_comp"  : "adjective",
        "exclam"      : "interjection" 
    }
    
    for mcode in ordered_items:
        if mcode in code_map:
            if debug: print(f'ordered_items 🠢 {code_map[mcode]}')
            return code_map[mcode]

    # 3. Indeclinable forms
    if "indeclform" in ordered_items:

        # 3a. Neuter-singular nom/acc indeclinable → adverb
        if (parse.get("gender") == "neut"
            and parse.get("number") == "sg"
            and parse.get("case") in ("nom", "acc")):
            if debug: print("indeclform+neut/sg/nom-acc → adverb ~ ADV")
            return "adverb"
        
        # 3b. Numeral indeclinable ? {This needs to be checked further!}
        if "numeral" in ordered_items:
            if debug: print("indeclform+numeral → numeral indeclinable ~ A-NUI")
            return "numeral indeclinable"

        # 3c. Proper noun indeclinable if still has gender or number
        #    we assume presence of gender/number on an indeclinable means a name ([TBC] - is this actualy the case?)
        if "gender" in parse or "number" in parse:
            if debug: print("indeclform+gender/number → proper noun indeclinable ~ N-PRI")
            return "proper noun indeclinable"

        # 3d. All other indeclinables → other noun indeclinable
        if debug: print("indeclform → other noun indeclinable ~ N-OI")
        return "noun other indeclinable" 
    
    # 4. Proclitic/enclitic → particle
    if "enclitic" in ordered_items or "proclitic" in ordered_items:
        if debug: print('enclitic or proclitic 🠢 particle ~ PART')
        return "particle"

    # 5. Anything with a case or gender → noun
    if "case" in parse or "gender" in parse:
        if debug: print('case or gender 🠢 noun ~ N-')
        return "noun"

    # 6. Tag adverbials (in other_end_tokens) just in case missed somewhere
    if "adverbial" in parse.get("other_end_tokens", []):
        if debug: print(f'Other_end_token 🠢 adverb')
        return "adverb"

    # 7. Fallback → unknown
    if True: # debug: 
        print(f'fallback 🠢 unknown')
        # Pretty-print the parse dict for readability
        pp.pprint(parse)
    return "unknown"

    # End of function analyse_pos()

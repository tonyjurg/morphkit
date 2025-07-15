# morphkit/analyse_morph_tag
# SPDX-License-Identifier: CC-BY-4.0
# Copyright (c) 2025 Tony Jurg
__version__ = "0.0.1"


# import required packages
from typing import Callable, Dict, Any, List, Tuple
import re
import textwrap

# Enable nicely formatted dumps of Python dicts
from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2, width=80, compact=False)


# Helper: get uppercase code for morphological features
def code(val, default=''):
    """
    Turn a scalar or list of strings into the concatenated
    uppercase initials (or default if missing).
    """
    if not val:
        return default
    if isinstance(val, (list, tuple)):
        # e.g. ['masc','fem'] -> 'MF'
        return ''.join(str(v)[0].upper() for v in val if v)
    # scalar case: 'nom' -> 'N'
    return str(val)[0].upper()

def append_dialect_suffix(tag: str, parse: Dict[str, Any]) -> str:
    """
    Append a dialect suffix to a morphological tag, if recognized dialects are present.

    Args:
    -----
        tag (str)   : The morphological tag to augment.

        parse (dict): The analysis dictionary, potentially containing 'dialects'.

    Returns:
    --------

        str: The tag with an optional mapped dialect suffix appended.
    """

    dialects = parse.get('dialects')
    if not dialects:
        return tag

    # Only explicitly recognized dialects are allowed
    # since the data is often a combined list like `attic/epic/doric/ionic`, it may be better to limit the number of 'recognized'
    # dialects to only Attic and Aeolic in order to have a closer match to the tags used in N1904-TF dataset
    DIALECT_MAP = {
        'attic':      'ATT',  # explicit in https://github.com/biblicalhumanities/Nestle1904/blob/master/morph/parsing.txt
        #'ionic':      'ION',  # added
        #'doric':      'DOR',  # added
        'aeolic':     'A',    # explicit
        #'epic':       'EPC',  # added
        #'homeric':    'HOM',  # added
    }

    # Normalize input and filter only those present in DIALECT_MAP
    mapped = [
        DIALECT_MAP[d.lower()]
        for d in dialects
        if d and d.lower() in DIALECT_MAP
    ]

    if not mapped:
        return tag  # no recognized dialects

    suffix = '-' + '-'.join(sorted(set(mapped)))
    return tag + suffix



def analyse_morph_tag(parse: Dict[str, Any] ,debug: bool=False) -> str:
    """ 
    Compute the Sandborg–Petersen morphological tag for a single Morpheus analyses block.

    Args:
    -----

        :parse (dict): Morphological parse with keys like 'pos', 'tense',
                            'voice', 'mood', 'case', 'number', 'gender', etc.

        :debug (bool): Optional argument. Defaults to `False`. If set to `True` the function print some debug information.

    Returns:
    --------

        :str: The SP morphological tag or 'UNK' if unrecognized.

    Steps:
    ------
    
      1.  Determine the POS prefix (e.g. 'N-', 'V-', 'A-', 'ADV', etc.).

      2.  Return immediately for indeclinable POS (adverbs, particles, etc.).

      3.  For verbs, build the tag as 'V-<Tense><Voice><Mood>' plus a suffix
          for person & number (finite), infinitive (no suffix), or participle
          (case–number–gender).

      4.  For nouns, adjectives, and articles, append uppercase initials of
          case, number, and gender; adjectives may get '-C'/'-S' for degree.

      5.  For pronouns, combine person, case, number, and gender.

      6.  If nothing matches, return 'UNK'.

    Example:
    --------

        .. code-block:: python

            api_endpoint = "10.10.0.10:1315" 
            blocs=morphkit.get_word_blocks('sune/rxomai',api_endpoint)
            for block in blocks: 
                parse=morphkit.parse_word_block(block)
                analysis=morphkit.analyse_morph_tag(parse)

            # dictionairy has now entry 'morph' added:
            {'analyses': [{'end_bc': 'omai',
                           'end_codes': ['w_stem'],
                           ...
                           'mood': 'indicative',
                           'morph': 'V-PEI-1S',
                           'number': 'singular',
                           ...

    General notes:
    --------------
    
        The documentation for the SP morphology is available via:
        https://github.com/biblicalhumanities/Nestle1904/blob/master/morph/parsing.txt

    """

    # First check if the input is indeed a valid dictionairy
    if not isinstance(parse, (dict)):
        if debug: 
            print (f'[analyse_morph_tag] Input should be a dictionairy 🠢  ERROR\nInput:')
            # pretty-print `parse`
            pp.pprint(parse)
        return 'ERROR'
    
    # If debug is True, print this function name (the return value will be printed later)
    if debug: print (f'[analyse_morph_tag] Called with betacode {parse.get("raw_bc")}: ',end='')
    
    # 1. Map part-of-speech to SP prefix
    _raw = parse.get('pos')
    if isinstance(_raw, str):
        pos = _raw.strip().lower()
    else:
        # This should not happen!  Exit with returning 'ERROR' 
        if debug: 
            print (f' Empty input string for POS 🠢 ERROR')
            # pretty-print `parse`
            pp.pprint(parse)
        return 'ERROR'
        
    prefix_map = {
        'noun':                                 'N-', 
        'adjective':                            'A-', 
        'article':                              'T-', 
        'definite article':                     'T-', 
        'indefinite article':                   'T-', 
        'verb':                                 'V-', 
        'personal pronoun':                     'P-', 
        'relative pronoun':                     'R-', 
        'reciprocal pronoun':                   'C-',
        'demonstrative pronoun':                'D-', 
        'correlative pronoun':                  'K-', 
        'interrogative pronoun':                'I-',
        'indefinite pronoun':                   'X-', 
        'correlative or interrogative pronoun': 'Q-',
        'reflexive pronoun':                    'F-', 
        'possessive pronoun':                   'S-',
        'adverb':                               'ADV', 
        'conjunction':                          'CONJ', 
        'conditional':                          'COND', 
        'particle':                             'PRT',
        'preposition':                          'PREP', 
        'interjection':                         'INJ', 
        'aramaic':                              'ARAM', 
        'hebrew':                               'HEB',
        'proper noun indeclinable':             'N-PRI',
        'numeral indeclinable':                 'A-NUI',
        'exclam':                               'INJ', 
        'numeral':                              'A-NUI',
        'letter indeclinable':                  'N-LI', 
        'noun other indeclinable':              'N-OI', 
        'punctuation':                          'PUNCT'
    }
    prefix = prefix_map.get(pos, '')
    if debug and not prefix:
        print(f" [WARNING] no prefix for {parse.get('work_unicode')}, pos={parse.get('pos')!r} (normalized {pos!r})")

    # 2. Return directly for indeclinable POS types
    # {Note: this may be jumping out a litle bit too early...}
    indecl = {'ADV','CONJ','COND','PRT','PREP','INJ','ARAM','HEB','N-PRI','A-NUI','N-LI','N-OI','PUNCT'}
    if prefix in indecl:
        # Handle interrogative adverb: morph_code 'interrog' gives suffix '-I'
        if prefix == 'ADV' and 'interrog' in parse.get('morph_codes', []):
            if debug: print('ADV + interrog 🠢 ADV-I')
            return 'ADV-I'
        if debug: print(f'prefix in indecl 🠢 {prefix}')
        # return prefix together with dialect suffix if pressent
        return append_dialect_suffix(prefix, parse)


        

    # 3. Handle verbs: V-<T><V><M> + optional suffix
    if prefix == 'V-':
        # Maps for tense, voice, mood
        tense_map = {
            'pres':                    'P',
            'imperf':                  'I',
            'fut':                     'F',
            'second future':              '2F',
            'aor':                     'A',
            'second aorist':              '2A',
            'perf':                    'R',
            'second perfect':             '2R',
            'plup':                 'L',
            'second pluperfect':          '2L',
            'no tense stated':            'X'
        }
        
        # Flags that signal a “second” form for certain tenses
        second_flags = {
            'aor':     ['aor2', 'aor2_pass'],
            'fut':     ['fut2', 'future2'],
            'perf':    ['perf2'],
            'plup':    ['lpl2', 'plup2'],
        }
        
        # Voice lookup map
        voice_map = {
            'act':                     'A',
            'mid':                     'M',
            'pass':                    'P',
            'mp':             'E',
            'middle deponent':            'D',
            'passive deponent':           'O',            
            'middle or passive deponent': 'N',
            'impersonal active':          'Q',
            'no voice':                   'X'           
        }
        
        # Mood lookup map
        mood_map = {
            'ind':                 'I',
            'subj':                'S',
            'opt':                   'O',
            'imperat':                 'M',
            'inf':                 'N',
            'part':                 'P',
            'imperative participle':      'R'
        }

        # TENSE

        # Normalize morph codes and parsed tense
        morph_codes = [c.lower() for c in parse.get('morph_codes', [])]
        base_tense  = parse.get('tense', '').strip().lower()
        
        # Decide which key to use in tense_map
        if base_tense in second_flags and any(flag in morph_codes for flag in second_flags[base_tense]):
           lookup_key = f"second {base_tense}"
        else:
           lookup_key = base_tense or 'no tense stated'

        # Final code (defaulting to 'X' if nothing matches)
        T = tense_map.get(lookup_key, 'X')


        # VOICE/MOOD

        # Always set voice & mood codes
        V = voice_map.get(parse.get('voice'), 'X')
        M = mood_map.get(parse.get('mood'),  'X')
        if V=='X' or M=='X': print (parse)

        # Grab person (fallback to other_end_tokens if needed)
        if parse.get('person'):
            person = parse.get('person')[0]
        else:
            for tok in parse.get('other_end_tokens', []):
                m = re.match(r'^([123])', tok)
                if m:
                    person = m.group(1)
                    break
            person=None  # no alternative data found -> initialize None Person

        # Number code
        num_code = code(parse.get('number')) # code return the first letter of the property in capitals (safe for gender, number, case, degree)

        # Base tag
        base = f"V-{T}{V}{M}"

        # Finite verbs: append “-<person><number>”
        if M in {'I','S','O','M'} and person:
            suffix = f"-{person}{num_code}"
            if debug: print(f'finite verb 🠢 {base}{suffix}')
            # return base + tag together with dialect suffix if pressent
            return append_dialect_suffix(base + suffix, parse)
            
        # Infinitives: just use the base (e.g. V-2AMN for 2nd aorist middle/passive infinitive)
        elif M == 'N':
            if debug: print(f'infinitive verb 🠢 {base}')
            # return base together with dialect suffix if pressent
            return append_dialect_suffix(base, parse)
            
        # Participles: suffix is case+number+gender
        elif M == 'P':
            raw_cases = parse.get('case','')
            cases = raw_cases if isinstance(raw_cases, (list, tuple)) \
                  else ([raw_cases] if raw_cases else [])
            raw_nums = parse.get('number','')
            nums  = raw_nums if isinstance(raw_nums, (list, tuple)) \
                  else ([raw_nums]  if raw_nums  else [])
            raw_gens = parse.get('gender','')
            gens  = raw_gens if isinstance(raw_gens, (list, tuple)) \
                 else ([raw_gens]  if raw_gens  else [])
            tags = [f"{base}-{code(c)}{code(n)}{code(g)}"
                    for c in cases for n in nums for g in gens]
            compound_return= '/'.join(tags) if tags else base
            if debug: print(f'participle 🠢 {compound_return}')
            # return compound together with dialect suffix if pressent
            return append_dialect_suffix(compound_return, parse)

    # 5. Noun/Adjective/Article pattern: prefix case number gender
    if prefix in {'N-','A-','T-'}:
        # Normalize case(s), number, and gender(s) to lists
        cases = parse.get('case') or []
        cases = cases if isinstance(cases, (list, tuple)) else [cases]
        nums = parse.get('number')
        nums = [nums] if nums else ['']
        gens = parse.get('gender') or []
        gens = gens if isinstance(gens, (list, tuple)) else [gens]

        # Build one tag per case×number×gender combination
        tags = []
        for c in cases:
            for n in nums:
                for g in gens:
                    cas_code = code(c)
                    num_code = code(n)
                    gen_code = code(g)
                    base_tag = f"{prefix}{cas_code}{num_code}{gen_code}"

                    # Adjective degree extension
                    if prefix == 'A-':
                        if parse.get('degree') == 'comparative':
                            base_tag += '-C'
                        elif parse.get('degree') == 'superlative':
                            base_tag += '-S'

                    # add dialect suffix if pressent
                    full_tag = append_dialect_suffix(base_tag, parse)
                    tags.append(full_tag)

        # Join all generated tags
        compound_return='/'.join(tags)
        if debug: print(f'noun/adjective/article 🠢 {compound_return}')
        return compound_return

    # 6. Pronouns: P-/R-/C-/D-/K-/I-/X-/Q-/F-/S- + [person] case number [gender]
    pronoun_prefixes = {'P-','R-','C-','D-','K-','I-','X-','Q-','F-','S-'}
    if prefix in pronoun_prefixes:
        # grab person/number
        person_code = code(parse.get('person'))  # e.g. '1','2','3'
        num_code    = code(parse.get('number'))  # e.g. 'S','P','D'

        # normalize cases to a list (even if missing)
        raw_cases = parse.get('case')
        if isinstance(raw_cases, (list, tuple)):
            cases = raw_cases
        elif raw_cases:
            cases = [raw_cases]
        else:
            cases = [None]           # no case? still get one iteration

        # normalize genders to a list (even if missing)
        raw_gens = parse.get('gender')
        if isinstance(raw_gens, (list, tuple)):
            gens = raw_gens
        elif raw_gens:
            gens = [raw_gens]
        else:
            gens = [None]            # no gender? still get one iteration


        tags = []
        for c in cases:
            for g in gens:
                parts = [prefix]
                if person_code:
                    parts.append(person_code)
                if c:
                    parts.append(code(c))     # case (N,G,D,A,V)
                if num_code:
                    parts.append(num_code)   # number

                if g:
                    parts.append(code(g))    # gender (M,F,N) - optional

                # add dialect suffix if pressent
                base_tag = ''.join(parts)
                full_tag = append_dialect_suffix(base_tag, parse)
                tags.append(full_tag)

        # Join all generated tags
        compound_return='/'.join(tags)
        if debug:
            if not compound_return:
                print(f"Analysis of pronoun (with prefix {prefix}) is empty 🠢 {compound_return}")
                # pretty-print `parse`
                pp.pprint(parse)
            else: print(f' pronoun (with prefix {prefix}) 🠢 {compound_return}')
        return compound_return

    # 7. Fallback for unhandled cases
    if debug: 
        print (f'[analyse_morph_tag] Fallback encountered 🠢 UNK')
        # pretty-print `parse`
        pp.pprint(parse)
    return 'UNK'

    # End of function analyse_morph_tag()


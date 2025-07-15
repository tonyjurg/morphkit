# morphkit/decode_tag.py
# SPDX-License-Identifier: CC-BY-4.0
# Copyright (c) 2025 Tony Jurg
__version__ = "0.0.1"

# import required packages
import re
from typing import Callable, Dict, Any, List, Tuple

def decode_tag(tag_input:str, debug: bool=False) -> Dict[str, Any]:
    """Decode a morphological tag into a set of human-readable features.

    This function takes a morphological tag (e.g. "V-PAI-3S") and returns
    a dictionary of interpreted grammatical properties, such as `Part of Speech`,
    `case`, `number`, `gender`, `tense`, `voice`, `mood`, `person`, and any `suffix` details.

    Args:
    -----
    
        :tag_input (str): The raw morphological tag string. Usually includes prefixes
            like "N-", "V-", "A-", etc., followed by coded letters/numbers.

        :debug (bool): Optional argument. Defaults to `False`. If set to `True` the function print some debug information.

    Returns:
    --------
    
        :Dict[str, Any]: A mapping from feature names to their full descriptions.

            Possible keys include:
              - "Part of Speech"
              - "Case", "Number", "Gender"
              - "Tense", "Voice", "Mood"
              - "Verb Extra" or "Suffix"
              - "Warning", warning related to feature elements
              - "Error" (e.g., if input is empty)

        If the part of speech can not be determined, it returns `{"Part of Speech": "Unknown or Unsupported"}`.

        If `tag_input` is empty or whitespace, it returns `{"Error": "Please enter a parsing tag."}`.

    Example:
    --------
    
    .. code-block:: python
    
        morphkit.decode_tag("N-NSM")
        {
            "Part of Speech": "Noun",
            "Case": "Nominative",
            "Number": "Singular",
            "Gender": "Masculine",
            ...
        }

    Note:
    -----

        This function is an addapted version of the tool available at https://github.com/tonyjurg/Sandborg-Petersen-decoder.

    """
    
    # Main Part of Speech mapping
    posMap: Dict[str, str] = {
        "N-PRI": "Proper Noun Indeclinable",  # first the subset since decoding is based on 'first match'
        "N-LI":  "Letter Indeclinable",
        "N-OI":  "Noun Other Type Indeclinable",
        "N-":    "Noun",  # generic Noun
        "A-NUI": "Numeral Indeclinable", 
        "A-":    "Adjective",
        "T-":    "Article",
        "V-":    "Verb",
        "P-":    "Personal Pronoun",
        "R-":    "Relative Pronoun",
        "C-":    "Reciprocal Pronoun",
        "D-":    "Demonstrative Pronoun",
        "K-":    "Correlative Pronoun",
        "I-":    "Interrogative Pronoun",
        "X-":    "Indefinite Pronoun",
        "Q-":    "Correlative/Interrogative Pronoun",
        "F-":    "Reflexive Pronoun",
        "S-":    "Possessive Pronoun",
        "ADV":   "Adverb",
        "CONJ":  "Conjunction",
        "COND":  "Conditional",
        "PRT":   "Particle",
        "PREP":  "Preposition",
        "INJ":   "Interjection",
        "ARAM":  "Aramaic",
        "HEB":   "Hebrew",
        "PUNCT": "Punctuation"
    }

    # List with pronominal parts of speech (without poss. pron. S- and refl. pron. F-)
    pronList = {
                 # Pronouns referring to people or things
        "P-",    # personal pronoun
        "R-",    # relative pronoun
        "C-",    # reciprocal pronoun
        "D-",    # demonstrative pronoun
                 # Pronouns used in specific contexts
        "K-",    # correlative pronoun
        "I-",    # interrogative pronoun
        "X-",    # indefinite pronoun
        "Q-",    # correlative or interrogative pronoun
                 # Pronouns indicating reflexivity
    }

    # List with all indeclinable parts of speech
    indeclList= {
        "ADV",   # adverb
        "CONJ",  # conjunction
        "COND",  # cond
        "PRT",   # particle
        "PREP",  # preposition
        "INJ",   # interjection
        "ARAM",  # aramaic
        "HEB",   # hebrew
        "N-PRI", # proper noun indeclinable
        "A-NUI", # numeral indeclinable
        "N-LI",  # letter indeclinable
        "N-OI",  # noun other type indeclinable
    }
    
    # grammatical case mapping
    caseMap: Dict[str, str] = {
        "V": "Vocative",
        "N": "Nominative",
        "G": "Genitive",
        "D": "Dative",
        "A": "Accusative"
    }
    
    # grammatical number mapping
    numberMap: Dict[str, str] = {
        "S": "Singular",
        "P": "Plural",
        "D": "Dual"
    }
    
    # grammatical gender mapping
    genderMap: Dict[str, str] = {
        "M": "Masculine",
        "F": "Feminine",
        "N": "Neuter"
    }
    
    # verb tense mapping
    tenseMap: Dict[str, str] = {
        "P":  "Present",
        "I":  "Imperfect",
        "F":  "Future",
        "2F": "Second Future",
        "A":  "Aorist",
        "2A": "Second Aorist",
        "R":  "Perfect",
        "2R": "Second Perfect",
        "L":  "Pluperfect",
        "2L": "Second Pluperfect",
        "X":  "No Tense Stated"
    }
    
    # verb voice mapping
    voiceMap: Dict[str, str] = {
        "A": "Active",
        "M": "Middle",
        "P": "Passive",
        "E": "Middle or Passive",
        "D": "Middle Deponent",
        "O": "Passive Deponent",
        "N": "Middle or Passive Deponent",
        "Q": "Impersonal Active",
        "X": "No Voice"
    }
    
    # verb mode mapping
    moodMap: Dict[str, str] = {
        "I": "Indicative",
        "S": "Subjunctive",
        "O": "Optative",
        "M": "Imperative",
        "N": "Infinitive",
        "P": "Participle",
        "R": "Imperative Participle"
    }
    
    # grammatical person mapping
    personMap: Dict[str, str] = {
        "1": "First Person",
        "2": "Second Person",
        "3": "Third Person"
    }
    
    # Extra verb info mapping
    verbExtraMap: Dict[str, str] = {
        "-M":   "Middle significance",
        "-C":   "Contracted form",
        "-T":   "Transitive",
        "-A":   "Aeolic",
        "-ATT": "Attic",
        "-AP":  "Apocopated form",
        "-IRR": "Irregular or impure form"
    }
    
    # suffix mapping
    suffixMap: Dict[str, str] = {
        "-K":   "Crasis",
        "-N":   "Negative",
        "-S":   "Superlative",
        "-C":   "Comparative",
        "-ABB": "Abbreviated",
        "-I":   "Interrogative",
        "-ATT": "Attic",
        "-P":   "Particle Attached"
    }

    # Prepare output dict
    output = {}

    # Type-check
    if not isinstance(tag_input, str):
        output["Part of Speech"] = "Unknown or Unsupported"
        output["Error"]="Input must be a string"
        if debug:
            print(f"[decode_tag] ERROR: Expected str, got {type(tag_input).__name__!r}: {tag_input!r}")
        return output

    # Emptiness check
    if not tag_input.strip():
        output["Part of Speech"] = "Unknown or Unsupported"
        output["Error"]= "Input cannot be empty"
        if debug:
            print(f"[decode_tag] ERROR: Input is empty or only whitespace: {tag_input!r}")
        return output

    # Normalize and upper-case once, keep original for suffix lookup
    full_tag = tag_input.strip().upper()

    
    # Decode part of speech
    # The first line retrieve an array of all the keys from posMap.
    # We will iterating and find the first matching key.
    pos = None

    for key in posMap.keys():
        if tag_input.startswith(key):
            pos = key
            break
    
    if pos is None:
        output["Part of Speech"] = "Unknown or Unsupported"
        output["Error"]="POS unknown"
        if debug:
            print(f"[decode_tag] ERROR: POS unknown ({tag_input!r})")
        return output

    output["Part of Speech"] = posMap[pos]
    # strip off the POS prefix for feature decoding
    input_str = full_tag[len(pos):]
    
    # Further decoding based on the detected part of speech


    '''
    Verb patterns are depending on the 'mood':

       V- tense voice I person number      [- verb-extra]
       V- tense voice S person number      [- verb-extra]
       V- tense voice O person number      [- verb-extra]
       V- tense voice M person number      [- verb-extra]
       # The next [- verb-extra] was added to decode tag V-RAN-ATT (Luke 24:23)
       V- tense voice N                    [- verb-extra]   
       V- tense voice P case number gender [- verb-extra]
       V- tense voice R case number gender [- verb-extra]
    '''
    
    if pos == "V-":

        # Regex to split into the three parts: TVM, features, extra
        _PATTERN = re.compile(r"""
            ^V
            -(?P<tvm>[0-9]?[A-Z]{3})     # optional digit + 3 letters -> tense/voice/mood e.g. "PAI" or "2A..."
            (?:-(?P<feat>[1-3A-Z]{2,3}))?  # person/number or case/number/gender
            (?:-(?P<extra>[A-Z-]+))?       # optional verb-extra like "ATT"
            $
            """, re.VERBOSE)

        m = _PATTERN.match(tag_input)
        if not m:
            output["Error"] = f"Tag {tag_input} does not match expected pattern."
            if debug:
                print (f"[decode_tag] Regex to split verb parts failed for {tag_input}")
            return output

        groups = m.groupdict()
        tvm   = groups["tvm"]    or ""
        feat  = groups["feat"]   or ""
        extra = groups["extra"]  or ""


        # parse Tense–Voice–Mood from 'tvm'
        # Length of this part should be either 3 or 4 
        tenseKey = next((tk for tk in tenseMap if tvm.startswith(tk)), None)
        if tenseKey:
            output["Tense"] = tenseMap[tenseKey]
            rem = tvm[len(tenseKey):]
            # length should of `rem` is now 2
            voiceKey=rem[0]
            moodKey=rem[1]
            output["Voice"] = voiceMap.get(voiceKey, "Unknown")
            output["Mood"]  = moodMap.get(moodKey, "Unknown")
        else:
            output["Tense"] = "Unknown" # 

        # parse Person/Number or Case/Number/Gender from 'feat' based on 'mood'

        # moods Present/imperfect → Case/Number/Gender
        if moodKey in ['P','R']:
            if len(feat) == 3:
                output["Case"]   = caseMap.get(feat[0], "Unknown")
                output["Number"] = numberMap.get(feat[1], "Unknown")
                output["Gender"] = genderMap.get(feat[2], "Unknown")
            else:
                output["Error"] = f"Incomplete feature code"
                if debug==True:
                    print(f"[decode_tag] ERROR: Incorrect feature code (‘{feat}’) for mood {moodKey} ({mood})")

        # Indicative/Subjunctive/Optative/Imperative → Person/Number
        elif moodKey in ['I','S','O','M']:
            if len(feat) == 2:
                output["Person"] = personMap.get(feat[0], "Unknown")
                output["Number"] = numberMap.get(feat[1], "Unknown")
            else:
                output["Error"] = f"Incorrect feature code"
                if debug==True:
                    print(f"[decode_tag] ERROR: Incorrect feature code (‘{feat}’) for mood {moodKey} ({mood})")

        # Infinitive -> according to definition, there should be no more info. 
        # However, in practice it may also contain a suffix/verb extra element (e.g. V-RAN-ATT at Luke 24:23)
        elif moodKey=='N':
            if len(feat) > 0:
                output["Warning"] = f"Unexpected extra element (‘{feat}’) for mood N will be handled as verb extra"
                extra=feat

        # If the moodKey is not handled by any of the above, it contains incorrect information
        else:
            output["Error"] = f"Unrecognized moodKey {moodKey!r}"
            if debug:
                print(f"[decode_tag] ERROR: Unrecognized moodKey {moodKey!r}")

        # Optional verb-extra
        if len(extra) > 0:
            raw_suffix = "-" + extra
            if raw_suffix in verbExtraMap:
                output["Verb extra"] = verbExtraMap[raw_suffix]
            else:
                output["Verb extra"] = "Unknown verb extra"
                output["Warning"] = f"Unknown verb extra {raw_suffix}"
                if debug:
                    print(f"[decode_tag] WARNING: Unknown verb extra ({input_str!r})")

        # we are done for verbs 
        return output

    # indeclinables
    elif pos in indeclList:
        # This follows pattern: pos [suffix]
        # Only proceed if there actually is a dash in the original tag
        if "-" in input_str:
            # If it’s a known suffix, map it
            if input_str in suffixMap:
                output["Suffix"] = suffixMap[input_str]
            else:
                output["Warning"] = "Unknown suffix"
                if debug:
                    print(f"[decode_tag] WARNING: Unknown suffix ({tag_input!r})")
                
        # no dash → no suffix (which is perfectly OK)

        # we are done for indeclinables 
        return output
    # 
    elif pos in ["N-", "A-", "T-"]:
        if len(input_str) >= 3:
            output["Case"]   = caseMap.get(input_str[0], "Unknown")
            output["Number"] = numberMap.get(input_str[1], "Unknown")
            output["Gender"] = genderMap.get(input_str[2], "Unknown")
        else:
            output["Warning"]= "Not enough elements provided"
            if debug:
                print(f"[decode_tag] WARNING: Not enough elements provided for indeclinable ({tag_input!r})")
        # note: suffix will be decoded in the default branch

    # Reflexive Pronoun
    elif pos in ["F-"]:
        if len(input_str) >= 4:
            output["Person"] = personMap.get(input_str[0], "Unknown")
            output["Case"]   = caseMap.get(input_str[1], "Unknown")
            output["Number"] = numberMap.get(input_str[2], "Unknown")
            output["Gender"] = genderMap.get(input_str[3], "Unknown")
        else:
            output["Warning"] = "Not enough elements provided"
            if debug:
                print(f"[decode_tag] WARNING: Not enough elements provided for reflexive pronoun ({tag_input!r})")
        # note: suffix will be decoded in the default branch

    # Possessive Pronoun
    elif pos in ["S-"]:
        if len(input_str) >= 5:
            output["Person of Possessor"] = personMap.get(input_str[0], "Unknown")
            output["Number of Possessor"] = numberMap.get(input_str[1], "Unknown")
            output["Case of Possessed"]   = caseMap.get(input_str[2], "Unknown")
            output["Number of Possessed"] = numberMap.get(input_str[3], "Unknown")
            output["Gender of Possessed"] = genderMap.get(input_str[4], "Unknown")
        else:
            output["Warning"] = "Not enough elements provided"
            if debug:
                print(f"[decode_tag] WARNING: Not enough elements provided for possesive pronoun ({tag_input!r})")
        # note: suffix will be decoded in the default branch
    
    elif pos in pronList:
        # The overall pattern is: pos [person] case number [gender] [suffix]
        # Pattern 1: [case,number]
        if len(input_str)==2:
            output["Case"]   = caseMap.get(input_str[0], "Unknown")
            output["Number"] = numberMap.get(input_str[1], "Unknown")

        # Pattern 2: [person, case, number]
        elif len(input_str) >= 3 and re.match(r'^[123]$', input_str[0]):
            output["Person"] = personMap.get(input_str[0], "Unknown")
            output["Case"]   = caseMap.get(input_str[1], "Unknown")
            output["Number"] = numberMap.get(input_str[2], "Unknown")
    
        # Pattern 3: [case, number, gender]
        elif len(input_str) >= 3:
            output["Case"]   = caseMap.get(input_str[0], "Unknown")
            output["Number"] = numberMap.get(input_str[1], "Unknown")
            output["Gender"] = genderMap.get(input_str[2], "Unknown")
    
        # Pronoun-specific suffix (e.g. the “-K” in “P-1AS-K”)
        if "-" in input_str:
            raw_suffix = "-" + input_str.rsplit("-", 1)[1]
            if raw_suffix in suffixMap:
                output["Suffix"] = suffixMap[raw_suffix]
            else:
                output["Warning"] = "Unknown suffix"
                if debug:
                    print(f"[decode_tag] WARNING: Unknown suffix for pronoun {raw_suffix}")

        # we are done for indeclinables 
        return output

    # Only proceed if there actually is a dash after the POS tag
    if "-" in input_str:
        # Grab everything after the last '-' (including the dash)
        raw_suffix = '-'+input_str.rsplit("-", 1)[1]
        # If it’s a known suffix, map it
        if raw_suffix in suffixMap:
            output["Suffix"] = suffixMap[raw_suffix]
        else:
            output["Warning"] = "Unknown suffix"
            if debug:
                print(f"[decode_tag] ERROR: Unknown suffix in default branch {raw_suffix}")

        # no dash → no suffix (which is perfectly OK)

    if debug:
        print(f"[decode_tag] Return ({output})")

    return output

    # End of function decode_tag()


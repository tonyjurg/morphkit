# morphkit/init_compare_tags.py
# SPDX-License-Identifier: CC-BY-4.0
# Copyright (c) 2026 Tony Jurg
__version__ = "1.0.1"

from typing import Callable, Dict, Any, List, Tuple

"""                                                                                                         
Function:

    This module initalizes the various functions used to perform a comparison between two morphological tags.
    The calculated figures for similairity are intended to express *similairity in syntactic function*.
    For example a verb with mood=indicative function in a sentence is completly different than when the verb has
    mood=participle or infinitive. The latter may perform functionaly noun-like. Hence the compare_tags function 
    will assign a higher value for similairity for them when comparing them with a noun.

References:

    The grammar used for the analysis in this file is mostly taken from these two books:
        - Daniel B. Wallace. The Basics of New Testament Syntax (Grand Rapids, MI: Zondervan, 2009),
          shortened in this file to BNT.
        - Daniel B. Wallace. Greek Grammar beyon the Basics (Grand Rapids, MI: Zondervan, 2009),
          shortened in this file to GGBB.

Implementation:

    Factory that initializes and returns a fully-configured `compare_tags` function.

    This function sets up:
    
      - Feature weights for each grammatical category.
      - Similarity functions for Part of Speech, Number, Tense, Voice, Mood,
        Gender, Case, Person, and Suffix, using predefined matrices and
        an optional substring fallback for suffixes.
      - The compare function should be symmetric, so sim(X,Y)=sim(Y,X))

    Args:

        None

    Returns:
    
        Callable[[str, str, bool], dict]: A `compare_tags` function with the signature:
            compare_tags(
                tag1 (str),
                tag2 (str),
                debug (bool=True)
            ) -> {
                'tag': str,
                'overall_similarity': float,
                'details': Dict[str, Dict[str, Union[str,float]]]
            }

    Example (end-user perspective):
    
        >>> morphkit.compare_tags("N-NSN-ATT", "N-ASM-ATT")
        {'tag': 'N-ASM-ATT',
         'overall_similarity': 0.8883720930232557,
         'details': {'Part of Speech': {'known': 'Noun',
         ... }


""" 


# Bring in the decoder from the sibling module
from .decode_tag import decode_tag


def init_compare_tags():
    """
    Factory that initializes and returns a fully-configured :py:func:`~morphkit.compare_tags` function.

    This function sets up:
    
      -  Feature weights for each grammatical category.

      -  Similarity functions for `Part of Speech`, `number`, `tense`, `voice`, `mood`,
         `gender`, `case`, `person`, and `suffix` using predefined matrices and an optional substring fallback for suffixes.

      -  The compare function should be symmetric, so sim(X,Y)=sim(Y,X))

    The returned function will:

          1. Decode each tag with :py:func:`~morphkit.decode_tag`.
          2. Compute per-feature similarities.
          3. Weight and sum them (as defined in this function).
          4. Normalize to the range [0.0, 1.0], inclusive.

        The calculated figures for similairity are intended to express *similairity in syntactic function*.

    For example the function of a verb with `mood=indicative` in a sentence is completly different than when the verb has `mood=participle` or `infinitive`. The latter may perform functionaly noun-like. Hence the `compare_tags` function   will assign a higher value for similairity for them when calculating the similairity with a noun.

    Args:
    -----

        :None:

    Returns:
    --------

        :Callable[[str, str, bool], dict]: the function :py:func:`.morphkit.compare_tags`:

        .. code-block:: python

            compare_tags(
                tag1 (str),     # the gold standard
                tag2 (str),     # the tag to compare with the gold standard
                debug (bool=True)
            ) -> {
                'tag': str,
                'overall_similarity': float,
                'details': Dict[str, Dict[str, Union[str,float]]]
            }

    Example:
    --------

    In this example we use the *generated* :py:func:`~morphkit.compare_tags` function:
    
        .. code-block:: python

           morphkit.compare_tags("N-NSN-ATT", "N-ASM-ATT")
           {'tag': 'N-ASM-ATT',
            'overall_similarity': 0.8883720930232557,
            'details': {'Part of Speech': {'tag1': 'Noun',
            ... }
    """


    # 1) Feature weights (adjustable)
    weights = {
        "Part of Speech": 10,
        "Number":          3,
        "Tense":           8,
        "Voice":           6,
        "Mood":            6,
        "Gender":          2,
        "Case":            4,
        "Person":          3,
        "Suffix":          1,
    }


    # 2) Generic matrix-sim builder 
    def make_matrix_similarity(labels, matrix, fallback=None, fallback_score=0.0):
        """
          
          Build a similarity function from a labeled similarity matrix.
        
            Returns a function that compares two feature values by:
              1. Returning 1.0 if they match exactly.
              2. Looking up their score in the provided matrix.
              3. Applying an optional fallback predicate before returning 0.0.
        
            Args:
            
                labels (List[str]): Ordered list of N feature labels.
                matrix (List[List[float]]): N×N matrix where matrix[i][j] is the similarity
                    score between labels[i] and labels[j].
                fallback (Optional[Callable[[str, str], bool]]): A predicate that, if true
                    for a pair (known, generated), forces the fallback_score.
                fallback_score (float): Score to return when fallback(...) is True.
        
            Returns:
            
                Callable[[str, str], float]: A function `sim_fn(known, generated)` that returns
                a float in the range [0.0, 1.0].
        
            Example:
            
                sim = make_matrix_similarity(['A','B'], [[1.0,0.5],[0.5,1.0]])
                assert sim('A','B') == 0.5
                
        """
        
        idx = {lab: i for i, lab in enumerate(labels)}
    
        def sim_fn(known, generated):
            # exact match
            if known == generated:
                return 1.0
            # lookup in matrix
            i = idx.get(known)
            j = idx.get(generated)
            if i is not None and j is not None:
                return matrix[i][j]
            # custom fallback (e.g. suffix‐substring)
            if fallback and fallback(known, generated):
                return fallback_score
            # otherwise no similarity
            return 0.0
    
        return sim_fn

    # 3) Build each similarity function *after* the builder is defined

    """ a) PART OF SPEECH
    
    Reasoning for the values in this matrix:

        For the core POS 'open-class' categories:
        
              Noun vs Verb  = 0.2: usualy not similair, except for infinitive and participle (see last block!)
              Noun vs Adj   = 0.5: adjectives agree with nouns in case/number/gender vs moderate closeness.
              Verb vs Adv   = 0.2: usualy not similair, except for infinitive and participle (see last block!)
              Verb vs Conj  = 0.7: conjunctions join predicates/clauses—slightly closer to verbs than nouns.
              Adv  vs Adj   = 0.5: overlap in function (manner, degree), but different inflection.
        
        The pronoun subtypes all cluster around personal pronoun:
        
              Personal vs Relative/Reciprocal/… = 0.8: they share “pronominal” morphology.
              Correlative vs Interrogative      = 0.9: these two are historically variants of each other.
              Most pronouns vs Noun             = 0.2: pronouns stand in for nouns, but morphologically distinct.
        
        For items with Indeclinable flags:
        
             Particle vs Preposition vs Interjection each get 1.0 on the diagonal (self‐match).
             Particle vs Interjection       = 0.3: both uninflected function words.
             Interjection vs Aramaic/Hebrew = 0.9: in Biblical context these loan‐words behave often like interjections (very close).
             particle vs conjunctions       = 0.8 : where conjuctions link, particles modify.
        
        Proper Noun Indeclinable” and “Noun Other Type Indeclinable”:
        
             Noun vs N-PNI  = 0.9 : (treated distinct). ([TBC] not sure  ....)
             Noun vs N-LI   = 0.9 : family of nouns
             Noun vs N-NOI  = 0.9 : “other noun indeclinable” is just a noun with irregular morphology—very similar.
        
        Language-origin flags (“Aramaic”, “Hebrew”):
        
            Aramaic vs Hebrew   = 1.0: both are foreign language tokens, used in similar ways.
            Aramaic vs Noun     = 0.6: many Aramaic elements in the Greek text function like nouns.
            Hebrew vs Noun      = 0.6: likewise 
            Hebr/Aram vs Interj = 0.6: also some are interjections like Amen).
            
        On top of the POS catagories returned by our intial analysis, we need to add (for this matrix) two classes.
        These are added at the end of the matrix. Their values are based upon:

          - Participle: a declinable verbal adjective; GGBB p.613
               Noun sim.: substantival use; GGBB p.613 = 0.7
               Verb sim.: shares tense/voice; GGBB p.613 = 0.8
               Adj sim.: verbal adjective GGBB p.613 = 0.9
               Adv sim.: participle as adverbial (circumstantial) = 0.4
               against infin = 0.5

          - Infinitive: an indeclinable verbal noun; GGBB p.588
               Noun sim.: verbal noun; GGBB p.588 = 0.8
               Verb sim.: verbal form = 0.9
               Adj sim.: rare adjectival use = 0.3
               Adv sim.: infinitive as adverbial (purpose/result) = 0.5
               against particpl = 0.5

    """
    
    pos_labels = ["Noun", "Verb", "Adjective", "Adverb", "Conjunction", 
                  "Personal Pronoun", "Relative Pronoun", "Reciprocal Pronoun", 
                  'Demonstrative Pronoun', 'Correlative Pronoun', 'Interrogative Pronoun',
                  'Indefinite Pronoun', 'Correlative or Interrogative Pronoun', 'Reflexive Pronoun',
                  'Possessive Pronoun','Particle', 'Preposition', 'Interjection',
                  'Proper Noun Indeclinable','Numeral Indeclinable', 'Letter Indeclinable', 
                  'Noun Other Type Indeclinable', 'Aramaic', 'Hebrew', 'Participle', 'Infinitive']
                  # Last two pos_labels were added (see function docblock).
    
    pos_matrix = [
        #                               |--------------------------pronouns -----------------------------|
        # noun verb  adj   adv   conj  prsn.  rela.  recu   demns. corr.  Intr.  Indf.  Cr/Int Refl.  Poss.  Prtl   Prep.  Intj.  N-PRI  A-NUI  N-LI   N-OI   ARR    HEB   Ptc.  Inf.  
    
        # Noun row:       
        [1.0,  0.2,  0.5,  0.4,  0.2,  0.2,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.9,   0.0,   0.9,   0.9,   0.6,   0.6,  0.7,  0.8],
        # Verb row:
        [0.2,  1.0,  0.5,  0.6,  0.7,  0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,  0.7,  0.9],
        # Adjective row:
        [0.5,  0.5,  1.0,  0.5,  0.4,  0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,  0.9,  0.3],
        # Adverb row:
        [0.4,  0.6,  0.5,  1.0,  0.3,  0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,  0.4,  0.5],
        # Conjunction row:
        [0.2,  0.7,  0.4,  0.3,  1.0,  0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.8,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,  0.0,  0.0],
    
        # ——— Pronoun block ———
        # Personal Pronoun:
        [0.2,  0.0,  0.0,  0.0,  0.0,  1.0,   0.8,   0.8,   0.8,   0.8,   0.8,   0.8,   0.8,   0.8,   0.8,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,  0.0,  0.0],
        # Relative Pronoun:
        [0.0,  0.0,  0.0,  0.0,  0.0,  0.8,   1.0,   0.8,   0.8,   0.8,   0.8,   0.8,   0.8,   0.8,   0.8,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,  0.0,  0.0],
        # Reciprocal Pronoun:
        [0.0,  0.0,  0.0,  0.0,  0.0,  0.8,   0.8,   1.0,   0.8,   0.8,   0.8,   0.8,   0.8,   0.8,   0.8,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,  0.0,  0.0],
        # Demonstrative Pronoun:
        [0.0,  0.0,  0.0,  0.0,  0.0,  0.8,   0.8,   0.8,   1.0,   0.8,   0.8,   0.8,   0.8,   0.8,   0.8,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,  0.0,  0.0],
        # Correlative Pronoun:
        [0.0,  0.0,  0.0,  0.0,  0.0,  0.8,   0.8,   0.8,   0.8,   1.0,   0.8,   0.8,   0.9,   0.8,   0.8,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,  0.0,  0.0],
        # Interrogative Pronoun:
        [0.0,  0.0,  0.0,  0.0,  0.0,  0.8,   0.8,   0.8,   0.8,   0.8,   1.0,   0.8,   0.9,   0.8,   0.8,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,  0.0,  0.0],
        # Indefinite Pronoun:
        [0.0,  0.0,  0.0,  0.0,  0.0,  0.8,   0.8,   0.8,   0.8,   0.8,   0.8,   1.0,   0.8,   0.8,   0.8,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,  0.0,  0.0],
        # Correlative/Interrogative Pronoun:
        [0.0,  0.0,  0.0,  0.0,  0.0,  0.8,   0.8,   0.8,   0.8,   0.9,   0.9,   0.8,   1.0,   0.8,   0.8,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,  0.0,  0.0],
        # Reflexive Pronoun:
        [0.0,  0.0,  0.0,  0.0,  0.0,  0.8,   0.8,   0.8,   0.8,   0.8,   0.8,   0.8,   0.8,   1.0,   0.8,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,  0.0,  0.0],
        # Possessive Pronoun:
        [0.0,  0.0,  0.0,  0.0,  0.0,  0.8,   0.8,   0.8,   0.8,   0.8,   0.8,   0.8,   0.8,   0.8,   1.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,  0.0,  0.0],
    
        # ——— Other indeclinables & language flags ———
        # Particle:
        [0.0,  0.0,  0.0,  0.0,  0.8,  0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   1.0,   0.0,   0.3,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,  0.0,  0.0],
        # Preposition:
        [0.0,  0.0,  0.0,  0.0,  0.0,  0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   1.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,  0.0,  0.0],
        # Interjection:
        [0.0,  0.0,  0.0,  0.0,  0.0,  0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.3,   0.0,   1.0,   0.0,   0.0,   0.0,   0.0,   0.6,   0.6,  0.0,  0.0],
        # Proper Noun Indeclinable (N-PRI):
        [0.9,  0.0,  0.0,  0.0,  0.0,  0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   1.0,   0.0,   0.0,   0.0,   0.0,   0.0,  0.0,  0.0],
        # Numeral Indeclinable (A-NUI):
        [0.0,  0.0,  0.0,  0.0,  0.0,  0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   1.0,   0.0,   0.0,   0.0,   0.0,  0.0,  0.0],
        # Letter Indeclinable  (N-LI):
        [0.9,  0.0,  0.0,  0.0,  0.0,  0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   1.0,   0.0,   0.0,   0.0,  0.0,  0.0],
        # Noun Other Type Indeclinable (N-OI):
        [0.9,  0.0,  0.0,  0.0,  0.0,  0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   1.0,   0.0,   0.0,  0.0,  0.0],
        # Aramaic:
        [0.6,  0.0,  0.0,  0.0,  0.0,  0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.6,   0.0,   0.0,   0.0,   0.0,   1.0,   0.0,  0.0,  0.0],
        # Hebrew:
        [0.6,  0.0,  0.0,  0.0,  0.0,  0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.6,   0.0,   0.0,   0.0,   0.0,   0.0,   1.0,  0.0,  0.0],

        # ——— Additional classes for special verb types ———
        # Participle:
        [0.7,  0.7,  0.9,  0.4,  0.0,  0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,  1.0,  0.5],
        # Infinitive:
        [0.8,  0.9,  0.3,  0.5,  0.0,  0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,  0.5,  1.0]
    ]
    
    # Perform basic sanity check on this matrix
    assert len(pos_labels) == len(pos_matrix), "Row count mismatch"
    for row in pos_matrix:
        assert len(row) == len(pos_labels), "Column count mismatch"

    # Symmetry check for Part-of-Speech, so sim(X,Y)=sim(Y,X)
    for i in range(len(pos_matrix)):
        for j in range(len(pos_matrix)):
            assert pos_matrix[i][j] == pos_matrix[j][i], \
                f"POS symmetry mismatch at {pos_labels[i]} vs {pos_labels[j]}: {pos_matrix[i][j]} != {pos_matrix[j][i]}"

    # Build the POS similarity function
    get_pos_similarity = make_matrix_similarity(pos_labels, pos_matrix)
    
    
    """ 2) NUMBER
    
    Reasoning for the values in this matrix:
    
       Diagonal                = 1.0: every 'number' is a perfect match with itself.
       Singular vs Dual        = 0.8: both are “small” numbers (one or two), also due to historical treatment of the dual form.
       Singular/Dual vs Plural = 0.4: conceptually further away. ([TBC] maybe still too high??)
       
    """
    
    number_labels = ["Singular", "Dual", "Plural"]
    
    number_matrix = [
        #Sing Dual Plur
        [1.0, 0.8, 0.4],  # Sing vs …
        [0.8, 1.0, 0.4],  # Dual vs …
        [0.4, 0.4, 1.0],  # Plural vs …
    ]

    # Build the NUMBER similarity function
    get_number_similarity = make_matrix_similarity(number_labels, number_matrix)
    
    
    
    """ c) TENSE
    
    Reasoning for the values in this matrix:
    
        Diagonal                     = 1.0: every 'tense' is a perfect match with itself.
        Present vs Imperfect         = 0.8: both imperfective.
        Present vs Future            = 0.6, Imperfect⇄Future = 0.8: Future is imperfective, closer to Imperfect.
        Future vs 2nd-Future         = 0.9: variant forms of same future.
        Aorist vs 2nd-Aorist         = 0.9: variant forms of same future.
        Perfect vs 2nd-Perfect       = 0.9: variant forms of same future.
        Perfect vs Pluperfect        = 0.8: resultative aspect shared.
        Pluperfect vs 2nd-Pluperfect = 0.9: variant forms of same future.
        perfective vs imperfective   = 0.0: Cross-aspect (no commonality).
        No-tense (X; fallback)       = 0.2: for all cases ([TBC] not sure if this is the best fallback).
    """
    
    tense_labels = ["Present", "Imperfect", "Future", "Second Future", "Aorist", "Second Aorist",  "Perfect", "Second Perfect", "Pluperfect", "Second Pluperfect", "No Tense Stated"]
    
    tense_matrix = [
       # pres impf  fut  2fut   aor   2aor  perf  2per  +per  2+pr  X
        [1.0, 0.8, 0.6, 0.6,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.2],  # Present vs …
        [0.8, 1.0, 0.8, 0.8,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.2],  # Imperfect vs …
        [0.6, 0.8, 1.0, 0.9,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.2],  # Future vs …
        [0.6, 0.8, 0.9, 1.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.2],  # Second Future vs …
        [0.0, 0.0, 0.0, 0.0,  1.0,  0.9,  0.0,  0.0,  0.0,  0.0,  0.2],  # Aorist vs …
        [0.0, 0.0, 0.0, 0.0,  0.9,  1.0,  0.0,  0.0,  0.0,  0.0,  0.2],  # Second Aorist vs …
        [0.0, 0.0, 0.0, 0.0,  0.0,  0.0,  1.0,  0.9,  0.8,  0.8,  0.2],  # Perfect vs …
        [0.0, 0.0, 0.0, 0.0,  0.0,  0.0,  0.9,  1.0,  0.8,  0.8,  0.2],  # Second Perfect vs …
        [0.0, 0.0, 0.0, 0.0,  0.0,  0.0,  0.8,  0.8,  1.0,  0.9,  0.2],  # Pluperfect vs …
        [0.0, 0.0, 0.0, 0.0,  0.0,  0.0,  0.8,  0.8,  0.9,  1.0,  0.2],  # Second Pluperfect vs …
        [0.2, 0.2, 0.2, 0.2,  0.2,  0.2,  0.2,  0.2,  0.2,  0.2,  1.0],  # No Tense Stated vs …
    ]
    
    # Perform basic sanity check on this matrix
    assert len(tense_labels) == len(tense_matrix), "Row count mismatch"
    for row in tense_matrix:
        assert len(row) == len(tense_labels), "Column count mismatch"

    # Symmetry check for Tense, so sim(X,Y)=sim(Y,X)
    for i in range(len(tense_matrix)):
        for j in range(len(tense_matrix)):
            assert tense_matrix[i][j] == tense_matrix[j][i], \
                f"Tense symmetry mismatch at {pos_labels[i]} vs {pos_labels[j]}: {tense_matrix[i][j]} != {tense_matrix[j][i]}"

    # Build TENSE similarity function
    get_tense_similarity = make_matrix_similarity(tense_labels, tense_matrix)
    
    
    """ d) VOICE
    
    Reasoning for the values in this matrix:
    
        Diagonal                              = 1.0: Every 'voice' is a perfect match with itself.
        Middle vs Middle Deponent             = 0.9: deponent forms differ only morphologically.
        Passive vs Passive Deponent           = 0.9: deponent forms differ only morphologically.
        Middle vs Passive                     = 0.8: “middle/passive” covers both, so pretty similar (same for variants M/P ⇄ M, M/P ⇄ P).
        Middle vs Middle or Passive           = 0.8: voice is close to each other.
        Passive vs Middle or Passive          = 0.8: voice is close to each other.
        Middle vs Middle or Passive Deponent  = 0.9: very close.
        Passive vs Middle or Passive Deponent = 0.9: very close.
        Active vs Impersonal Active           = 0.8: behave syntactically like active in meaning.
        Everything vs No Voice                = 0.2: “no voice stated” is a low‐certainty fallback situation.
        All other pairs are set to 0.0 since they either contradict (eg., Active versus Passive) or there is no real overlap.
    """
    
    voice_labels = [
        "Active",
        "Middle",
        "Passive",
        "Middle or Passive",
        "Middle Deponent",
        "Passive Deponent",
        "Middle or Passive Deponent",
        "impersonal Active",
        "no voice"
    ]
    
    voice_matrix = [
       #  Act   Mid   Pas   M/P   M-Dep  P-Dep  M/P-Dep ImpAct NoV
        [1.0,  0.0,  0.0,  0.0,  0.0,   0.0,   0.0,    0.8,   0.2],   # Active vs …
        [0.0,  1.0,  0.0,  0.8,  0.9,   0.0,   0.9,    0.0,   0.2],   # Middle vs …
        [0.0,  0.0,  1.0,  0.8,  0.0,   0.9,   0.9,    0.0,   0.2],   # Passive vs …
        [0.0,  0.8,  0.8,  1.0,  0.8,   0.8,   0.9,    0.0,   0.2],   # Middle or Passive vs …
        [0.0,  0.9,  0.0,  0.8,  1.0,   0.0,   0.8,    0.0,   0.2],   # Middle Deponent vs …
        [0.0,  0.0,  0.9,  0.8,  0.0,   1.0,   0.8,    0.0,   0.2],   # Passive Deponent vs …
        [0.0,  0.9,  0.9,  0.9,  0.8,   0.8,   1.0,    0.0,   0.2],   # Middle or Passive Deponent vs …
        [0.8,  0.0,  0.0,  0.0,  0.0,   0.0,   0.0,    1.0,   0.2],   # Impersonal Active vs …
        [0.2,  0.2,  0.2,  0.2,  0.2,   0.2,   0.2,    0.2,   1.0],   # No Voice vs …
    ]

    # Perform basic sanity check on this matrix
    assert len(voice_labels) == len(voice_matrix), "Row count mismatch"
    for row in voice_matrix:
        assert len(row) == len(voice_labels), "Column count mismatch"
        
    # Build the VOICE similarity function
    get_voice_similarity = make_matrix_similarity(voice_labels, voice_matrix)
    
    
    
    """ e) MOOD
    
    Reasoning for the values in this matrix:
    
        Diagonal                            = 1.0: Every 'mood' is a perfect match with itself.
        Indicative vs Subjunctive           = 0.8: Both express realis vs. potential truth-values in finite clauses so are quite similar syntactically.
        Subjunctive vs Optative             = 0.8: The Optative is a more “remote” potential. Also grammatically and morphologically it groups with the Subjunctive.
        Indicative vs Optative              = 0.0: Indicative is realis while the Optative is pure potential, so there is no overlap.
        Imperative vs Imperative Participle = 0.8: The Imperative Participle adds adjectival force to a command (“being X, do Y…”), so quite close to the pure Imperative.
        Infinitive vs Participle            = 0.6: Both are non-finite forms without person/number.
        Infinitive vs Imperative Participle = 0.5: Both non-finite, but the Imperative Participle has a directive flavor (slightly less close than just “Participle”).
        Participle vs Imperative Participle = 0.9: Both are participles where the latter one just adds an imperative nuance.
        Everything else not listed above    = 0.0: There seems to be no meaningful overlap.
        
    """
    
    mood_labels = ["Indicative", "Subjunctive", "Optative", "Imperative", "Infinitive", "Participle", "Imperative Participle"]
    
    mood_matrix = [
       # Ind   Sub   Opt   Imp   Inf   Part  ImpPart
        [1.0,  0.8,  0.0,  0.0,  0.0,  0.0,  0.0   ],  # Indicative vs …
        [0.8,  1.0,  0.8,  0.0,  0.0,  0.0,  0.0   ],  # Subjunctive vs …
        [0.0,  0.8,  1.0,  0.0,  0.0,  0.0,  0.0   ],  # Optative vs …
        [0.0,  0.0,  0.0,  1.0,  0.0,  0.0,  0.8   ],  # Imperative vs …
        [0.0,  0.0,  0.0,  0.0,  1.0,  0.6,  0.5   ],  # Infinitive vs …
        [0.0,  0.0,  0.0,  0.0,  0.6,  1.0,  0.9   ],  # Participle vs …
        [0.0,  0.0,  0.0,  0.8,  0.5,  0.9,  1.0   ],  # Imperative Participle vs …
    ]

    assert len(mood_labels) == len(mood_matrix), "Row count mismatch in Mood"
    for row in mood_matrix:
        assert len(row) == len(mood_labels), "Column count mismatch in Mood"
    # Build the MOOD similarity function
    get_mood_similarity = make_matrix_similarity(mood_labels, mood_matrix)
    
    
    
    """ f) GENDER 
    
    Reasoning for the values in this matrix:
    
        Diagonal         = 1.0: Every gender is a perfect match with itself.
        Everything else  = 0.2: I want to put some weight to the fact the word is gendered, even with the 'wrong' one.
        
    """
    gender_labels = ["Masculine", "Feminine", "Neuter"]
    
    gender_matrix = [
        [1.0, 0.2, 0.2],  # Masculine vs …
        [0.2, 1.0, 0.2],  # Feminine vs …
        [0.2, 0.2, 1.0],  # Neuter vs …
    ]

    # Build the GENDER similarity function
    get_gender_similarity = make_matrix_similarity(gender_labels, gender_matrix)
    
    
    
    """ g) CASE
    
    Reasoning for the values in this matrix:
    
       Diagonal                = 1.0: Every 'case' is a perfect match with itself.
       Nominative vs Vocative  = 0.8: Here is form similairity and vocative is a direct “address” form of the subject.
       Accusative vs Dative    = 0.4: Although the endings differ, they’re both “objective” cases.
       Other off-diagonals     = 0.2: Litle commonality, but give some credit to the word having a case.
       
    """
    
    case_labels = ["Nominative", "Accusative", "Genitive", "Dative", "Vocative"]
    
    case_matrix = [
       # Nom  Acc  Gen  Dat  Voc
        [1.0, 0.2, 0.2, 0.2, 0.8],  # Nominative vs …
        [0.2, 1.0, 0.2, 0.4, 0.2],  # Accusative vs …
        [0.2, 0.2, 1.0, 0.2, 0.2],  # Genitive vs …
        [0.2, 0.4, 0.2, 1.0, 0.2],  # Dative vs …
        [0.8, 0.2, 0.2, 0.2, 1.0],  # Vocative vs …
    ]
    
    # Build the CASE similarity function 
    get_case_similarity = make_matrix_similarity(case_labels, case_matrix)
    
    
    
    """ h) PERSON

    Reasoning for the values in this matrix:
    
        Diagonal         = 1.0: Every 'person' is a perfect match with itself.
        Everything else  = 0.2: I want to put some weight to the fact the word is 'personed', even with the 'wrong' one.

    """
    person_labels = ["First", "Second", "Third"]
    
    person_matrix = [
        [1.0, 0.2, 0.2],  # 1st
        [0.2, 1.0, 0.2],  # 2nd
        [0.2, 0.2, 1.0],  # 3rd
    ]

    # Build the PERSON similarity function
    get_person_similarity = make_matrix_similarity(person_labels, person_matrix)
    
    
    """ i) SUFFIX 
    
    For suffixes, there is currently no precomputed matrix defined, so we:
      - pass empty labels & matrix
      - use a fallback that checks if one suffix string is contained in the other
      - assign a “medium” similarity of 0.5 for any substring match
    
    """
    
    suffix_labels = []
    suffix_matrix = []
    suffix_fallback = lambda k, g: bool(k and g and (k in g or g in k))

    # Build the SUFFIX similarity function
    get_suffix_similarity = make_matrix_similarity(
        suffix_labels,
        suffix_matrix,
        fallback=suffix_fallback,
        fallback_score=0.5
    )


    # Gather all the feature‐specific sim functions into one lookup.
    # These functions will be called when comparing the corresponding feature.
    sim_funcs = {
        "Part of Speech":  get_pos_similarity,
        "Number":          get_number_similarity,
        "Tense":           get_tense_similarity,
        "Voice":           get_voice_similarity,
        "Mood":            get_mood_similarity,
        "Gender":          get_gender_similarity,
        "Case":            get_case_similarity,
        "Person":          get_person_similarity,
        "Suffix":          get_suffix_similarity,
    }

    # 4) The actual compare_tags, closing over weights & sim_funcs
    
    def compare_tags(tag1, tag2, debug=False):
        
        """
        Compare two morphological parsing tags by decoding them into features
        and computing a weighted similarity score.
    
        This function is generated by :py:func:`~morphkit.init_compare_tags` and performs the following actions:
            
              1. Uses `decodeTag` to turn each tag (e.g. "V-PAI-3S") into a dict of
                 grammatical features.
                 
              2. For each feature (Part of Speech, Tense, Case, etc.), looks up the
                 similarity via prebuilt similarity functions.
                 
              3. Multiplies each similarity by its weight, sums and normalizes to
                 the range [0.0,1.0].
                 
              4. Returns both the overall score and a breakdown per feature.
        
        Args:
        -----
            
            :tag1 (str):  The “gold standard” tag you expect (e.g. from a reference corpus).
            
            :tag2 (str): The tag you want to evaluate against the "gold standard".
            
            :debug (bool): Optional argument. Defaults to `False`. If `True`, print each feature’s known vs. generated value,
                    the raw similarity score, and the feature’s weight. 
        
        Returns:
        --------
            
            :dict: A dictionairy with the following structure:

                .. code-block:: python

                    "tag" (str),                   # echo of `generated_tag`.
                    "overall_similarity" (float)   # weighted, normalized [0.0–1.0].
                    "details" (dict)               # for each feature name, a sub-dict with:
                        "tag1" (str)               # the decoded known feature.
                        "tag2" (str)               # the decoded generated feature.
                        "similarity" (float)       # the raw sim score (0.0–1.0).
        
        Example:
        --------

            .. code-block:: python
                
                result = morphkit.compare_tags("N-NSM", "N-DSM")
                print(result["overall_similarity"])
                0.875
                print(result["details"]["Case"])
                {"tag1": "Nominative", "tag2": "Dative", "similarity": 0.2}


        Flow diagram:
        -------------

            .. code-block:: none

                       +----------------------------+
                       | decode_tag(tag1)           |
                       | decode_tag(tag2)           | 
                       +-------------+--------------+
                                     |
                                     v
                +------------------------------------------+
                |   Adjust POS if Mood = Participle/Inf    |
                +--------------------+---------------------+
                                     |
                                     v
                +------------------------------------------+
                | for each feature in weights:             |
                |   - get tag1/2 values                    |
                |   - sim = sim_funcs[feature](tag1, tag2) |
                |   - accumulate score × weight            |
                |   - store details                        |
                +--------------------+---------------------+
                                     |
                                     v
                +------------------------------------------+
                |     Normalize: total_score / weight      |
                +--------------------+---------------------+
                                     |
                                     v
                +------------------------------------------+
                | Return: dict with tag1, tag2, similarity |
                |          and per-feature details         |
                +------------------------------------------+

        """

        # If debugging is enabled, print the raw input values for the tags to compare
        if debug==True:
            print(f"[compare_tags] First tag: {tag1};  second tag: {tag2}")

        # Decode each tag string into a dictionary of grammatical features
        tag1_dict = decode_tag(tag1)
        tag2_dict = decode_tag(tag2)

        # Override POS if currently 'Verb' but actual form is non-finite
        for d in (tag1_dict, tag2_dict):
            if d.get("Part of Speech") == "Verb":
                m = d.get("Mood", "")
                if m == "Participle":   # mood==P in tag
                    d["Part of Speech"] = "Participle"
                elif m == "Infinitive":  # mood==N in tag
                    d["Part of Speech"] = "Infinitive"

        # Initialize accumulators for the weighted score and total weight
        total_score, total_weight = 0.0, 0
        # Prepare a dict to hold per-feature details
        details = {}

        # Loop over each feature and its weight
        for feat, w in weights.items():
            # Look up the feature value in each decoded dict (defaulting to empty string)
            t1 = tag1_dict.get(feat, "")
            t2 = tag2_dict.get(feat, "")
            # Compute similarity for this feature using the corresponding sim function
            sim = sim_funcs[feat](t1, t2)
            # In case 'Part of Speech' is 'Unknown or Unsupported', comparing does not make sense. Return 0
            if t1=='Unknown or Unsupported' or t2=='Unknown or Unsupported': 
                sim=0
                w=0
                # we do not break out of the loop on purpose to allow for a uniform details block to be returned
            if t1=='' or t2=='':
            # If there is nothing to compare for a feature, leave it out the calculation, but still report it
                sim=0
                w=0
            # Record the feature values for tag1 and tag2 and their raw similarity
            details[feat] = {
                "tag1": t1, 
                "tag2": t2, 
                "similarity": sim,
                "weight": w
            }
            total_score  += sim * w
            total_weight += w

            # Accumulate weighted similarity and total weight
            if debug:
                print(f"[compare_tags] {feat:17s}: {t1:12s} vs {t2:12s} → sim={sim:.2f}, weight={w}")

        # Compute the overall similarity (normalized to [0.0, 1.0])
        overall = total_score / total_weight if total_weight else 0.0

        # If debugging, print the final overall similarity
        if debug:
            print(f"[compare_tags]  Overall similarity: {overall:.3f}")

        # Return a structured report including the generated tag, overall score, and per-feature breakdown
        return {
            "tag1"               : tag1, 
            "tag2"               : tag2,
            "overall_similarity" : overall, 
            "details"            : details
        }

    return compare_tags

    # End of function init_compare_tags()
Architecture
============

This page documents the software architecture of Morphkit as released in ``1.0.0``. It combines the functional overview from the project description with implementation details from the code in this repository.

For this initial release, the architecture should be read as the architecture of a packaged research snapshot. Morphkit is not presented here as a universal morphology platform, but as the project-specific translation layer that connects Morpheus analyses to the SP / ``N1904-TF`` conventions used in the Nestle1904 Text-Fabric workflow.

.. _morpheus-api: https://github.com/perseidsproject/morpheus-api
.. _morpheus-engine: https://github.com/perseids-tools/morpheus-perseids
.. _beta-code: https://stephanus.tlg.uci.edu/encoding.php
.. _n1904: https://github.com/CenterBLC/N1904
.. _n1904-sp: https://github.com/biblicalhumanities/Nestle1904/blob/master/morph/parsing.txt
.. _text-fabric: https://annotation.github.io/text-fabric/tf/index.html

Overview
--------

Morphkit is a small Python middleware layer between:

- Python research scripts or notebooks,
- a deployed `Morpheus API <morpheus-api_>`_ service backed by the `Morpheus engine <morpheus-engine_>`_,
- downstream consumers such as `Text-Fabric <text-fabric_>`_ export pipelines.

In other words, ``1.0.0`` is a semantic translation layer between incompatible morphological systems, packaged so that the same logic can be reinstalled and reused reproducibly inside the research environment for which it was designed.

At a high level, Morphkit takes a word form encoded in `Beta Code <beta-code_>`_, retrieves one or more analyses from Morpheus over HTTP, parses the raw text blocks into Python dictionaries, and augments those dictionaries with:

- part-of-speech classifications,
- Sandborg-Petersen-style morphological tags aligned with the `N1904-TF schema <n1904-sp_>`_,
- optional tag similarity scores and analysis ranking.

Runtime Model
-------------

Morphkit does not embed Morpheus locally. Instead, it assumes that Morpheus is already available behind an HTTP endpoint and that client code knows the host and port of that service.

.. code-block:: text

   +--------------------+      HTTP       +--------------------+
   | User Python code   | <-------------> | Morpheus API       |
   | or notebook        |                 | endpoint           |
   +---------+----------+                 +---------+----------+
             |                                      |
             | calls Morphkit                       | runs Morpheus
             v                                      v
   +--------------------------------------------------------------+
   | Morphkit                                                     |
   | - request layer                                               |
   | - block splitting                                             |
   | - parse normalization                                         |
   | - POS inference                                               |
   | - SP morph-tag generation                                     |
   | - optional similarity / ranking                               |
   +--------------------------------------------------------------+

This design keeps the package lightweight and makes the analysis pipeline reproducible, because the same Morpheus service can be queried from scripts, notebooks, or batch jobs. That reproducibility refers to the project workflow: it does not imply that Morphkit is already detached from the assumptions of the ``N1904-TF`` environment.

End-to-End Flow
---------------

The main entry point for Greek analysis is :doc:`api/autogen/morphkit.analyse_word_with_morpheus`. Internally it orchestrates the full pipeline:

.. code-block:: text

   Input word in Beta Code
            |
            v
   get_word_blocks()
            |
            v
   split_into_raw_blocks()
            |
            v
   parse_word_block() for each block
            |
            +--> analyse_pos()
            |
            +--> analyse_morph_tag()
            |
            v
   Combined result dictionary

The returned object contains:

- the queried raw form in Beta Code,
- the Unicode form for Greek input,
- the number of analysis blocks found,
- a list of parsed and annotated analyses.

Core Components
---------------

+---------------------------------------------------------------+--------------------------------------------------------------+
| Component                                                     | Responsibility                                               |
+===============================================================+==============================================================+
| :doc:`api/autogen/morphkit.get_word_blocks`                   | Build the Morpheus request URL, perform HTTP I/O, and apply  |
|                                                               | timeout and retry policy.                                    |
+---------------------------------------------------------------+--------------------------------------------------------------+
| :doc:`api/autogen/morphkit.split_into_raw_blocks`             | Separate the raw Morpheus response into one block per parse. |
+---------------------------------------------------------------+--------------------------------------------------------------+
| :doc:`api/autogen/morphkit.parse_word_block`                  | Convert Morpheus block lines into structured Python data.    |
+---------------------------------------------------------------+--------------------------------------------------------------+
| :doc:`api/autogen/morphkit.analyse_pos`                       | Infer a broad part of speech from parse features and codes.  |
+---------------------------------------------------------------+--------------------------------------------------------------+
| :doc:`api/autogen/morphkit.analyse_morph_tag`                 | Convert the parse into an SP-style morphological tag.        |
+---------------------------------------------------------------+--------------------------------------------------------------+
| :doc:`api/autogen/morphkit.decode_tag`                        | Decode SP tags back into feature dictionaries.               |
+---------------------------------------------------------------+--------------------------------------------------------------+
| :doc:`api/autogen/morphkit.compare_tags`                      | Compare two SP tags by weighted grammatical similarity.      |
+---------------------------------------------------------------+--------------------------------------------------------------+
| :doc:`api/autogen/morphkit.annotate_and_sort_analyses`        | Rank and group competing analyses against a reference tag.   |
+---------------------------------------------------------------+--------------------------------------------------------------+
| ``morphkit.config``                                           | Hold global timeout and retry settings for API requests.     |
+---------------------------------------------------------------+--------------------------------------------------------------+

Request Layer
-------------

The request boundary is implemented by :doc:`api/autogen/morphkit.get_word_blocks`.

Important technical details in ``1.0.0``:

- Morpheus is queried over plain HTTP using ``requests``.
- The API path is derived from the selected language (currently Greek or Latin).
- The input word is URL-encoded (in Beta Code) before transmission.
- Retry behavior is centralized through ``morphkit.config``.
- Distinct exceptions are defined for timeout, connection, and generic API failures.

The global configuration object in ``morphkit.config`` exposes:

- ``timeout`` with a default of 30 seconds,
- ``retry_attempts`` with a default of 3,
- ``retry_delay`` with a default of 1 second,
- optional overrides via environment variables such as ``MORPHKIT_TIMEOUT``.

This separation keeps transport concerns out of the parsing and annotation stages.

Parsing Layer
-------------

Morpheus returns analyses as structured line-oriented text. The parser is designed to preserve that information rather than aggressively reinterpret it.

:doc:`api/autogen/morphkit.split_into_raw_blocks` first separates the response at each ``:raw`` marker. Then :doc:`api/autogen/morphkit.parse_word_block` walks through each labeled line and maps it into dictionary fields such as:

- ``raw_bc`` / ``raw_uc``
- ``workw_bc`` / ``workw_uc``
- ``lem_full_bc`` and ``lem_base_bc``
- ``stem_bc`` and ``end_bc``
- grammatical features such as ``case``, ``number``, ``gender``, ``tense``, ``voice``, ``mood``, and ``person``
- Morpheus metadata such as ``stem_codes``, ``end_codes``, ``dialects``, and parse flags

The parser also performs two important normalization tasks:

1. It converts Beta Code to precomposed polytonic Greek Unicode for readability.
2. It preserves multiple values when Morpheus reports ambiguity, for example a form that may be either masculine or feminine.

This means Morphkit keeps the Morpheus output close to its source representation while still making it usable from Python code.

Annotation Layer
----------------

After parsing, Morphkit adds higher-level linguistic interpretation in two steps.

Part-of-Speech Inference
~~~~~~~~~~~~~~~~~~~~~~~~

:doc:`api/autogen/morphkit.analyse_pos` applies a rule-based heuristic over the parse dictionary. The logic checks, in order:

- verb-like features such as tense and mood,
- known Morpheus code mappings,
- indeclinable patterns,
- clitic behavior,
- fallback noun-like inflectional evidence such as case or gender.

This stage intentionally stays morphology-driven. It does **not** use sentence context, so it can identify likely part-of-speech classes but cannot resolve discourse-level ambiguity.

Morphological Tag Generation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:doc:`api/autogen/morphkit.analyse_morph_tag` converts the parse into a compact SP-style tag aligned with the `N1904-TF project <n1904_>`_.

The implementation branches by POS class:

- verbs compose tense, voice, mood, and either person/number or participial case-number-gender,
- nouns, adjectives, and articles compose case-number-gender patterns,
- pronouns receive dedicated handling for person and subtype-sensitive structure,
- indeclinables map to fixed tags such as ``ADV``, ``CONJ``, or ``PREP``.

Dialect markers such as Attic can also be appended when recognized in the Morpheus metadata.

Comparison and Ranking Layer
----------------------------

Morphkit also contains a second architecture branch for comparing or prioritizing alternate analyses.

.. code-block:: text

   SP tag
     |
     v
   decode_tag()
     |
     v
   compare_tags()
     |
     v
   similarity report
     |
     v
   annotate_and_sort_analyses()

This part of the package is especially useful when Morphkit output needs to be aligned with an external annotation source.

:doc:`api/autogen/morphkit.decode_tag` turns compact SP tags back into human-readable grammatical features.

:doc:`api/autogen/morphkit.compare_tags` then:

- decodes both tags,
- compares them feature by feature,
- applies weighted similarity matrices for features such as part of speech, tense, mood, number, case, and gender,
- produces an overall similarity score between ``0.0`` and ``1.0``.

:doc:`api/autogen/morphkit.annotate_and_sort_analyses` uses that similarity score to:

- annotate each candidate analysis,
- group analyses by lemma,
- sort groups and individual analyses against a reference morph tag and lemma.

Data Shape
----------

The central Morphkit data shape is a dictionary containing a list of per-analysis dictionaries.

.. code-block:: python

   {
       "raw_bc": "mo/non",
       "raw_uc": "μόνον",
       "blocks": 2,
       "analyses": [
           {
               "lem_full_bc": "mo/nos",
               "lem_base_bc": "mo/nos",
               "stem_bc": "mon",
               "end_bc": "on",
               "case": "acc",
               "number": "sg",
               "gender": "masc",
               "end_codes": ["os_h_on"],
               "pos": "noun",
               "morph": "N-ASM",
           },
           ...
       ],
   }

That structure is intentionally plain Python data. It makes the package easy to use from scripts, notebooks, or export layers without forcing a separate object model.

Design Characteristics
----------------------

The ``1.0.0`` architecture has a few defining characteristics:

- ``Middleware-first``: Morphkit focuses on integration, normalization, and annotation; it is **not** an implemention of Morpheus.
- ``Research-bound``: some of the translation rules are aligned with the ``N1904-TF`` use case rather than a truely universal morphology interchange standard.
- ``Function-oriented``: the codebase is organized around small modules and explicit processing functions instead of a large class hierarchy.
- ``Loss-minimizing parsing``: Morpheus fields are preserved as directly as possible.
- ``Version-aware documentation``: the docs site publishes architecture information per software release.

Versioning Note
---------------

This page describes how Morphkit ``1.0.0`` works as the packaged, reproducible research snapshot for that environment.

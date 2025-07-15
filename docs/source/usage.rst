Usage
=====

Some example use cases.

Obtain Morpheus Analytic blocks for a Greek word
------------------------------------------------

.. code-block:: python

   # convert unicode greek to betacode
   import beta_code
   bc_word=beta_code.greek_to_beta_code(u'του') 
   api_endpoint="10.0.1.156:1315"
   print(morphkit.get_word_blocks(bc_word,api_endpoint))
   
This will output three Morpheus Analytic blocks (one shown):

.. code-block:: text

   :raw tou

   :workw tou=
   :lem o(
   :prvb 				
   :aug1 				
   :stem tou=			indeclform	
   :suff 				
   :end 	 masc/neut gen sg		indeclform	article

Get the compact analysis results
--------------------------------

.. code-block:: python

   print(morphkit.get_word_blocks(bc_word,api_endpoint,output="compact"))
   
This prints (for the same word as the previous example) the compact notation:

.. code-block:: text

   tou
   <NL>N tou=,o(  masc/neut gen sg		indeclform	article</NL><NL>N tou=,ti/s  gen sg	attic	indeclform	indecl</NL><NL>N tis  gen sg	attic	enclitic indeclform	indef</NL>
   
Perform a full analysis
-----------------------

The following will analyse a word and produce a full dictionary of Morpheus data augmented with a Part of Speech and a morphological tag.

.. code-block:: python

   result=morphkit.analyse_word_with_morpheus("mo/non",api_endpoint)
   
This provides a Python dictionary like below (truncated):

.. code-block:: text

   {'raw_bc': 'mo/non',
    'raw_uc': 'μόνον',
    'blocks': 2,
    'analyses': [{'raw_bc': 'mo/non',
      'raw_uc': 'μόνον',
      'workw_bc': 'mo/non',
      'workw_uc': 'μόνον',
      'lem_full_bc': 'mo/nos',
      'lem_full_uc': 'μόνος',
      'lem_base_bc': 'mo/nos',
      'lem_base_uc': 'μόνος',
      'stem_bc': 'mon',
      'stem_uc': 'μον',
      'stem_codes': ['os_h_on'],
      'end_bc': 'on',
      'end_uc': 'ον',
      'gender': 'masc',
      'case': 'acc',
      'number': 'sg',
      'end_codes': ['os_h_on'],
      'pos': 'noun',
      'morph': 'N-ASM'},
     {'raw_bc': 'mo/non',
      'raw_uc': 'μόνον',
      'workw_bc': 'mo/non',
    ...

Limited Latin support
---------------------

Latin words can be analysed and the results stored in a Python dictionary:

.. code-block:: python

   import pprint as pp
   raw_text=morphkit.get_word_blocks("dico",api_endpoint,language="latin")
   blocks=morphkit.split_into_raw_blocks(raw_text)
   all_parses = []
   for block in blocks:
      raw_beta, parses = morphkit.parse_word_block(block,"latin")
      all_parses.append(parses)
      pp.pprint(parses)

This procudes a dictiorary like:

.. code-block:: text

     [{'end': 'o_',
      'end_codes': ['conj1'],
      'lem_base': 'dico#',
      'lem_full': 'dico#1',
      'lem_homonym': 1,
      'mood': 'indicative',
      'number': 'sg',
      'person': '1',
      'raw': 'dico',
      'stem': 'dic',
      'stem_codes': ['conj1', 'are_vb'],
      'tense': 'present',
      'voice': 'active',
      'workw': 'dico_'}]
    [{'end': 'o_',
      'end_codes': ['conj3'],
      'lem_base': 'dico#',

.. _notebook: https://github.com/tonyjurg/morphkit/blob/main/notebooks/Morphkit_usage_examples.ipynb

To see these examples in action, you can download `this Jupyter Notebook <notebook_>`_.
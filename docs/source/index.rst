
.. image:: _static/logo.png
   :alt: Morphkit logo

Home
----

.. _tf: https://tonyjurg.github.io/N1904addons/
.. _n1904: https://centerblc.github.io/N1904/

Welcome to the documentation for Morphkit, a Python toolkit for processing the output of the Morpheus Morphological analyser. 

This package was created as part of a research project to create a `Text-Fabric dataset <tf_>`_ containing the Morpheus analytical data for each word of the `Nestle1904 <n1904_>`_ Greek New Testament. A number of functions are specificly related to this use case.

Features
--------

- Lightweight and modular morphological toolkit.
- Compatible with Morpheus environments.
- Designed for use with Greek New Testament texts (SP tags).
- Basic support for Latin.

Using this package
------------------

:doc:`install`
   How to install this package in your Python environments

:doc:`usage`
   How to use this package
   

GitHub
------

.. _github-repo: https://github.com/tonyjurg/morphkit
.. _issue-tracker: https://github.com/tonyjurg/morphkit/issues

You can find the project's source code on `GitHub <github-repo_>`_ and report issues or suggestions at the `issue tracker <issue-tracker_>`_.


.. Hidden TOCs

.. toctree::
   :caption: Content
   :maxdepth: 2
   :hidden:

   install
   usage

   
.. toctree::
   :maxdepth: 3
   :caption: Functions
   :hidden:
   
   genindex
   

Summary of functions
--------------------

.. autosummary::
   :toctree: api/autogen
   :recursive:
   :nosignatures:

   morphkit.analyse_pos
   morphkit.analyse_morph_tag
   morphkit.analyse_word_with_morpheus
   morphkit.annotate_and_sort_analyses
   morphkit.compare_tags
   morphkit.decode_tag
   morphkit.get_word_blocks
   morphkit.init_compare_tags
   morphkit.parse_word_block
   morphkit.split_into_raw_blocks


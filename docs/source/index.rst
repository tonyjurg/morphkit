
.. image:: ../images/morphkit.png
   :alt: Morphkit logo

Home
----

.. _tf: https://tonyjurg.github.io/N1904addons/
.. _n1904: https://centerblc.github.io/N1904/

Welcome to the documentation for Morphkit, a Python research tool for processing the output of the Morpheus Morphological analyser.

You are currently reading the ``|docs_label|`` documentation for Morphkit ``|release_version|``. Use the version selector in the sidebar to switch between the stable release, development docs, and older tagged versions.

This package was created as part of a research project to create a `Text-Fabric dataset <tf_>`_ containing the Morpheus analytical data for each word of the `Nestle1904 <n1904_>`_ Greek New Testament. A number of functions are specifically related to this use case.

In ``1.0.0``, Morphkit is best understood as a semantic translation layer between two incompatible morphological systems: the raw Morpheus analyses and the SP / ``N1904-TF`` tagging conventions used in that project. The initial release is therefore tightly bound to the ``N1904-TF`` environment. It is packaged and documented so the research workflow can be reproduced, not because it has already become a fully general standalone package.

Features
--------

- Research-oriented middleware around Morpheus output.
- Translation of Morpheus analyses into SP / ``N1904-TF``-style tags.
- Intended primarily for Nestle1904 Text-Fabric scripts, notebooks, and exports.
- Basic support for Latin within the same architecture.

Using this package
------------------

:doc:`install`
   How to install the reproducible research snapshot

:doc:`usage`
   How to use this tool in its intended research setting

:doc:`architecture`
   How the ``1.0.0`` Morphkit translation layer is structured internally

:doc:`license`
   How code and non-code materials in this repository are licensed
   

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
   architecture
   license
   releases

   
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


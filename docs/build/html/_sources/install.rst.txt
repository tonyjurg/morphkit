Installation
============

Since this not a 'normal package' (yet), you need to import it by adding the relative path to the location where the **directory** /morphkit can be found to the path-search (using `sys.path.insert`). After this, your notebook will be able to load morphkit. 

.. code-block:: python

   import sys
   sys.path.insert(0, "../../morphkit")    # relative to notebook dir
   import morphkit

Dependencies
------------

You also need to have install the `dependencies <https://github.com/tonyjurg/morphkit/blob/main/morphkit/requirements.txt>`_:

- `beta-code-py <https://pypi.org/project/beta-code-py/>`_ (for Beta Code ↔ Unicode conversion)
- `requests <https://pypi.org/project/requests/>`_ (for API calls using HTTP to Morpheus)

Morpheus
--------

Since the purpose of this package it to interface with an Morpheus API endpoint, you need access to such a service. A Morpheus API endpoint can be set up locally, e.g., via the `perseidsproject/morpheus-api Docker image <https://hub.docker.com/r/perseidsproject/morpheus-api>`_.

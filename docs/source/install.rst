Installation
============

Morphkit is packaged as a standard Python project. The current baseline release is ``|release_version|``.

Released Version
----------------

Install the released package with:

.. code-block:: bash

   pip install morphkit==|release_version|

This is the recommended installation method for notebooks, scripts, and reproducible research environments.

Development Checkout
--------------------

If you are working from a git checkout and want the repository version instead of the published release, install the project in editable mode:

.. code-block:: bash

   pip install -e .

Dependencies
------------

The package metadata installs the runtime dependencies automatically. The core dependencies are:

- `beta-code-py <https://pypi.org/project/beta-code-py/>`_ (for Beta Code ↔ Unicode conversion)
- `requests <https://pypi.org/project/requests/>`_ (for API calls using HTTP to Morpheus)

Morpheus
--------

Since the purpose of this package it to interface with an Morpheus API endpoint, you need access to such a service. A Morpheus API endpoint can be set up locally, e.g., via the `perseidsproject/morpheus-api Docker image <https://hub.docker.com/r/perseidsproject/morpheus-api>`_.

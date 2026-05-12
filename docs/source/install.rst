Installation
============

Morphkit ``|release_version|`` is packaged for reproducibility, not as a general-purpose standalone product.

In the initial release, Morphkit functions as a semantic translation layer between Morpheus analyses and the SP / ``N1904-TF`` tagging conventions used in the Nestle1904 Text-Fabric workflow. Much of the behaviour in this release assumes that research context.

Reproducible Release Snapshot
-----------------------------

Install the frozen research snapshot with:

.. code-block:: bash

   pip install morphkit==|release_version|

Use this when you need to recreate the exact Morphkit code state used in notebooks, scripts, or internal data processing runs. The purpose of the ``pip`` package here is reproducibility: it lets collaborators pin the same release and obtain the same Python-level translation logic.

The package is intentionally published as-is:

- for internal and research use,
- for reproducible execution of the ``N1904-TF`` workflow,
- without claiming that the software is already a domain-neutral morphology package.

If you want an isolated environment for that reproducible setup, a typical workflow is:

.. code-block:: bash

   python -m venv .venv
   source .venv/bin/activate
   python -m pip install --upgrade pip
   pip install morphkit==|release_version|

On Windows, use the equivalent activation command for the virtual environment.

Development Checkout
--------------------

If you are working from a git checkout and want the repository version instead of the frozen release snapshot, install the project in editable mode:

.. code-block:: bash

   pip install -e .

This is appropriate when you actively want to develop upon Morphkit for the same research setting, or when you are experimenting with project-specific adjustments that should not be confused with the pinned reproducible release.

Dependencies
------------

The package metadata installs the runtime dependencies automatically. The core dependencies are:

- `beta-code-py <https://pypi.org/project/beta-code-py/>`_ (for Beta Code ↔ Unicode conversion)
- `requests <https://pypi.org/project/requests/>`_ (for API calls using HTTP to Morpheus)

These dependencies capture the Python-side runtime only. They do not, by themselves, reproduce the full research environment or the assumptions of the ``N1904-TF`` pipeline.

Morpheus
--------

Since the purpose of this package is to interface with a Morpheus API endpoint, you need access to such a service. A Morpheus API endpoint can be set up locally, e.g., via the `perseidsproject/morpheus-api Docker image <https://hub.docker.com/r/perseidsproject/morpheus-api>`_.

Installing Morphkit with ``pip`` does not provision Morpheus. It simply provides a stable way to reinstall the same translation layer.

.. _index:

git-recycle-bin
================

git-recycle-bin publishes build outputs to a dedicated git repository
while keeping full traceability back to the source commit. Artifacts
can expire automatically yet can be prolonged or removed using normal
git commands. Discovery of available artifacts is done via git notes.

How to install
--------------

Enter the provided Nix shell and install the package:

.. code-block:: bash

   nix-shell shell.nix --pure
   pip install .

Usage
-----

Run the tool inside your build directory. For command-line help:

.. code-block:: bash

   git_recycle_bin.py --help

Further Examples
----------------

See the ``demos/`` directory for practical usage scenarios.

Motivation
----------

Storing binaries in git offers a simple, auditable artifact repository
without extra infrastructure.

Implementation details
----------------------

Artifacts are stored as commits with a commit-message schema as
outlined in the README. Refspecs control their placement and git notes
provide quick lookup information.

.. toctree::
   :maxdepth: 2
   :caption: Contents:


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

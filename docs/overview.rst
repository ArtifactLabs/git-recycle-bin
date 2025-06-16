Overview
========

What is Git Recycle Bin?
-------------------------

Git Recycle Bin is a command-line tool (`git_recycle_bin.py`) that extends Git's capabilities to efficiently 
manage build artifacts alongside your source code. It provides a Git-native solution for storing, organizing, 
and retrieving binary artifacts while maintaining full traceability to their source code.

Core Problems Solved
---------------------

Traditional Artifact Management Issues
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **Lost Traceability**: Binary artifacts stored in external systems lose connection to their source code
* **No Expiry Mechanism**: Artifacts accumulate indefinitely without automatic cleanup
* **Complex Infrastructure**: Requires additional services, databases, or storage systems
* **Poor Git Integration**: Doesn't leverage existing Git workflows and tooling
* **Build Inefficiency**: No way to avoid redundant builds when artifacts already exist

Git Recycle Bin Solutions
~~~~~~~~~~~~~~~~~~~~~~~~~~

* **Source Traceability**: Every artifact maintains complete metadata linking it to its source commit
* **Git-Native Expiry**: Uses Git's own features to implement automatic expiry and garbage collection
* **Build Avoidance**: Through :git-doc:`git notes <git-notes>` integration, enables skipping expensive builds
  by downloading existing artifacts
* **Simple Adoption**: Leverages Git commands you already know with minimal new concepts
* **No External Dependencies**: Works with any standard Git server without additional infrastructure

Key Concepts
-------------

Git Recycle Bin leverages many Git concepts and :git-doc:`plumbing commands
<gitglossary#Documentation/gitglossary.txt-aiddefplumbingaplumbing>`.
For detailed definitions of Git terminology used below, see the `Git Glossary <https://git-scm.com/docs/gitglossary>`_.

Artifact Repositories
~~~~~~~~~~~~~~~~~~~~~~

Artifacts are stored in separate Git repositories from your source code. This separation provides:

* **Size Management**: Keeps source repositories lightweight
* **Access Control**: Different permissions for source vs. artifacts
* **Retention Policies**: Independent expiry and cleanup strategies
* **Storage Optimization**: Specialized handling for binary content

Orphan Branches
~~~~~~~~~~~~~~~

Each artifact is stored in an :git-book:`orphan branch <Git-Branching-Branches-in-a-Nutshell#_create_new_branch>`
(see also: `orphan <https://git-scm.com/docs/gitglossary#Documentation/gitglossary.txt-aiddeforphanaorphan>`_ in Git
Glossary) with no commit history, using a structured naming convention:

.. code-block:: text

   artifact/expire/{EXPIRY_DATE}/{SOURCE_REPO}@{SOURCE_SHA}/{ARTIFACT_PATH}

This naming scheme encodes:

* **Expiry Information**: When the artifact should be garbage collected
* **Source Traceability**: Which repository and commit produced the artifact
* **Path Context**: Where the artifact originated in the source tree

Latest Tags
~~~~~~~~~~~

For convenience, "latest" :git-doc:`tags <git-tag>` point to the most recent artifact for each branch:

.. code-block:: text

   artifact/latest/{SOURCE_REPO}@{SOURCE_BRANCH}/{ARTIFACT_PATH}

This enables easy discovery of current artifacts without knowing specific :git-doc:`commit SHAs <git-rev-parse>`.

Metadata-Only References
~~~~~~~~~~~~~~~~~~~~~~~~

To avoid downloading large binary trees when only metadata is needed:

.. code-block:: text

   refs/artifact/meta-for-commit/{SOURCE_SHA}/{ARTIFACT_SHA}

These lightweight references allow efficient queries about available artifacts.

Git Notes Integration
~~~~~~~~~~~~~~~~~~~~~

Git Recycle Bin uses :git-doc:`Git notes <git-notes>` to inform source repositories about available
artifacts. Notes are stored in specialized refspecs like:

.. code-block:: text

   refs/notes/artifact/{REMOTE}/{ARTIFACT_NAME}/{COMMIT_SHA}-{STATE}

This enables build systems to:

1. Check if artifacts exist for the current commit
2. Download them instead of rebuilding
3. Dramatically reduce build times

How It Works
------------

Publishing Workflow
~~~~~~~~~~~~~~~~~~~

1. **Metadata Capture**: Automatically collect comprehensive information about the source commit
2. **Orphan Branch Creation**: Create or update the appropriate artifact branch
3. **Artifact Storage**: Copy the artifact to the structured location
4. **Tag Management**: Update latest tags to point to new artifacts
5. **Notes Integration**: Inform the source repository about the new artifact

Retrieval Workflow
~~~~~~~~~~~~~~~~~~

1. **Artifact Discovery**: Query available artifacts by name, path, or commit
2. **Metadata Verification**: Check artifact compatibility and freshness
3. **Selective Download**: Fetch only the needed artifacts without full repository
4. **Build Avoidance**: Skip expensive build steps when artifacts exist

Expiry and Cleanup
~~~~~~~~~~~~~~~~~~

1. **Automatic Expiry**: Expired branches are identified by their naming convention
2. **Git-Native Cleanup**: Standard :git-doc:`git gc <git-gc>` removes expired references and objects
3. **Metadata Cleanup**: Orphaned metadata references are automatically removed
4. **Configurable Retention**: Flexible expiry policies from hours to years

Benefits
--------

Developer Experience
~~~~~~~~~~~~~~~~~~~~

* **Familiar Tooling**: Uses Git commands and concepts you already know
* **Fast Operations**: Efficient artifact discovery and retrieval
* **Clear Traceability**: Always know which code produced which artifact
* **Build Avoidance**: Skip redundant builds automatically

Operations and DevOps
~~~~~~~~~~~~~~~~~~~~~

* **No New Infrastructure**: Works with existing Git servers
* **Automatic Cleanup**: Built-in expiry prevents storage bloat
* **Audit Trail**: Complete history of what was built when and by whom
* **CI/CD Integration**: Natural fit for existing Git-based workflows

Team Collaboration
~~~~~~~~~~~~~~~~~~

* **Shared Artifacts**: Team members can reuse each other's builds
* **Consistent Environments**: Reproduce exact build outputs across machines
* **Distributed Development**: Works with distributed teams and repositories
* **Access Control**: Leverage existing Git permissions and authentication

Use Cases
---------

Documentation Generation
~~~~~~~~~~~~~~~~~~~~~~~~

* Store generated HTML, PDF, or other documentation formats
* Link documentation directly to source code versions
* Enable documentation previews without rebuilding

Compiled Binaries
~~~~~~~~~~~~~~~~~

* Share executables across development team
* Cache compilation results for large codebases
* Distribute release candidates efficiently

Container Images
~~~~~~~~~~~~~~~~

* Store Docker image layers or complete images
* Maintain image history tied to source commits
* Enable image reuse across environments

Test Results and Reports
~~~~~~~~~~~~~~~~~~~~~~~~

* Archive test outputs, coverage reports, and benchmarks
* Link results to exact code versions tested
* Enable historical analysis and regression detection

Deployment Artifacts
~~~~~~~~~~~~~~~~~~~~

* Store deployment packages, configurations, and scripts
* Maintain deployment history with source traceability
* Enable rollbacks to known-good artifacts

Next Steps
----------

* **Installation**: See :doc:`installation` for setup instructions
* **Quick Start**: Follow :doc:`quickstart` for your first artifact
* **Concepts**: Learn more in :doc:`concepts` about the underlying principles
* **Examples**: Explore :doc:`examples/basic-workflow` for common patterns 
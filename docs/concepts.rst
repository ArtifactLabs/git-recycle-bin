Core Concepts
=============

This guide provides a deep understanding of the fundamental concepts that power git-recycle-bin. 
Understanding these concepts will help you use the tool more effectively and troubleshoot issues when 
they arise.

.. note::
   
   This guide uses many Git concepts and terminology. For definitions of Git terms, see the 
   official `Git Glossary <https://git-scm.com/docs/gitglossary>`_.

Artifact Lifecycle
-------------------

Understanding the Lifecycle
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Every artifact in git-recycle-bin follows a predictable lifecycle:

1. **Creation**: Artifact is created from source code at a specific commit
2. **Storage**: Artifact is stored in a structured Git repository 
3. **Discovery**: Artifact can be found and queried by various criteria
4. **Retrieval**: Artifact can be downloaded and used
5. **Expiry**: Artifact automatically expires based on configured policy
6. **Cleanup**: Expired artifacts are removed during garbage collection

.. code-block:: text

   Source Code → Build Process → Artifact Creation → Storage
        ↓              ↑                                ↑
   Git Commit ← Traceability ← Metadata ← Structure Naming
        
   Storage → Discovery → Retrieval → Usage
                         ↓
               Expiry → Garbage Collection

Lifecycle States
~~~~~~~~~~~~~~~~~

**Active State**
   - Artifact is available and not expired
   - Can be discovered via list operations
   - Can be downloaded and used
   - Referenced by both branch and tag

**Expired State**
   - Artifact has passed its expiry date
   - Still physically present but marked for cleanup
   - Can be manually cleaned with the clean command
   - Only referenced by expired branch (tag may point elsewhere)

**Cleaned State**
   - Artifact has been garbage collected
   - No longer physically present in repository
   - All references have been removed
   - Only exists in Git :git-doc:`reflog <git-reflog>` until reflog expires

Branch and Tag Naming Conventions
----------------------------------

|grb| uses a sophisticated naming scheme that encodes essential information directly in Git 
references. Understanding Git 
`branch <https://git-scm.com/docs/gitglossary#Documentation/gitglossary.txt-aiddefbranchbranch>`_ 
and `tag <https://git-scm.com/docs/gitglossary#Documentation/gitglossary.txt-aiddeftagtag>`_ concepts is 
helpful for understanding this structure.

Artifact Branches
~~~~~~~~~~~~~~~~~

**Format:**
``artifact/expire/{EXPIRY_DATE}/{SOURCE_REPO}@{SOURCE_SHA}/{ARTIFACT_PATH}``

**Example:**
``artifact/expire/2024-12-25/14.30+0200/myproject.git@a1b2c3d4e5f6/{dist/webapp}``

**Components:**

- ``artifact/expire/`` - Fixed prefix identifying expiring artifacts
- ``2024-12-25/14.30+0200`` - ISO date and time with timezone offset
- ``myproject.git`` - Source repository name (basename of Git URL)
- ``a1b2c3d4e5f6`` - First 10 characters of :git-doc:`source commit SHA <git-rev-parse>`
- ``{dist/webapp}`` - Artifact path relative to source repository root

**Why This Structure?**

1. **Chronological Sorting**: Dates sort naturally for efficient expiry processing
2. **Source Traceability**: Every artifact knows exactly which code created it
3. **Path Context**: Artifacts maintain their relationship to source structure
4. **Collision Avoidance**: SHA ensures uniqueness even with same dates/paths

Latest Tags
~~~~~~~~~~~

:git-doc:`Tags <git-tag>` (see 
`Git tag <https://git-scm.com/docs/gitglossary#Documentation/gitglossary.txt-aiddeftagtag>`_ 
in Git Glossary) provide convenient access to the most recent artifacts:

**Format:**
``artifact/latest/{SOURCE_REPO}@{SOURCE_BRANCH}/{ARTIFACT_PATH}``

**Example:**
``artifact/latest/myproject.git@main/{dist/webapp}``

**Purpose:**
- Always points to the most recent artifact for a given branch/path combination
- Enables "give me the latest build from main" scenarios
- Automatically updated when new artifacts are pushed
- Provides stable reference that doesn't include commit SHAs

Metadata References
~~~~~~~~~~~~~~~~~~~

**Format:**
``refs/artifact/meta-for-commit/{SOURCE_SHA}/{ARTIFACT_SHA}``

**Example:**
``refs/artifact/meta-for-commit/a1b2c3d4e5f6.../9f8e7d6c5b4a...``

**Purpose:**
- Contains only the commit message (metadata) without the artifact tree
- Enables fast metadata queries without downloading large binaries
- Supports garbage collection of metadata when artifacts are removed
- Links source commits to their artifact commits

Metadata Structure and Usage
-----------------------------

Commit Message Format
~~~~~~~~~~~~~~~~~~~~~

|grb| stores rich metadata in :git-doc:`Git commit <git-commit>` messages (see 
`commit object <https://git-scm.com/docs/gitglossary#Documentation/gitglossary.txt-aiddefcommitobjectcommitobject>`_ 
in Git Glossary) using a structured format:

.. code-block:: text

   Artifact: my-webapp-build

   Built from source commit a1b2c3d4e5f6789... on branch 'main'
   
   artifact-schema-version: 1.0
   artifact-name: my-webapp-build
   artifact-mime-type: application/directory
   artifact-tree-prefix: dist/webapp
   artifact-expire: 2024-12-25/14.30+0200
   src-git-relpath: dist/webapp
   src-git-commit-sha: a1b2c3d4e5f6789...
   src-git-commit-title: Fix user authentication bug
   src-git-branch: main
   src-git-repo-url: git@github.com:company/myproject.git
   src-git-repo: myproject.git
   src-time-author: 2024-01-15 10:30:00 +0200
   src-time-commit: 2024-01-15 10:30:00 +0200
   src-status-clean: true
   build-host: ci-runner-01.company.com
   build-user: ci-user
   build-env-vars: NODE_ENV=production,BUILD_NUMBER=123

Key Metadata Fields
~~~~~~~~~~~~~~~~~~~

**Core Identification:**
- ``artifact-name``: Human-readable name for discovery
- ``artifact-mime-type``: Type of artifact (file, directory, symlink)
- ``artifact-tree-prefix``: Path within artifact repository

**Source Traceability:**
- ``src-git-commit-sha``: Exact source commit that created this artifact
- ``src-git-branch``: Source branch at time of creation
- ``src-git-repo-url``: Complete source repository URL
- ``src-time-author``: When the source commit was originally created
- ``src-time-commit``: When the source commit was last modified

**Build Context:**
- ``build-host``: Machine that created the artifact
- ``build-user``: User account that ran the build
- ``src-status-clean``: Whether :git-book:`working directory <Git-Basics-Recording-Changes-to-the-Repository>` was clean
- ``build-env-vars``: Relevant environment variables

**Lifecycle Management:**
- ``artifact-expire``: When this artifact should be cleaned up
- ``artifact-schema-version``: Format version for compatibility

Git Notes Integration
---------------------

Purpose and Benefits
~~~~~~~~~~~~~~~~~~~~

Git notes provide a way for artifact repositories to communicate back to source repositories without 
modifying the source commit history. This creates **bidirectional traceability** between source code and 
artifacts, enabling powerful workflows that traditional artifact management systems cannot provide.

:git-doc:`Git notes <git-notes>` enable:

- **🔍 Build Avoidance**: Check if artifacts exist before building
- **📊 Artifact Discovery**: Find all artifacts created from a commit
- **📝 Audit Trail**: Track what was built when and where
- **🤝 Distributed Coordination**: Multiple build systems can see each other's work
- **🔄 Bidirectional Linking**: Navigate from source commits to artifacts and back

**How Bidirectional Traceability Works:**

.. code-block:: text

   Source Repository          Artifact Repository
   ┌─────────────────┐       ┌──────────────────┐
   │ Commit abc123   │◄──────┤ Artifact Build   │
   │                 │       │ (contains        │
   │ + git notes ────┼──────►│  abc123 SHA)     │
   │   refs/notes/   │       │                  │
   │   artifact/*    │       └──────────────────┘
   └─────────────────┘

1. **Forward Traceability**: Every artifact stores the source :git-doc:`commit SHA <git-rev-parse>` in its metadata
2. **Reverse Traceability**: :git-doc:`Git notes <git-notes>` in the source repo point to available artifacts
3. **Distributed Discovery**: Any developer can query git notes to find existing artifacts

Notes Structure
~~~~~~~~~~~~~~~

**Note Refspec:**
``refs/notes/artifact/{REMOTE_ID}/{ARTIFACT_NAME}/{COMMIT_SHA}-{STATE}``

**Example:**
``refs/notes/artifact/artifacts.company.com%2Fmyproject.git/webapp-build/a1b2c3d4e5f6-clean``

**Components:**
- ``artifacts.company.com%2Fmyproject.git`` - URL-encoded artifact repository
- ``webapp-build`` - Artifact name (URL-encoded)
- ``a1b2c3d4e5f6`` - Artifact commit SHA
- ``clean`` - State of :git-book:`working directory <Git-Basics-Recording-Changes-to-the-Repository>` when built

**Note Content:**
JSON format with essential artifact information:

.. code-block:: json

   {
     "date": "2024-01-15/14.30+0200",
     "name": "webapp-build",
     "user": "ci-user",
     "host": "ci-runner-01",
     "expire": "2024-12-25/14.30+0200",
     "remote": "git@artifacts.company.com:myproject.git",
     "commit": "9f8e7d6c5b4a3e2d1c0b9a8f7e6d5c4b"
   }

Working with Notes
~~~~~~~~~~~~~~~~~~

**Fetching Notes:**

.. code-block:: bash

   # Fetch all artifact notes
   git fetch origin 'refs/notes/artifact/*:refs/notes/artifact/*'
   
   # Fetch notes for specific remote
   git fetch origin 'refs/notes/artifact/artifacts.company.com*:refs/notes/artifact/artifacts.company.com*'

**Querying Notes:**

.. code-block:: bash

   # List all notes for current commit
   GIT_NOTES_REF=refs/notes/artifact/artifacts.company.com%2Fmyproject.git/webapp-build/a1b2c3d4e5f6-clean \
       git notes list HEAD
   
   # Show note content
   GIT_NOTES_REF=refs/notes/artifact/artifacts.company.com%2Fmyproject.git/webapp-build/a1b2c3d4e5f6-clean \
       git notes show HEAD

For more information on working with git notes, see the :git-doc:`git-notes <git-notes>` documentation.

**Build Avoidance Pattern:**

.. code-block:: bash

   # Check if artifact exists for current commit
   current_sha=$(git rev-parse HEAD)
   note_ref="refs/notes/artifact/artifacts.company.com%2Fmyproject.git/webapp-build/${current_sha}-clean"
   
   if git show-ref --quiet "$note_ref"; then
       echo "Artifact exists, downloading..."
       # Extract artifact commit from note and download
   else
       echo "No artifact found, building..."
       # Run build process
   fi

Expiry and Garbage Collection
-----------------------------

Expiry Policies
~~~~~~~~~~~~~~~

**Time-Based Expiry:**

Common expiry patterns:

.. code-block:: bash

   # Relative dates
   --expire "1 week"       # 7 days from now
   --expire "2 months"     # 60 days from now
   --expire "1 year"       # 365 days from now
   
   # Absolute dates
   --expire "2024-12-31"           # Specific date
   --expire "2024-12-31 23:59"     # Date with time
   --expire "2024-12-31 23:59 EST" # Date with timezone
   
   # Natural language
   --expire "in 30 days"
   --expire "next month"

**Expiry Date Encoding:**

Expiry dates are encoded in ISO format with timezone:
- ``2024-12-31/23.59+0000`` - December 31st, 2024 at 23:59 UTC
- ``2024-06-15/14.30-0500`` - June 15th, 2024 at 14:30 EST
- ``2025-01-01/00.00+0200`` - January 1st, 2025 at midnight CET

Garbage Collection Process
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Automatic Expiry Detection:**

|grb| identifies expired artifacts by:

1. **Parsing Branch Names**: Extract expiry dates from branch names
2. **Time Comparison**: Compare expiry dates to current time
3. **Timezone Handling**: Properly handle timezone offsets
4. **Grace Period**: Optional grace period before actual deletion

**Cleanup Process:**

.. code-block:: bash

   # Manual cleanup
   git_recycle_bin.py clean REPOSITORY

**What Gets Cleaned:**

1. **Expired Branches**: ``artifact/expire/...`` branches past their expiry date
2. **Orphaned Metadata**: Metadata refs for artifacts that no longer exist
3. **Unreferenced Objects**: Git objects no longer referenced by any branch/tag
4. **Note References**: :git-doc:`Git notes <git-notes>` for cleaned artifacts

**What Doesn't Get Cleaned:**

1. **Latest Tags**: These may point to non-expired artifacts
2. **Non-Expired Branches**: Even if they're old, they stay until expired
3. **Source Repository Notes**: Git notes in source repos are independent

Recovery and Safety
~~~~~~~~~~~~~~~~~~~

**Recovery Window:**

Even after cleanup, artifacts may be recoverable:

.. code-block:: bash

   # Git keeps objects in reflog for ~30 days by default
   git reflog --all | grep "artifact/expire"
   
   # Recover a specific artifact branch
   git update-ref refs/heads/artifact/expire/... SHA_FROM_REFLOG

**Safety Measures:**

1. **Dry Run Support**: Preview what would be cleaned
2. **Incremental Cleanup**: Clean one artifact at a time
3. **Logging**: Detailed logs of what was cleaned
4. **Backup Integration**: Can be integrated with repository backup systems

Advanced Concepts
-----------------

Path Normalization
~~~~~~~~~~~~~~~~~~

|grb| normalizes paths to ensure consistency:

.. code-block:: bash

   # These all result in the same artifact path
   --path ./dist/webapp
   --path dist/webapp
   --path dist/webapp/
   
   # Results in artifact path: dist/webapp

**Normalization Rules:**
1. Remove leading ``./``
2. Remove trailing ``/`` 
3. Resolve ``..`` and ``.`` components
4. Use forward slashes consistently
5. Store relative to source repository root

Repository Relationships
~~~~~~~~~~~~~~~~~~~~~~~~

Understanding Git 
`repository <https://git-scm.com/docs/gitglossary#Documentation/gitglossary.txt-aiddefrepositoryrepository>`_ 
concepts is essential for effective artifact management.

**Source Repository:**
- Contains your application code
- Where you run git-recycle-bin commands
- Receives :git-doc:`git notes <git-notes>` about available artifacts
- Never contains the actual artifacts

**Artifact Repository:**
- Contains only artifacts and metadata
- Can be completely separate from source
- May be shared across multiple source repositories
- Optimized for binary storage and expiry

**Multiple Artifact Repositories:**

You can use different repositories for different types of artifacts:

.. code-block:: bash

   # Documentation artifacts
   git_recycle_bin.py push git@docs.company.com:artifacts.git \
       --path ./docs/_build --name "api-docs"
   
   # Binary artifacts  
   git_recycle_bin.py push git@binaries.company.com:artifacts.git \
       --path ./dist/bin --name "webapp"
   
   # Container images
   git_recycle_bin.py push git@containers.company.com:artifacts.git \
       --path ./docker-context --name "webapp-image"

Conflict Resolution
~~~~~~~~~~~~~~~~~~~

**Concurrent Builds:**

When multiple builds happen simultaneously:

1. **Idempotent Operations**: Same input produces same artifact SHA
2. **Branch Conflicts**: Later push wins (branches are updated atomically)
3. **Tag Conflicts**: Latest tag always points to most recent artifact
4. **Note Conflicts**: Git notes merge with ``cat_sort_uniq`` strategy

Performance Considerations
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Large Artifacts:**
- Git handles large files reasonably well
- Consider Git LFS integration for very large binaries
- Artifact repositories can use shallow clones

**Many Artifacts:**
- Branch/tag operations scale well
- Use specific artifact name filters when listing
- Consider separate repositories for different artifact types

**Network Efficiency:**
- Only changed objects are transferred
- Metadata-only refs enable fast queries
- Sparse checkout can limit what's downloaded

Understanding these concepts will help you design effective artifact management strategies and troubleshoot 
issues when they arise. The next step is to see these concepts in action through practical examples. 
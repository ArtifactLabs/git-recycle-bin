Quick Start Guide
==================

This guide will get you up and running with git-recycle-bin in just a few minutes, walking you through 
your first artifact storage and retrieval workflow.

Prerequisites Check
-------------------

Before starting, ensure you have:

1. **git-recycle-bin installed** (see :doc:`installation`)
2. **A Git repository** to work with
3. **Some files to use as artifacts** (we'll create test files if needed)

Let's verify your installation:

.. code-block:: bash

   # Check that git-recycle-bin is available
   git_recycle_bin.py --help

You should see the help output without errors.

Your First Artifact
--------------------

Step 1: Set Up a Test Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's create a simple test scenario:

.. code-block:: bash

   # Create a test directory (if you don't have an existing Git repo)
   mkdir git-recycle-test
   cd git-recycle-test
   
   # Initialize as a Git repository
   git init
   git config user.name "Your Name"
   git config user.email "your.email@example.com"
   
   # Create some initial content
   echo "# Test Project" > README.md
   git add README.md
   git commit -m "Initial commit"

Step 2: Create Some Artifacts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now let's create some files that we'll treat as build artifacts:

.. code-block:: bash

   # Create a build directory with some "artifacts"
   mkdir -p build
   echo "Built application v1.0" > build/app.txt
   echo "Documentation generated" > build/docs.html
   echo "Configuration file" > build/config.json
   
   # Let's see what we have
   ls -la build/

Step 3: Push Your First Artifact
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now we'll push the build directory as an artifact. For this example, we'll use a local artifact repository:

.. code-block:: bash

   # Push the build directory as an artifact
   git_recycle_bin.py push . \
       --path build \
       --name "my-first-artifact" \
       --expire "1 week"

Let's break down this command:

* ``push`` - The command to upload an artifact
* ``.`` - Use the current directory as the artifact repository (for testing)
* ``--path build`` - The directory/file to store as an artifact
* ``--name "my-first-artifact"`` - A human-readable name for the artifact
* ``--expire "1 week"`` - The artifact will expire in one week

**Expected Output:**

.. code-block:: text

   Adding 'build' as 'build' ...
   Artifact commit: abc123def456...
   Artifact branch: artifact/expire/2024-01-15/14.30+0000/git-recycle-test.git@def789.../build
   Artifact tag: artifact/latest/git-recycle-test.git@master/build
   Artifact [meta data]-only ref: refs/artifact/meta-for-commit/def789.../abc123...
   Artifact [meta data]-only obj: 456789abc...

The artifact is now stored with full metadata and will automatically expire on the specified date, 
demonstrating the core capabilities of git-recycle-bin.

Step 4: List Available Artifacts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now let's see what artifacts are available:

.. code-block:: bash

   # List all artifacts in the repository
   git_recycle_bin.py list .

**Expected Output:**

.. code-block:: text

   my-first-artifact
   expire: 2024-01-15/14.30+0000
   commit: abc123def456...
   path: build

You can also filter by name:

.. code-block:: bash

   # List artifacts matching a specific name
   git_recycle_bin.py list . --name "my-first-artifact"

Step 5: Download an Artifact
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's simulate needing to download the artifact (maybe for build avoidance):

.. code-block:: bash

   # First, let's remove our local build directory
   rm -rf build
   ls  # Notice build is gone
   
   # First get the artifact SHA from the list output
   # Then download using the SHA (from previous list command output)
   git_recycle_bin.py download . abc123def456

   # Check that our files are back
   ls -la build/

**Note:** The actual SHA will be shown in the list command output. Replace `abc123def456` with the real SHA.

**Expected Output:**

.. code-block:: text

   Downloading artifact abc123def456...
   Downloaded: build/app.txt
   Downloaded: build/docs.html  
   Downloaded: build/config.json

Understanding the Output
------------------------

Branch and Tag Names
~~~~~~~~~~~~~~~~~~~~

|grb| creates structured names for branches and tags:

**Artifact Branch:**
``artifact/expire/2024-01-15/14.30+0000/git-recycle-test.git@def789.../build``

This encodes:
- ``artifact/expire/`` - Prefix indicating this is an expiring artifact
- ``2024-01-15/14.30+0000`` - Expiry date and time with timezone
- ``git-recycle-test.git@def789...`` - Source repository and commit SHA
- ``build`` - The path of the artifact within the source

**Latest Tag:**
``artifact/latest/git-recycle-test.git@master/build``

This provides:
- ``artifact/latest/`` - Prefix for latest artifacts
- ``git-recycle-test.git@master`` - Source repository and branch
- ``build`` - The artifact path

Metadata References
~~~~~~~~~~~~~~~~~~~

The tool also creates lightweight metadata references:
- ``refs/artifact/meta-for-commit/...`` - Contains just the commit message metadata
- This allows querying artifact info without downloading the full artifact tree

Working with Remote Repositories
---------------------------------

Real-World Example
~~~~~~~~~~~~~~~~~~

In practice, you'll typically use a remote repository for artifacts:

.. code-block:: bash

   # Push to a remote artifact repository
   git_recycle_bin.py push git@artifacts.example.com:myproject.git \
       --path ./dist \
       --name "webapp-build" \
       --expire "1 month"
   
   # List artifacts from the remote
   git_recycle_bin.py list git@artifacts.example.com:myproject.git
   
   # Download from the remote
   git_recycle_bin.py download git@artifacts.example.com:myproject.git \
       --name "webapp-build" \
       --output ./dist

Build Avoidance Example
~~~~~~~~~~~~~~~~~~~~~~~

Here's how you might use this in a build script:

.. code-block:: bash

   #!/bin/bash
   
   ARTIFACT_REPO="git@artifacts.example.com:myproject.git"
   ARTIFACT_NAME="webapp-build"
   
   # Check if artifact already exists for current commit
   if git_recycle_bin.py list "$ARTIFACT_REPO" --name "$ARTIFACT_NAME" | grep -q .; then
       echo "Artifact found! Downloading instead of building..."
       git_recycle_bin.py download "$ARTIFACT_REPO" \
           --name "$ARTIFACT_NAME" \
           --output ./dist
       echo "Build skipped - using existing artifact"
   else
       echo "No artifact found. Building..."
       npm run build  # or your build command
       git_recycle_bin.py push "$ARTIFACT_REPO" \
           --path ./dist \
           --name "$ARTIFACT_NAME" \
           --expire "1 month"
       echo "Build complete and artifact stored"
   fi

Common Gotchas for Beginners
----------------------------

1. **Forgetting the Path**

   .. code-block:: bash
   
      # Wrong - no --path specified
      git_recycle_bin.py push . --name "myapp"
      
      # Correct - specify what to push
      git_recycle_bin.py push . --path ./build --name "myapp"

2. **Using Relative Paths**

   |grb| handles path normalization, but be consistent:

   .. code-block:: bash
   
      # Both work, but pick one style
      git_recycle_bin.py push . --path ./build --name "myapp"
      git_recycle_bin.py push . --path build --name "myapp"

3. **Expiry Format Confusion**

   .. code-block:: bash
   
      # These all work:
      --expire "1 week"
      --expire "2 months"
      --expire "2024-12-31"
      --expire "in 30 days"
      
      # This doesn't work:
      --expire "next Tuesday"  # Too vague

4. **Repository Path Issues**

   .. code-block:: bash
   
      # For local testing, use current directory
      git_recycle_bin.py push . --path build --name test
      
      # For real use, specify full repository URL
      git_recycle_bin.py push git@host:repo.git --path build --name prod

5. **Forgetting Git Identity**

   If you see errors about Git user configuration:

   .. code-block:: bash
   
      git config --global user.name "Your Name"
      git config --global user.email "your.email@example.com"
      
      # Or set per-command
      git_recycle_bin.py push . --path build --name test \
          --user-name "Your Name" --user-email "your.email@example.com"

Cleanup and Maintenance
-----------------------

Cleaning Expired Artifacts
~~~~~~~~~~~~~~~~~~~~~~~~~~~

To remove expired artifacts:

.. code-block:: bash

   # Clean up expired artifacts (this runs garbage collection)
   git_recycle_bin.py clean .

Checking What Will Be Cleaned
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To see what would be cleaned without actually doing it:

.. code-block:: bash

   # List expired artifacts
   git_recycle_bin.py list . --expired

Next Steps
----------

Now that you've successfully pushed, listed, and downloaded your first artifact, you can:

1. **Explore Advanced Features**: Learn about custom expiry formats, :git-doc:`git notes <git-notes>` 
   integration, and metadata handling

2. **Integrate with Your Build System**: See how to add artifact management to your existing build process

3. **Real-World Examples**: Follow complete workflows in :doc:`examples/basic-workflow`

4. **Command Reference**: Get detailed information about all available options

5. **Understand the Concepts**: Dive deeper into how |grb| works in :doc:`concepts`

Troubleshooting
---------------

**Command Not Found:**

.. code-block:: bash

   # Make sure it's installed correctly
   which git_recycle_bin.py
   pip list | grep git-recycle-bin

**Permission Errors:**

.. code-block:: bash

   # Check Git configuration
   git config --list | grep user
   
   # Or specify user explicitly
   git_recycle_bin.py push . --path build --name test \
       --user-name "Name" --user-email "email@example.com"

**Repository Access Issues:**

.. code-block:: bash

   # Test Git access first
   git ls-remote git@host:repo.git
   
   # Use HTTPS if SSH doesn't work
   git_recycle_bin.py push https://github.com/user/artifacts.git \
       --path build --name test

**Getting Help:**

If you run into issues:

1. Run commands with increased verbosity: ``git_recycle_bin.py --debug ...``
2. Check the troubleshooting guide
3. Search or create an issue on `GitHub Issues <https://github.com/ArtifactLabs/git-recycle-bin/issues>`_

You've successfully completed your first git-recycle-bin workflow! You can now store, retrieve, and manage 
build artifacts with automatic expiry and full source traceability. 
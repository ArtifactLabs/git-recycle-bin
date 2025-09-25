Basic Operations
================

This guide covers the fundamental operations you'll use with git-recycle-bin on a daily basis. All 
commands follow a consistent pattern and provide comprehensive help when needed.

Command Syntax
--------------

Global Command Structure
~~~~~~~~~~~~~~~~~~~~~~~~~

All git-recycle-bin commands follow this general pattern:

.. code-block:: bash

   git_recycle_bin.py <command> <remote_url> [options]

**Components:**
- ``<command>`` - What to do: push, list, download, clean
- ``<remote_url>`` - Git remote URL where artifacts are stored
- ``[options]`` - Operation-specific flags and values

**Common Options:**
- ``--help`` - Show detailed help for any command
- ``--verbose`` - Enable detailed output for debugging (can be repeated: -vv)
- ``--quiet`` - Suppress output
- ``--color`` - Enable colorized output (default: True)

**Environment Variables:**
You can set defaults using environment variables:

- ``GITRB_USERNAME`` - Default author name for artifact commits
- ``GITRB_EMAIL`` - Default author email for artifact commits  
- ``GITRB_SRC_REMOTE`` - Default source remote name (default: origin)
- ``GITRB_RM_TMP`` - Remove temporary repositories (default: True)
- ``GITRB_COLOR`` - Enable colorized output (default: True)
- ``GITRB_PATH`` - Default artifact path
- ``GITRB_NAME`` - Default artifact name
- ``GITRB_EXPIRE`` - Default expiry date (default: "in 30 days")
- ``GITRB_PUSH_TAG`` - Push tags to remote (default: False)
- ``GITRB_PUSH_NOTE`` - Push notes to source remote (default: False)

Getting Help
~~~~~~~~~~~~

.. code-block:: bash

   # General help
   git_recycle_bin.py --help
   
   # Help for specific operations
   git_recycle_bin.py push --help
   git_recycle_bin.py list --help
   git_recycle_bin.py download --help
   git_recycle_bin.py clean --help

Repository Specification
~~~~~~~~~~~~~~~~~~~~~~~~~

The repository parameter can be specified in several ways:

.. code-block:: bash

   # Current directory (if it's a Git repository)
   git_recycle_bin.py list .
   
   # Local path to another repository
   git_recycle_bin.py list /path/to/artifacts.git
   
   # Remote repository URL
   git_recycle_bin.py list git@artifacts.company.com:myproject.git
   git_recycle_bin.py list https://github.com/company/artifacts.git
   
   # SSH with custom port
   git_recycle_bin.py list ssh://git@server.com:2222/artifacts.git

Push Operations
---------------

Basic Push Syntax
~~~~~~~~~~~~~~~~~~

The push operation stores artifacts in the artifact repository:

.. code-block:: bash

   git_recycle_bin.py push <repository> --path <artifact_path> --name <artifact_name> [options]

**Required Parameters:**
- ``<repository>`` - Target artifact repository
- ``--path`` - Path to artifact within current repository
- ``--name`` - Human-readable name for the artifact

**Common Options:**
- ``--expire`` - When artifact should be cleaned up
- ``--meta-branch`` - Custom branch name for metadata

Simple Push Examples
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Push a build directory
   git_recycle_bin.py push . --path dist --name "webapp-build"
   
   # Push with expiry
   git_recycle_bin.py push . --path dist --name "webapp-build" --expire "1 week"
   
   # Push to remote repository
   git_recycle_bin.py push git@artifacts.company.com:myproject.git \
       --path dist --name "webapp-build" --expire "30 days"
   
   # Push a single file
   git_recycle_bin.py push . --path docs/manual.pdf --name "user-manual"

Advanced Push Options
~~~~~~~~~~~~~~~~~~~~~

**Custom Expiry Dates:**

.. code-block:: bash

   # Relative dates
   --expire "1 week"
   --expire "2 months"
   --expire "1 year"
   
   # Absolute dates
   --expire "2024-12-31"
   --expire "2024-12-31 23:59"
   --expire "2024-12-31 23:59 EST"
   
   # Natural language
   --expire "in 30 days"
   --expire "next Friday"

**Custom Metadata Branch:**

.. code-block:: bash

   # Use custom branch for metadata (useful for CI/CD)
   git_recycle_bin.py push . --path dist --name "webapp" \
       --meta-branch "refs/artifact/meta-for-commit/special-branch"

**Handling Different Artifact Types:**

.. code-block:: bash

   # Directory artifacts
   git_recycle_bin.py push . --path build/webapp --name "webapp-dist"
   
   # File artifacts
   git_recycle_bin.py push . --path target/app.jar --name "java-app"
   
   # Documentation
   git_recycle_bin.py push . --path docs/_build/html --name "api-docs"
   
   # Container contexts
   git_recycle_bin.py push . --path docker --name "webapp-image"

Understanding Push Output
~~~~~~~~~~~~~~~~~~~~~~~~~

When you push an artifact, you'll see output like this:

.. code-block:: text

   Pushing artifact 'webapp-build' from path 'dist'...
   Source commit: a1b2c3d4e5f6789... (Fix authentication bug)
   Artifact commit: 9f8e7d6c5b4a3e2d1c0b9a8f7e6d5c4b
   
   Created references:
   - Branch: artifact/expire/2024-12-25/14.30+0200/myproject.git@a1b2c3d4/{dist}
   - Tag: artifact/latest/myproject.git@main/{dist}
   - Metadata: refs/artifact/meta-for-commit/a1b2c3d4e5f6/9f8e7d6c5b4a
   
   Artifact will expire: 2024-12-25 14:30 +0200

**Key Information:**
- **Source commit**: The commit in your source repository that created this artifact
- **Artifact commit**: The commit in the artifact repository containing your artifact
- **Branch**: Time-based reference that will be cleaned up automatically
- **Tag**: Latest reference that gets updated with each new push
- **Expiry**: When this artifact will be eligible for cleanup

List Operations
---------------

Basic List Syntax
~~~~~~~~~~~~~~~~~~

The `list` operation prints the SHAs of available artifacts for the current source commit (`HEAD`), one SHA per line.

.. code-block:: bash

   git_recycle_bin.py list <repository> [options]

**Options:**
- ``--name <string>`` - Filter artifacts by their given name.
- ``--path <file|dir>`` - Filter artifacts by their original source path.

Simple List Examples
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # List all artifact SHAs for the current commit
   git_recycle_bin.py list .

   # List artifact SHAs from a remote repository
   git_recycle_bin.py list git@artifacts.company.com:myproject.git

   # List SHAs for artifacts with a specific name
   git_recycle_bin.py list . --name "webapp-build"

Understanding List Output
~~~~~~~~~~~~~~~~~~~~~~~~~

The command outputs a list of artifact commit SHAs, one per line. This format is designed to be easily piped into other commands.

.. code-block:: text

   9f8e7d6c5b4a3e2d1c0b9a8f7e6d5c4b
   a1b2c3d4e5f678901234567890abcdefabcde

This output can be used directly with `git_recycle_bin.py download` or other command-line tools like `xargs`, `head`, or `sed`.

Download Operations
-------------------

Basic Download Syntax
~~~~~~~~~~~~~~~~~~~~~~

The download operation retrieves one or more artifacts from the repository.

.. code-block:: bash

   git_recycle_bin.py download <repository> <artifact_sha>...

**Required Parameters:**
- ``<repository>`` - The artifact repository URL (or `.` for local).
- ``<artifact_sha>`` - One or more artifact SHAs to download.

**Common Options:**
- ``--force`` - Overwrite existing local files.

Simple Download Examples
~~~~~~~~~~~~~~~~~~~~~~~~

The typical workflow is to use `list` to find the artifact SHA and then pipe it to `download`.

.. code-block:: bash

   # 1. Find the SHA of the artifact you want
   git_recycle_bin.py list . --name "webapp-build"

   # 2. Download it (replace <artifact_sha> with the actual SHA from the output)
   git_recycle_bin.py download . <artifact_sha>

   # Or, more powerfully, pipe the commands together to get the latest artifact
   git_recycle_bin.py list . --name "webapp-build" | head -n 1 | xargs git_recycle_bin.py download .

   # Force the download to overwrite local files
   git_recycle_bin.py list . --name "webapp-build" | head -n 1 | xargs git_recycle_bin.py download . --force


Understanding Download Output
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The tool will check out the files from the artifact commit into your current working directory.

.. code-block:: text

   Downloading artifact '9f8e7d6c5b4a'...

After the command completes, the artifact's files will be present in your local filesystem.


Common Patterns
---------------

Development Workflow
~~~~~~~~~~~~~~~~~~~~

**Typical development cycle:**

.. code-block:: bash

   # 1. Build your application
   npm run build
   
   # 2. Push build artifacts
   git_recycle_bin.py push . --path dist --name "webapp-build" --expire "1 week"
   
   # 3. Later, on another machine or CI, get the latest artifact
   LATEST_SHA=$(git_recycle_bin.py list . --name "webapp-build" | head -n 1)
   git_recycle_bin.py download . "$LATEST_SHA"

CI/CD Integration
~~~~~~~~~~~~~~~~~

**Build stage (push artifacts):**

.. code-block:: bash

   #!/bin/bash
   # ci-build.sh
   
   # Build the application
   npm ci
   npm run build
   
   # Push artifacts
   git_recycle_bin.py push git@artifacts.company.com:myproject.git \
       --path dist \
       --name "webapp-build-${BUILD_NUMBER}" \
       --expire "30 days"

**Deploy stage (download artifacts):**

.. code-block:: bash

   #!/bin/bash
   # ci-deploy.sh
   
   # Find and download the latest artifact for a specific build number
   ARTIFACT_SHA=$(git_recycle_bin.py list git@artifacts.company.com:myproject.git --name "webapp-build-${BUILD_NUMBER}" | head -n 1)

   if [ -n "$ARTIFACT_SHA" ]; then
       git_recycle_bin.py download git@artifacts.company.com:myproject.git "$ARTIFACT_SHA"
   else
       echo "Error: Artifact for build ${BUILD_NUMBER} not found!"
       exit 1
   fi

Cross-Repository Sharing
~~~~~~~~~~~~~~~~~~~~~~~~

**Shared artifact repository pattern:**

.. code-block:: bash

   # Team A pushes documentation
   git_recycle_bin.py push git@artifacts.company.com:shared.git \
       --path docs/_build --name "api-docs" --expire "2 weeks"
   
   # Team B finds and downloads the latest documentation artifact
   API_DOCS_SHA=$(git_recycle_bin.py list git@artifacts.company.com:shared.git --name "api-docs" | head -n 1)
   git_recycle_bin.py download git@artifacts.company.com:shared.git "$API_DOCS_SHA"

Multi-Environment Artifacts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Environment-specific naming:**

.. code-block:: bash

   # Development builds
   git_recycle_bin.py push . --path dist \
       --name "webapp-dev" --expire "3 days"
   
   # Staging builds  
   git_recycle_bin.py push . --path dist \
       --name "webapp-staging" --expire "1 week"
   
   # Production builds
   git_recycle_bin.py push . --path dist \
       --name "webapp-prod" --expire "3 months"

**Environment-specific repositories:**

.. code-block:: bash

   # Push to development artifact repo
   git_recycle_bin.py push git@dev-artifacts.company.com:myproject.git \
       --path dist --name "webapp"
   
   # Push to production artifact repo
   git_recycle_bin.py push git@prod-artifacts.company.com:myproject.git \
       --path dist --name "webapp"

Error Handling
--------------

Common Error Scenarios
~~~~~~~~~~~~~~~~~~~~~~

**Path doesn't exist:**

.. code-block:: text

   Error: Path 'dist' does not exist in the repository

**Solution:** Check that your build process completed and the path exists.

**Repository access denied:**

.. code-block:: text

   Error: Permission denied (publickey)

**Solution:** Verify SSH keys and repository access permissions.

**Artifact not found:**

.. code-block:: text

   Error: No artifact found with name 'webapp-build'

**Solution:** Use ``list`` command to see available artifacts.

**Output directory already exists:**

.. code-block:: text

   Error: Output directory './dist' already exists

**Solution:** Use ``--force`` flag or choose different output location.

Debugging Commands
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Enable verbose output
   git_recycle_bin.py --verbose list .
   
   # Check repository connectivity
   git_recycle_bin.py list . --verbose
   
   # Verify repository access
   git ls-remote git@artifacts.company.com:myproject.git

Clean Operations
----------------

The clean command removes expired artifacts from the artifact repository.

Basic Clean Syntax
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   git_recycle_bin.py clean <remote_url>

**Components:**
- ``clean`` - The command to clean expired artifacts
- ``<remote_url>`` - Git remote URL of artifact repository to clean

Simple Clean Examples
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Clean expired artifacts from local repository
   git_recycle_bin.py clean .
   
   # Clean expired artifacts from remote repository
   git_recycle_bin.py clean git@artifacts.company.com:myproject.git

**Expected Output:**

.. code-block:: text

   Cleaning expired artifacts...
   Removed expired branch: artifact/expire/2024-01-15/project@abc123/build
   Removed expired branch: artifact/expire/2024-01-16/project@def456/docs
   Cleaned 2 expired artifacts

**Understanding Clean Behavior:**
- Only removes artifacts past their expiry date
- Does not affect artifacts that haven't expired yet
- Removes both branches and associated metadata
- Uses Git's native garbage collection

These basic operations form the foundation of working with git-recycle-bin. Once you're comfortable 
with these patterns, you can explore the advanced features for more complex workflows. 
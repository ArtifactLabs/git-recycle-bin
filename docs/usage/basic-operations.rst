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

   git_recycle_bin.py <operation> <repository> [options]

**Components:**
- ``<operation>`` - What to do: push, list, download, clean
- ``<repository>`` - Where artifacts are stored (can be `.` for current directory)
- ``[options]`` - Operation-specific flags and values

**Common Options:**
- ``--help`` - Show detailed help for any command
- ``--verbose`` - Enable detailed output for debugging
- ``--dry-run`` - Preview what would happen without making changes

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

The list operation shows available artifacts:

.. code-block:: bash

   git_recycle_bin.py list <repository> [options]

**Common Options:**
- ``--name`` - Filter by artifact name
- ``--expired`` - Show only expired artifacts  
- ``--active`` - Show only non-expired artifacts
- ``--format`` - Output format (table, json, compact)

Simple List Examples
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # List all artifacts
   git_recycle_bin.py list .
   
   # List from remote repository
   git_recycle_bin.py list git@artifacts.company.com:myproject.git
   
   # List with specific name
   git_recycle_bin.py list . --name "webapp-build"
   
   # List only active artifacts
   git_recycle_bin.py list . --active

Understanding List Output
~~~~~~~~~~~~~~~~~~~~~~~~~

Default table format shows:

.. code-block:: text

   NAME           SOURCE         COMMIT     EXPIRE              SIZE    PATH
   webapp-build   main           a1b2c3d4   2024-12-25 14:30    2.3MB   dist
   api-docs       develop        b2c3d4e5   2024-12-20 09:15    890KB   docs/_build
   user-manual    main           a1b2c3d4   2024-12-31 23:59    1.2MB   docs/manual.pdf
   
**Columns:**
- **NAME**: Artifact name you provided during push
- **SOURCE**: Git branch when artifact was created
- **COMMIT**: First 8 characters of source commit SHA
- **EXPIRE**: When artifact will be cleaned up
- **SIZE**: Estimated size of artifact
- **PATH**: Source path of artifact

Filtering Options
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Show only expired artifacts
   git_recycle_bin.py list . --expired
   
   # Show only active (non-expired) artifacts  
   git_recycle_bin.py list . --active
   
   # Filter by name pattern
   git_recycle_bin.py list . --name "webapp*"
   
   # Combine filters
   git_recycle_bin.py list . --name "webapp*" --active

Output Formats
~~~~~~~~~~~~~~

**Compact Format:**

.. code-block:: bash

   git_recycle_bin.py list . --format compact

.. code-block:: text

   webapp-build (main@a1b2c3d4, expires 2024-12-25 14:30, 2.3MB)
   api-docs (develop@b2c3d4e5, expires 2024-12-20 09:15, 890KB)

**JSON Format:**

.. code-block:: bash

   git_recycle_bin.py list . --format json

.. code-block:: json

   [
     {
       "name": "webapp-build",
       "source_branch": "main",
       "source_commit": "a1b2c3d4e5f6789...",
       "artifact_commit": "9f8e7d6c5b4a3e2d...",
       "expire": "2024-12-25T14:30:00+02:00",
       "path": "dist",
       "size_bytes": 2419200,
       "expired": false
     }
   ]

Download Operations
-------------------

Basic Download Syntax
~~~~~~~~~~~~~~~~~~~~~~

The download operation retrieves artifacts from the repository:

.. code-block:: bash

   git_recycle_bin.py download <repository> --name <artifact_name> [options]

**Required Parameters:**
- ``<repository>`` - Source artifact repository
- ``--name`` - Name of artifact to download

**Common Options:**
- ``--output`` - Where to save the artifact (default: artifact name)
- ``--commit`` - Download specific commit instead of latest
- ``--force`` - Overwrite existing files

Simple Download Examples
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Download latest artifact with default name
   git_recycle_bin.py download . --name "webapp-build"
   
   # Download to specific location
   git_recycle_bin.py download . --name "webapp-build" --output ./dist
   
   # Download from remote repository
   git_recycle_bin.py download git@artifacts.company.com:myproject.git \
       --name "webapp-build" --output ./build/webapp
   
   # Force overwrite existing files
   git_recycle_bin.py download . --name "webapp-build" --output ./dist --force

Download Specific Versions
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Download specific artifact commit
   git_recycle_bin.py download . --name "webapp-build" \
       --commit "9f8e7d6c5b4a3e2d1c0b9a8f7e6d5c4b"
   
   # Get commit SHA from list operation first
   git_recycle_bin.py list . --name "webapp-build" --format json

**Finding Commit SHAs:**

Use the list operation to find available versions:

.. code-block:: bash

   # List all versions of an artifact
   git_recycle_bin.py list . --name "webapp-build"
   
   # Use JSON format for exact commit SHAs
   git_recycle_bin.py list . --name "webapp-build" --format json | \
       jq -r '.[] | "\(.name): \(.artifact_commit)"'

Understanding Download Output
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   Downloading artifact 'webapp-build'...
   Source: artifact/latest/myproject.git@main/{dist}
   Commit: 9f8e7d6c5b4a3e2d1c0b9a8f7e6d5c4b
   Output: ./webapp-build
   
   Downloaded:
   - index.html (12KB)
   - assets/app.js (234KB)
   - assets/style.css (45KB)
   - images/logo.png (8KB)
   
   Total: 299KB in 4 files

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
   
   # 3. Later, on another machine or CI
   git_recycle_bin.py download . --name "webapp-build" --output ./dist

CI/CD Integration
~~~~~~~~~~~~~~~~~

**Build stage (push artifacts):**

.. code-block:: bash

   #!/bin/bash
   # ci-build.sh
   
   # Build the application
   npm ci
   npm run build
   
   # Push artifacts with build number
   git_recycle_bin.py push git@artifacts.company.com:myproject.git \
       --path dist \
       --name "webapp-build-${BUILD_NUMBER}" \
       --expire "30 days"
   
   # Also push with generic name for latest
   git_recycle_bin.py push git@artifacts.company.com:myproject.git \
       --path dist \
       --name "webapp-build" \
       --expire "30 days"

**Deploy stage (download artifacts):**

.. code-block:: bash

   #!/bin/bash
   # ci-deploy.sh
   
   # Download specific build
   if [ -n "$BUILD_NUMBER" ]; then
       git_recycle_bin.py download git@artifacts.company.com:myproject.git \
           --name "webapp-build-${BUILD_NUMBER}" \
           --output ./deploy/webapp
   else
       # Download latest build
       git_recycle_bin.py download git@artifacts.company.com:myproject.git \
           --name "webapp-build" \
           --output ./deploy/webapp
   fi

Cross-Repository Sharing
~~~~~~~~~~~~~~~~~~~~~~~~

**Shared artifact repository pattern:**

.. code-block:: bash

   # Team A pushes documentation
   git_recycle_bin.py push git@artifacts.company.com:shared.git \
       --path docs/_build --name "api-docs" --expire "2 weeks"
   
   # Team B downloads documentation
   git_recycle_bin.py download git@artifacts.company.com:shared.git \
       --name "api-docs" --output ./external-docs

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
   
   # Check what would be pushed without doing it
   git_recycle_bin.py push . --path dist --name "test" --dry-run
   
   # Verify repository access
   git ls-remote git@artifacts.company.com:myproject.git

These basic operations form the foundation of working with git-recycle-bin. Once you're comfortable 
with these patterns, you can explore the advanced features for more complex workflows. 
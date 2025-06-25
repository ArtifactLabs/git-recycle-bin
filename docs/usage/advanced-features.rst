Advanced Features
=================

This guide covers advanced git-recycle-bin features for power users and complex workflows.

Advanced Push Options
---------------------

Beyond basic artifact pushing, git-recycle-bin provides several advanced options for fine-grained control.

User Identity Options
~~~~~~~~~~~~~~~~~~~~~

Control who appears as the author of artifact commits:

.. code-block:: bash

   # Set custom author for artifact commits
   git_recycle_bin.py push <remote_url> \
       --path dist \
       --name "webapp-build" \
       --user-name "CI System" \
       --user-email "ci@company.com"

**Environment Variable Equivalents:**

.. code-block:: bash

   export GITRB_USERNAME="CI System"
   export GITRB_EMAIL="ci@company.com"
   git_recycle_bin.py push <remote_url> --path dist --name "webapp-build"

Source Repository Options
~~~~~~~~~~~~~~~~~~~~~~~~~~

Configure source repository references:

.. code-block:: bash

   # Use different source remote name
   git_recycle_bin.py push <remote_url> \
       --path dist \
       --name "webapp-build" \
       --src-remote-name "upstream"

Repository Management Options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Control temporary repository cleanup:

.. code-block:: bash

   # Keep temporary repository for debugging
   git_recycle_bin.py push <remote_url> \
       --path dist \
       --name "webapp-build" \
       --rm-tmp false

Git Integration Options
~~~~~~~~~~~~~~~~~~~~~~~

Control Git notes and tag pushing:

.. code-block:: bash

   # Push tags to artifact repository
   git_recycle_bin.py push <remote_url> \
       --path dist \
       --name "webapp-build" \
       --push-tag true

   # Push notes to source repository
   git_recycle_bin.py push <remote_url> \
       --path dist \
       --name "webapp-build" \
       --push-note true

Force Push Options
~~~~~~~~~~~~~~~~~~

Override existing artifacts:

.. code-block:: bash

   # Force push branches and tags
   git_recycle_bin.py push <remote_url> \
       --path dist \
       --name "webapp-build" \
       --force-branch true \
       --force-tag true

**Warning:** Force pushing will overwrite existing artifacts and may cause data loss.

Artifact Management Options
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Advanced artifact handling:

.. code-block:: bash

   # Include files normally ignored by .gitignore
   git_recycle_bin.py push <remote_url> \
       --path dist \
       --name "webapp-build" \
       --add-ignored true

   # Clean up expired artifacts during push
   git_recycle_bin.py push <remote_url> \
       --path dist \
       --name "webapp-build" \
       --rm-expired true

   # Clean up metadata references
   git_recycle_bin.py push <remote_url> \
       --path dist \
       --name "webapp-build" \
       --flush-meta true

Advanced List Options
---------------------

The `list` command prints artifact SHAs, one per line. It can be filtered by `name` or `path`.

Filtering and Querying
~~~~~~~~~~~~~~~~~~~~~~~

Filter artifacts by path or name:

.. code-block:: bash

   # List artifact SHAs for a specific path
   git_recycle_bin.py list <remote_url> --path "dist/webapp"

   # List artifact SHAs for a specific name
   git_recycle_bin.py list <remote_url> --name "webapp-build"

   # List all artifact SHAs for the current commit
   git_recycle_bin.py list <remote_url>

Advanced Download Options
-------------------------

This command has very few options. It takes one or more artifact SHAs as positional arguments.

Force Download
~~~~~~~~~~~~~~

Overwrite existing files during download:

.. code-block:: bash

   # Force download even if files exist
   git_recycle_bin.py download <remote_url> <artifact_sha> --force

Troubleshooting and Debugging
-----------------------------

Verbose Output
~~~~~~~~~~~~~~

Enable detailed logging for troubleshooting:

.. code-block:: bash

   # Basic verbose output
   git_recycle_bin.py --verbose push <remote_url> --path dist --name "build"

   # Maximum verbosity
   git_recycle_bin.py -vv push <remote_url> --path dist --name "build"

Quiet Mode
~~~~~~~~~~

Suppress all output except errors:

.. code-block:: bash

   # Quiet mode for scripting
   git_recycle_bin.py --quiet push <remote_url> --path dist --name "build"

Color Control
~~~~~~~~~~~~~

Control colorized output:

.. code-block:: bash

   # Disable colors
   git_recycle_bin.py --color false list <remote_url>

   # Force colors (even when not in terminal)
   git_recycle_bin.py --color true list <remote_url>

Environment Configuration
-------------------------

Complete Environment Variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All available environment variables for default configuration:

.. code-block:: bash

   # User identity
   export GITRB_USERNAME="Your Name"
   export GITRB_EMAIL="your.email@example.com"

   # Repository settings
   export GITRB_SRC_REMOTE="origin"
   export GITRB_RM_TMP="true"

   # Artifact defaults
   export GITRB_PATH="dist"
   export GITRB_NAME="default-build"
   export GITRB_EXPIRE="in 30 days"

   # Push behavior
   export GITRB_PUSH_TAG="false"
   export GITRB_PUSH_NOTE="false"
   export GITRB_ADD_IGNORED="false"
   export GITRB_RM_EXPIRED="false"
   export GITRB_FLUSH_META="false"
   export GITRB_FORCE_BRANCH="false"
   export GITRB_FORCE_TAG="false"

   # Output settings
   export GITRB_COLOR="true"

Configuration File Example
~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a shell script for consistent configuration:

.. code-block:: bash

   #!/bin/bash
   # grb-config.sh
   
   export GITRB_USERNAME="CI System"
   export GITRB_EMAIL="ci@company.com"
   export GITRB_EXPIRE="7 days"
   export GITRB_PUSH_TAG="true"
   export GITRB_RM_EXPIRED="true"
   
   # Source this file before using git-recycle-bin
   # source grb-config.sh

Best Practices
--------------

Production Workflows
~~~~~~~~~~~~~~~~~~~~

Recommended settings for production environments:

.. code-block:: bash

   # Production push with cleanup
   git_recycle_bin.py push <remote_url> \
       --path dist \
       --name "prod-build-${BUILD_ID}" \
       --expire "30 days" \
       --push-tag true \
       --rm-expired true \
       --user-name "CI System" \
       --user-email "ci@company.com"

Development Workflows
~~~~~~~~~~~~~~~~~~~~~

Settings for development and testing:

.. code-block:: bash

   # Development push
   git_recycle_bin.py push <remote_url> \
       --path build \
       --name "dev-build-$(date +%Y%m%d)" \
       --expire "3 days" \
       --add-ignored true

Error Handling
~~~~~~~~~~~~~~

Check command success in scripts:

.. code-block:: bash

   #!/bin/bash
   
   if git_recycle_bin.py push <remote_url> --path dist --name "build"; then
       echo "Artifact pushed successfully"
   else
       echo "Failed to push artifact" >&2
       exit 1
   fi

These advanced features provide fine-grained control over artifact management and enable integration
with complex CI/CD pipelines and development workflows.
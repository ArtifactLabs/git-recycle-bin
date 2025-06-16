Basic Workflow Example
=======================

This guide walks through a complete, realistic workflow using git-recycle-bin for a web application 
project. You'll see how to set up artifact repositories, integrate with build processes, and manage 
artifacts throughout development.

Scenario Overview
-----------------

**Project**: A Node.js web application with automated builds
**Team**: 3 developers working on different features
**Goal**: Share build artifacts without rebuilding from scratch
**Infrastructure**: Git repositories for source and artifacts

.. code-block:: text

   Source Repo        Artifact Repo        Deployment
   ┌─────────────┐    ┌──────────────┐    ┌──────────────┐
   │ webapp.git  │───▶│ artifacts.git│───▶│ Production   │
   │             │    │              │    │ Staging      │
   │ - main      │    │ - Builds     │    │ Development  │
   │ - develop   │    │ - Docs       │    └──────────────┘
   │ - feature/* │    │ - Assets     │
   └─────────────┘    └──────────────┘

Initial Setup
-------------

Repository Setup
~~~~~~~~~~~~~~~~

First, let's set up our repositories:

.. code-block:: bash

   # Create and clone the source repository
   git clone git@github.com:company/webapp.git
   cd webapp
   
   # Create a separate artifact repository
   # (This could be on the same Git server or different one)
   git clone git@artifacts.company.com:webapp-artifacts.git

**Directory Structure:**

.. code-block:: text

   ~/projects/
   ├── webapp/                 # Source repository
   │   ├── src/
   │   ├── package.json
   │   ├── build/             # Build output (not committed)
   │   └── docs/
   └── webapp-artifacts/       # Artifact repository (could be elsewhere)

Verify Installation
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Verify git-recycle-bin is available
   git_recycle_bin.py --help
   
   # Test repository access
   git_recycle_bin.py list git@artifacts.company.com:webapp-artifacts.git

If you get permission errors, verify your SSH keys and repository access.

Day 1: Initial Development
--------------------------

Setting Up the Build Process
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Our web application has a typical Node.js build process:

**package.json build scripts:**

.. code-block:: json

   {
     "scripts": {
       "build": "webpack --mode production",
       "build:dev": "webpack --mode development", 
       "docs": "jsdoc src/ -d docs/",
       "test": "jest"
     }
   }

**First Build and Push:**

.. code-block:: bash

   # Start in source repository
   cd ~/projects/webapp
   
   # Install dependencies and build
   npm install
   npm run build
   
   # Verify build output
   ls -la build/
   # Should see: index.html, bundle.js, styles.css, assets/

Push Your First Artifact
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Push the build artifacts
   git_recycle_bin.py push git@artifacts.company.com:webapp-artifacts.git \
       --path build \
       --name "webapp-build" \
       --expire "1 week"

**Expected Output:**

.. code-block:: text

   Pushing artifact 'webapp-build' from path 'build'...
   Source commit: f3e2d1c0 (Initial application structure)
   Artifact commit: a9b8c7d6e5f4
   
   Created references:
   - Branch: artifact/expire/2024-01-22/10.30+0200/webapp.git@f3e2d1c0/{build}
   - Tag: artifact/latest/webapp.git@main/{build}
   - Metadata: refs/artifact/meta-for-commit/f3e2d1c0/a9b8c7d6
   
   Artifact will expire: 2024-01-22 10:30 +0200

**What Happened:**
1. Git Recycle Bin created a commit in the artifact repository containing your build files
2. It created a branch with expiry information in the name
3. It updated a "latest" tag for easy access
4. It stored metadata linking back to your source commit

Verify the Push
~~~~~~~~~~~~~~~

.. code-block:: bash

   # List available artifacts
   git_recycle_bin.py list git@artifacts.company.com:webapp-artifacts.git

**Expected Output:**

.. code-block:: text

   NAME           SOURCE    COMMIT     EXPIRE              SIZE    PATH
   webapp-build   main      f3e2d1c0   2024-01-22 10:30    1.2MB   build

Day 2: Teammate Downloads Artifact
-----------------------------------

Your teammate needs to work on the project but doesn't want to rebuild from scratch.

Teammate's Workflow
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Teammate clones the source repository
   git clone git@github.com:company/webapp.git
   cd webapp
   
   # Install dependencies (but skip build)
   npm install
   
   # Download the existing build instead of building
   git_recycle_bin.py download git@artifacts.company.com:webapp-artifacts.git \
       --name "webapp-build" \
       --output build

**Expected Output:**

.. code-block:: text

   Downloading artifact 'webapp-build'...
   Source: artifact/latest/webapp.git@main/{build}
   Commit: a9b8c7d6e5f4
   Output: ./build
   
   Downloaded:
   - index.html (4KB)
   - bundle.js (856KB)
   - styles.css (23KB)
   - assets/logo.png (45KB)
   - assets/favicon.ico (2KB)
   
   Total: 930KB in 5 files

Now your teammate can start the development server immediately:

.. code-block:: bash

   # Start development server with existing build
   npm run serve
   # Server ready at http://localhost:3000

Day 3: Feature Development
--------------------------

Working on a Feature Branch
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Create feature branch
   git checkout -b feature/user-authentication
   
   # Make code changes
   # ... edit src/auth.js, src/login.html, etc ...
   
   # Test changes
   npm run test
   
   # Build updated application
   npm run build

Push Feature Build
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Push feature-specific build
   git_recycle_bin.py push git@artifacts.company.com:webapp-artifacts.git \
       --path build \
       --name "webapp-auth-feature" \
       --expire "3 days"

**Why shorter expiry?** Feature builds are temporary and don't need long retention.

**Expected Output:**

.. code-block:: text

   Pushing artifact 'webapp-auth-feature' from path 'build'...
   Source commit: d7c6b5a4 (Add user authentication system)
   Artifact commit: 1f2e3d4c5b6a
   
   Created references:
   - Branch: artifact/expire/2024-01-18/14.45+0200/webapp.git@d7c6b5a4/{build}
   - Tag: artifact/latest/webapp.git@feature/user-authentication/{build}
   
   Artifact will expire: 2024-01-18 14:45 +0200

Check Current Artifacts
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # See all artifacts
   git_recycle_bin.py list git@artifacts.company.com:webapp-artifacts.git

**Expected Output:**

.. code-block:: text

   NAME                 SOURCE                      COMMIT     EXPIRE              SIZE    PATH
   webapp-build         main                        f3e2d1c0   2024-01-22 10:30    1.2MB   build
   webapp-auth-feature  feature/user-authentication d7c6b5a4   2024-01-18 14:45    1.3MB   build

Day 4: Documentation Build
---------------------------

Adding Documentation Artifacts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Generate documentation
   npm run docs
   
   # Push documentation as separate artifact
   git_recycle_bin.py push git@artifacts.company.com:webapp-artifacts.git \
       --path docs \
       --name "webapp-docs" \
       --expire "2 weeks"

**Why separate artifact?** Documentation has different usage patterns and retention needs.

**Expected Output:**

.. code-block:: text

   Pushing artifact 'webapp-docs' from path 'docs'...
   Source commit: d7c6b5a4 (Add user authentication system)
   Artifact commit: 9e8d7c6b5a4f
   
   Created references:
   - Branch: artifact/expire/2024-01-29/09.15+0200/webapp.git@d7c6b5a4/{docs}
   - Tag: artifact/latest/webapp.git@feature/user-authentication/{docs}
   
   Artifact will expire: 2024-01-29 09:15 +0200

Day 5: Merge and Production Build
----------------------------------

Merging Feature to Main
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Switch to main and merge feature
   git checkout main
   git merge feature/user-authentication
   
   # Build production version
   npm run build
   
   # Push production build with longer retention
   git_recycle_bin.py push git@artifacts.company.com:webapp-artifacts.git \
       --path build \
       --name "webapp-build" \
       --expire "2 months"

**Note:** Using the same name "webapp-build" means this becomes the new "latest" version.

**Expected Output:**

.. code-block:: text

   Pushing artifact 'webapp-build' from path 'build'...
   Source commit: 2a1b0c9d (Merge feature/user-authentication)
   Artifact commit: 8d7c6b5a4e3f
   
   Created references:
   - Branch: artifact/expire/2024-03-15/11.20+0200/webapp.git@2a1b0c9d/{build}
   - Tag: artifact/latest/webapp.git@main/{build}  # <- Updated to point here
   
   Artifact will expire: 2024-03-15 11:20 +0200

Current State Check
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Check all artifacts
   git_recycle_bin.py list git@artifacts.company.com:webapp-artifacts.git

**Expected Output:**

.. code-block:: text

   NAME                 SOURCE                      COMMIT     EXPIRE              SIZE    PATH
   webapp-build         main                        f3e2d1c0   2024-01-22 10:30    1.2MB   build
   webapp-build         main                        2a1b0c9d   2024-03-15 11:20    1.3MB   build
   webapp-auth-feature  feature/user-authentication d7c6b5a4   2024-01-18 14:45    1.3MB   build
   webapp-docs          feature/user-authentication d7c6b5a4   2024-01-29 09:15    456KB   docs

**Notice:** Two artifacts with the same name but different commits.

Day 7: Deployment Process
-------------------------

Production Deployment
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # On deployment server
   ssh deploy@production.company.com
   
   # Create deployment directory
   mkdir -p /var/www/webapp-deploy
   cd /var/www/webapp-deploy
   
   # Download latest production build
   git_recycle_bin.py download git@artifacts.company.com:webapp-artifacts.git \
       --name "webapp-build" \
       --output ./current

**Expected Output:**

.. code-block:: text

   Downloading artifact 'webapp-build'...
   Source: artifact/latest/webapp.git@main/{build}
   Commit: 8d7c6b5a4e3f
   Output: ./current
   
   Downloaded:
   - index.html (4KB)
   - bundle.js (967KB)
   - styles.css (28KB)
   - assets/logo.png (45KB)
   - assets/favicon.ico (2KB)
   
   Total: 1.05MB in 5 files

Rollback Scenario
~~~~~~~~~~~~~~~~~

If there's an issue with the new version:

.. code-block:: bash

   # Find previous version
   git_recycle_bin.py list git@artifacts.company.com:webapp-artifacts.git \
       --name "webapp-build" --format json

.. code-block:: json

   [
     {
       "name": "webapp-build",
       "source_commit": "2a1b0c9d8e7f...",
       "artifact_commit": "8d7c6b5a4e3f...",
       "expire": "2024-03-15T11:20:00+02:00",
       "path": "build"
     },
     {
       "name": "webapp-build", 
       "source_commit": "f3e2d1c0b9a8...",
       "artifact_commit": "a9b8c7d6e5f4...",
       "expire": "2024-01-22T10:30:00+02:00",
       "path": "build"
     }
   ]

.. code-block:: bash

   # Download specific (older) version
   git_recycle_bin.py download git@artifacts.company.com:webapp-artifacts.git \
       --name "webapp-build" \
       --commit "a9b8c7d6e5f4" \
       --output ./rollback \
       --force

Week 2: Maintenance and Cleanup
--------------------------------

Checking for Expired Artifacts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Check what's expired
   git_recycle_bin.py list git@artifacts.company.com:webapp-artifacts.git --expired

**Expected Output (if today is Jan 19):**

.. code-block:: text

   NAME                 SOURCE                      COMMIT     EXPIRE              SIZE    PATH
   webapp-auth-feature  feature/user-authentication d7c6b5a4   2024-01-18 14:45    1.3MB   build

Cleaning Up Expired Artifacts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Clean expired artifacts
   git_recycle_bin.py clean git@artifacts.company.com:webapp-artifacts.git

**Expected Output:**

.. code-block:: text

   Cleaning expired artifacts...
   
   Found expired artifacts:
   - webapp-auth-feature (expired 2024-01-18 14:45)
   
   Cleaned:
   - Branch: artifact/expire/2024-01-18/14.45+0200/webapp.git@d7c6b5a4/{build}
   - Metadata: refs/artifact/meta-for-commit/d7c6b5a4/1f2e3d4c
   
   Reclaimed space: 1.3MB

CI/CD Integration
-----------------

Automated Build Script
~~~~~~~~~~~~~~~~~~~~~~

**build.sh** (for CI server):

.. code-block:: bash

   #!/bin/bash
   set -e
   
   # Build application
   npm ci
   npm run test
   npm run build
   
   # Determine expiry based on branch
   if [ "$GIT_BRANCH" = "main" ]; then
       EXPIRE="2 months"
       ARTIFACT_NAME="webapp-build"
   elif [ "$GIT_BRANCH" = "develop" ]; then
       EXPIRE="2 weeks"  
       ARTIFACT_NAME="webapp-build-dev"
   else
       EXPIRE="3 days"
       ARTIFACT_NAME="webapp-build-$(echo $GIT_BRANCH | sed 's/[^a-zA-Z0-9]/-/g')"
   fi
   
   # Push artifacts
   git_recycle_bin.py push git@artifacts.company.com:webapp-artifacts.git \
       --path build \
       --name "$ARTIFACT_NAME" \
       --expire "$EXPIRE"
   
   echo "Build artifact: $ARTIFACT_NAME (expires in $EXPIRE)"

**deploy.sh** (for deployment):

.. code-block:: bash

   #!/bin/bash
   set -e
   
   ENVIRONMENT=${1:-staging}
   
   case $ENVIRONMENT in
       production)
           ARTIFACT_NAME="webapp-build"
           DEPLOY_PATH="/var/www/production"
           ;;
       staging)
           ARTIFACT_NAME="webapp-build-dev"
           DEPLOY_PATH="/var/www/staging"
           ;;
       *)
           echo "Unknown environment: $ENVIRONMENT"
           exit 1
           ;;
   esac
   
   # Download and deploy
   mkdir -p "$DEPLOY_PATH"
   git_recycle_bin.py download git@artifacts.company.com:webapp-artifacts.git \
       --name "$ARTIFACT_NAME" \
       --output "$DEPLOY_PATH/current" \
       --force
   
   echo "Deployed $ARTIFACT_NAME to $ENVIRONMENT"

Advanced Workflow Patterns
---------------------------

Multi-Repository Setup
~~~~~~~~~~~~~~~~~~~~~~

For larger organizations, you might have:

.. code-block:: bash

   # Separate repositories by artifact type
   
   # Application builds
   git_recycle_bin.py push git@artifacts.company.com:webapp-builds.git \
       --path build --name "webapp"
   
   # Documentation
   git_recycle_bin.py push git@artifacts.company.com:webapp-docs.git \
       --path docs --name "api-docs"
   
   # Container images (if using containers)
   git_recycle_bin.py push git@artifacts.company.com:webapp-containers.git \
       --path docker-context --name "webapp-image"

Cross-Team Sharing
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Backend team pushes API documentation
   git_recycle_bin.py push git@artifacts.company.com:shared-docs.git \
       --path api-docs --name "user-service-api" --expire "1 month"
   
   # Frontend team downloads API docs
   git_recycle_bin.py download git@artifacts.company.com:shared-docs.git \
       --name "user-service-api" --output ./external-apis/user-service

Build Avoidance Pattern
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   #!/bin/bash
   # smart-build.sh
   
   # Check if artifact exists for current commit
   current_commit=$(git rev-parse HEAD)
   
   if git_recycle_bin.py list git@artifacts.company.com:webapp-artifacts.git \
           --name "webapp-build" --format json | \
           jq -e ".[] | select(.source_commit | startswith(\"$current_commit\"))" > /dev/null; then
       
       echo "Artifact exists for commit $current_commit, downloading..."
       git_recycle_bin.py download git@artifacts.company.com:webapp-artifacts.git \
           --name "webapp-build" --output build
   else
       echo "No artifact found for commit $current_commit, building..."
       npm run build
       git_recycle_bin.py push git@artifacts.company.com:webapp-artifacts.git \
           --path build --name "webapp-build" --expire "1 month"
   fi

Summary
-------

This workflow demonstrates:

**Key Benefits:**
- **Time Savings**: Teammates don't rebuild unnecessarily
- **Consistency**: Everyone uses the same build artifacts
- **Traceability**: Every artifact links back to source code
- **Automatic Cleanup**: Expired artifacts are removed automatically
- **Deployment Reliability**: Exact artifacts used in production are known

**Best Practices Shown:**
- Use descriptive artifact names
- Set appropriate expiry times for different use cases
- Separate artifacts by type and purpose
- Integrate with existing CI/CD processes
- Regular cleanup of expired artifacts

**Next Steps:**
- Explore advanced features like :git-doc:`git notes <git-notes>` integration
- Set up automated cleanup schedules
- Consider artifact repository backup strategies
- Implement monitoring for artifact repository health

This basic workflow can be adapted to any development process and scales from individual developers to large teams.

This example demonstrates a complete workflow for managing documentation artifacts using git-recycle-bin, 
from initial setup through publishing, retrieval, and eventual cleanup of expired artifacts. 
♻️ git-recycle-bin Documentation
================================

.. raw:: html

   <div class="hero-section">
      <img src="_static/artwork/grb/vector/flat1-color-dark.snug.svg" alt="Logo" style="width: 250px; height: 250px; margin-bottom: 0px; display: block; margin-left: auto; margin-right: auto; background: transparent;">

      <table class="hero-taglines-table">
         <tr>
            <td class="hero-tagline">
               <strong>🔧 The missing piece in your CI pipeline</strong>
            </td>
            <td class="hero-tagline">
               <strong>🌍 Store artifacts in git,<br>skip rebuilds across teams</strong>
            </td>
         </tr>
         <tr>
            <td class="hero-tagline">
               <strong>🤘🏼 Permission-less, decentralized<br>artifact storage</strong>
            </td>
            <td class="hero-tagline">
               <strong>👀 See artifacts using standard CLI<br><code>git log --notes</code></strong>
            </td>
         </tr>
         <tr>
            <td class="hero-tagline">
               <strong>⚡ Efficient artifact management,<br>Git-powered</strong>
            </td>
            <td class="hero-tagline">
               <strong>🔑 Same authentication you already use</strong>
            </td>
         </tr>
         <tr>
            <td class="hero-tagline">
               <strong>💾 Use any Git-host storage,<br>no vendor lock-in</strong>
            </td>
            <td class="hero-tagline">
               <strong>💻 Local developers first, CI second</strong>
            </td>
         </tr>
         <tr>
            <td class="hero-tagline" colspan="2" style="text-align: center;">
               <strong>🍰 Have your cake and share it too 💃</strong>
            </td>
         </tr>
      </table>
   </div>

|grb| is a command-line tool that transforms how you manage build artifacts by treating them as
first-class citizens in your Git workflow, enabling automatic expiry, full source traceability, and efficient
build avoidance through Git-native storage and retrieval mechanisms.

✨ Key Features
---------------

.. grid:: 2
   :gutter: 3

   .. grid-item-card:: 🔄 Bidirectional Traceability
      :class-card: feature-card

      Full bidirectional linking between source commits and artifacts using :git-doc:`git notes <git-notes>`

   .. grid-item-card:: ⏰ Automatic Expiry  
      :class-card: feature-card

      Set expiration dates for artifacts with automatic cleanup

   .. grid-item-card:: 🔧 Git Integration
      :class-card: feature-card

      Uses Git for storage, versioning, and distributed access

   .. grid-item-card:: 📋 Metadata Tracking
      :class-card: feature-card

      Rich metadata links artifacts back to source commits

   .. grid-item-card:: 🚀 Build Avoidance
      :class-card: feature-card

      Avoid rebuilding artifacts that already exist

   .. grid-item-card:: 👥 Team Collaboration
      :class-card: feature-card

      Share artifacts across team members and CI/CD systems

🚀 Quick Start
--------------

Get up and running in minutes:

.. code-block:: bash

   # Install directly from GitHub (use of venv recommended)
   pip install --user git+https://github.com/ArtifactLabs/git-recycle-bin.git@v0.2.6

   # Push an artifact with expiry
   git_recycle_bin.py push <remote_url> --path build/ --name "my-build" --expire "1 week"

   # List available artifacts
   git_recycle_bin.py list <remote_url>

- where `<remote_url>` is the URL of the remote repository you want to push to.

This will create a new branch in the remote repository and push your build artifact to it.


📚 Documentation Sections
-------------------------

.. toctree::
   :maxdepth: 2
   :caption: 🎯 Getting Started
   :name: getting-started

   overview
   installation
   quickstart
   concepts
   comparison
   faq

.. toctree::
   :maxdepth: 2
   :caption: 📖 User Guide
   :name: user-guide

   usage/basic-operations
   usage/advanced-features

.. toctree::
   :maxdepth: 2
   :caption: 💡 Examples & Tutorials
   :name: examples

   examples/basic-workflow



🔗 Quick Navigation
-------------------

.. grid:: 2
   :gutter: 3

   .. grid-item-card:: ⚡ Quick Start
      :link: quickstart
      :link-type: doc
      :class-card: nav-card

      Get started in 5 minutes with our step-by-step guide

   .. grid-item-card:: 🏗️ Basic Workflow
      :link: examples/basic-workflow
      :link-type: doc
      :class-card: nav-card

      Complete workflow example with real-world scenarios

   .. grid-item-card:: 📚 Command Reference
      :link: usage/basic-operations
      :link-type: doc
      :class-card: nav-card

      Comprehensive command-line reference

   .. grid-item-card:: 🧠 Core Concepts
      :link: concepts
      :link-type: doc
      :class-card: nav-card

      Understanding the architecture and design principles

   .. grid-item-card:: 💻 Installation
      :link: installation
      :link-type: doc
      :class-card: nav-card

      Installation instructions for all platforms


🆘 Support and Development
--------------------------

.. admonition:: Need Help?
   :class: tip

   For questions, bug reports, or feature requests, please visit the project repository.

.. admonition:: Contributing
   :class: note

   Contributions welcome! See the project repository for development guidelines.

📊 Project Status
-----------------

.. list-table:: Project Information
   :widths: 30 70
   :header-rows: 1

   * - Aspect
     - Status
   * - **Development Status**
     - Active Development
   * - **Python Support**
     - 3.8+
   * - **License**
     - Apache License 2.0
   * - **Documentation**
     - Comprehensive

🔍 Search and Index
-------------------

* :ref:`genindex` - General Index
* :ref:`modindex` - Module Index  
* :ref:`search` - Search Documentation

Installation
============

|grb| can be installed in several ways depending on your environment and preferences.

Prerequisites
-------------

* **Git**: Version 2.0 or higher (for proper :git-doc:`git notes <git-notes>` support)
* **Python**: Version 3.8 or higher
* **Operating System**: Linux, macOS, or Windows with WSL

.. tip::
   
   New to Git? The `Git Glossary <https://git-scm.com/docs/gitglossary>`_ provides definitions for all Git
   concepts used in this documentation.

Check your Git version:

.. code-block:: bash

   git --version

Check your Python version:

.. code-block:: bash

   python3 --version

Installation Methods
--------------------

Method 1: Using Nix
~~~~~~~~~~~~~~~~~~~

If you're using Nix, this is the preferred installation method as it ensures reproducible builds and
handles all dependencies automatically.

**Option A: Using shell.nix**

Create a ``shell.nix`` file in your project:

.. code-block:: nix

   { pkgs ? import <nixpkgs> {} }:
   let
     git-recycle-bin = pkgs.callPackage (pkgs.fetchFromGitHub {
       owner = "ArtifactLabs";
       repo = "git-recycle-bin";
       rev = "v0.2.6";  # Pin to a specific version
       sha256 = "sha256-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=";  # Update this hash
     } + "/default.nix") {};
   in
   pkgs.mkShell {
     buildInputs = [
       git-recycle-bin
       pkgs.git
     ];
   }

Then enter the shell:

.. code-block:: bash

   nix-shell

**Option B: Using flakes**

If you prefer Nix flakes, add to your ``flake.nix``:

.. code-block:: nix

   {
     inputs = {
       nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
       git-recycle-bin = {
         url = "github:ArtifactLabs/git-recycle-bin";
         inputs.nixpkgs.follows = "nixpkgs";
       };
     };

     outputs = { self, nixpkgs, git-recycle-bin }:
       let
         system = "x86_64-linux";  # or your system
         pkgs = nixpkgs.legacyPackages.${system};
       in {
         devShells.${system}.default = pkgs.mkShell {
           buildInputs = [
             git-recycle-bin.packages.${system}.default
           ];
         };
       };
   }

Method 2: Using pip
~~~~~~~~~~~~~~~~~~~

Install latest master directly from GitHub (not recommended):

.. code-block:: bash

   pip install git+https://github.com/ArtifactLabs/git-recycle-bin.git

Or install a specific version:

.. code-block:: bash

   pip install git+https://github.com/ArtifactLabs/git-recycle-bin.git@v0.2.6

**Using a virtual environment (recommended):**

.. code-block:: bash

   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install git+https://github.com/ArtifactLabs/git-recycle-bin.git@v0.2.6

Method 3: From Source
~~~~~~~~~~~~~~~~~~~~~

Clone the repository and install:

.. code-block:: bash

   git clone https://github.com/ArtifactLabs/git-recycle-bin.git
   cd git-recycle-bin
   pip install .

For development installation:

.. code-block:: bash

   git clone https://github.com/ArtifactLabs/git-recycle-bin.git
   cd git-recycle-bin
   pip install -e .

This creates an editable installation that reflects changes to the source code.

Verification
------------

After installation, verify that git-recycle-bin is working correctly:

.. code-block:: bash

   # Check that the command is available
   git_recycle_bin.py --version

   # Display help to see all available options
   git_recycle_bin.py --help

   # Run a quick test (if you're in a Git repository)
   git_recycle_bin.py list . --help

Expected output should show version information and help text without errors.

Dependencies
------------

|grb| has minimal runtime dependencies:

**Required Python Packages:**

* ``maya`` - For date parsing and manipulation
* ``colorama`` - For colored terminal output
* ``dateparser`` - For flexible date parsing

These are automatically installed when using pip or handled by Nix.

**Optional Dependencies:**

* ``pytest`` - For running tests (development only)
* ``coverage`` - For test coverage reports (development only)
* ``markdownlint`` - For linting documentation (development only)

Configuration
-------------

|grb| uses Git's configuration system. You may want to set up some global defaults using
:git-doc:`git config <git-config>`:

.. code-block:: bash

   # Set default user information for artifact commits
   git config --global user.name "Your Name"
   git config --global user.email "your.email@example.com"

   # Optional: Set default remote for artifacts
   git config --global recycle-bin.default-remote "git@artifacts.example.com:artifacts.git"

Troubleshooting
---------------

Common Installation Issues
~~~~~~~~~~~~~~~~~~~~~~~~~~

**"Command not found" error:**

Ensure that the installation location is in your PATH. With pip installations:

.. code-block:: bash

   # Find where pip installed the script
   python3 -m pip show -f git-recycle-bin

   # Check your PATH
   echo $PATH

**Permission errors with pip:**

Use a virtual environment or user installation:

.. code-block:: bash

   pip install --user git+https://github.com/ArtifactLabs/git-recycle-bin.git

**Git version compatibility:**

Ensure you have Git 2.0 or higher:

.. code-block:: bash

   git --version

Some features like advanced :git-doc:`git notes <git-notes>` handling require newer Git versions.

**Python version issues:**

|grb| requires Python 3.8+. Check your version:

.. code-block:: bash

   python3 --version

Platform-Specific Notes
~~~~~~~~~~~~~~~~~~~~~~~

**macOS:**

If using Homebrew's Git, ensure it's in your PATH before system Git:

.. code-block:: bash

   export PATH="/usr/local/bin:$PATH"

**Windows:**

Use Windows Subsystem for Linux (WSL) for the best experience. Native Windows support may have path
handling limitations.

**Linux:**

Most distributions work out of the box. Ensure you have development headers if building from source:

.. code-block:: bash

   # Ubuntu/Debian
   sudo apt install python3-dev git

   # RHEL/CentOS/Fedora
   sudo yum install python3-devel git

Getting Help
------------

If you encounter issues during installation:

1. **Check the logs**: Look for specific error messages
2. **Verify prerequisites**: Ensure Git and Python versions are correct
3. **Try different methods**: If pip fails, try Nix or source installation
4. **Search issues**: Check the `GitHub Issues <https://github.com/ArtifactLabs/git-recycle-bin/issues>`_ page
5. **Ask for help**: Open a new issue with your installation details

Next Steps
----------

After successful installation:

* **Quick Start**: Try the :doc:`quickstart` guide
* **Basic Usage**: Learn common operations in :doc:`usage/basic-operations`  
* **Examples**: See real-world examples in :doc:`examples/basic-workflow` 
# Contributing 🙌

Thank you for considering a contribution!
To keep the project easy to work with please follow these steps:

1. **Fork and branch** from `master`.
   Clone your fork then create a feature branch:

   ```bash
   git clone git@example.com:you/git-recycle-bin.git
   cd git-recycle-bin
   git checkout -b my-feature origin/master
   ```

2. **Coding style** follows PEP 8 with four-space indents
   and type hints where useful.
3. **Run tests locally**:
   - Preferred: `nix-shell shell.nix --pure --run "just unittest"`
   - Non‑Nix: `pip install .` then `PYTHONPATH=$PWD:$PWD/src pytest`
4. **Open a pull request** with a short summary of your changes and how you
   tested them.

Please also read `AGENTS.md` for repository etiquette.

## Installing Nix

Nix gives you a fully reproducible build environment. Follow the official
[installation guide](https://nixos.org/download.html) if you don't have it yet.

All kinds of improvements are welcome – documentation, tests or features.
Happy hacking! 🚀

# Contributing 🙌

Thank you for considering a contribution! To keep the project easy to work with please follow these steps:

1. **Fork and branch** from `master`.
2. **Coding style** follows PEP 8 with four-space indents and type hints where useful.
3. **Run tests locally**:
   - Preferred: `nix-shell shell.nix --pure --run "just unittest"`
   - Non‑Nix: `pip install .` then `PYTHONPATH=$PWD:$PWD/src pytest`
4. **Open a pull request** with a short summary of your changes and how you tested them.

All kinds of improvements are welcome – documentation, tests or features. Happy hacking! 🚀

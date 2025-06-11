# Contributing 🤝

Thank you for considering contributing to Git Recycle Bin!

## Getting started

1. Fork this repository and create a feature branch.
2. Install dependencies:
   ```bash
   pip install python-dateutil colorama maya
   ```
3. Export a timezone for tests (optional but ensures reproducibility):
   ```bash
   export TZ=Europe/Copenhagen
   ```
4. Run the unit tests:
   ```bash
   PYTHONPATH=$PWD:$PWD/src pytest -q
   ```

## Sending changes

- Ensure tests pass and update documentation as needed.
- Submit a pull request with a clear description of your changes.

We love improvements, big or small. Happy hacking! 🚀

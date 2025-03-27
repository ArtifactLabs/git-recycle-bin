# Clean generated docs, lint reports, python caches, etc
clean: docs-clean python-clean

# Run all linters (practical set)
lint:  docs-lint shell-lint md-lint rst-lint

########################

# Run unit tests
unittest:
    PYTHONPATH="$PYTHONPATH:$PWD:$PWD/src" pytest --cov=src --cov-report=xml

# Test of aux/git_add_ssh_remote.sh
test_git_add_ssh_remote:
    tests/test_git_add_ssh_remote.sh

########################

# Demonstrate --help
demo0:
    git_recycle_bin.py --help

# for general flags look at push.justfile
# the other examples are only command specific
mod demo-push 'demos/push.justfile'
mod demo-list 'demos/list.justfile'
mod demo-clean 'demos/clean.justfile'
mod demo-download 'demos/download.justfile'

########################

# Lint shell scripts for tracked files, not for submodules
shell-lint:
    git ls-files -z '*.sh' | xargs -0 shellcheck

########################

# Lint Markdown files for tracked files, not for submodules
md-lint:
    git ls-files -z '*.md' | xargs -0 markdownlint

########################

# Lint RST files for basic syntax issues (basic check only)
rst-lint-basic:
    git ls-files -z '*.rst' | xargs -0 restructuredtext-lint || echo "Note: Some Sphinx-specific errors are expected"

# Check RST files with rstcheck (ignoring Sphinx-specific elements)
rst-lint-syntax:
    git ls-files -z '*.rst' | xargs -0 rstcheck --ignore-directives toctree,automodule,grid --ignore-roles git-doc,git-book,doc,ref || echo "Note: Some Sphinx-specific errors may remain"

# Check RST line lengths (120 char limit)
rst-lint-length:
    find docs/ -name '*rst' | while read line; do awk 'length>120{print FILENAME ":" NR, "is too long. It is", length, "characters long"}' "$line"; done

# Run all RST linters (comprehensive but may show expected errors)
rst-lint: rst-lint-basic rst-lint-syntax rst-lint-length

########################

# Delete Sphinx-generated documentation
docs-clean:
    -rm -rf docs/_build/

# Internal, prep for assets referenced by raw html
_docs-pre:
    @mkdir -p docs/_build/html/_static/
    @cp -r docs/artwork/ docs/_build/html/_static/

# Build Sphinx documentation
# Output goes to docs/_build/html
# Use PYTHONPATH so autodoc can find modules
docs: _docs-pre
    PYTHONPATH="$PYTHONPATH:$PWD:$PWD/src" sphinx-build -b html docs docs/_build/html

# Lint documentation with Sphinx
# Treat warnings as errors to catch broken references
docs-lint-warnings: _docs-pre
    PYTHONPATH="$PYTHONPATH:$PWD:$PWD/src" sphinx-build -E -n -W -b dummy docs docs/_build/dummy

# Sphinx replacements fail in certain cases, check for our own substitutions
# Old issue https://github.com/sphinx-doc/sphinx/issues/3151
docs-lint-failed-substitutions: docs
    # Any matches are failures
    ! rg -thtml '\|grb\|' docs/_build/html/

# Lint the Sphinx build
docs-lint: docs-lint-warnings docs-lint-failed-substitutions

########################

# Clean python caches
python-clean:
    -find . -name '.pytest_cache' -type d -exec rm -rf {} +
    -find . -name '.venv*' -type d -exec rm -rf {} +
    -find . -name '.mypy_cache' -type d -exec rm -rf {} +
    -find . -name '.ruff_cache' -type d -exec rm -rf {} +
    -find . -name '__pycache__' -type d -exec rm -rf {} +
    -find . -name 'htmlcov' -type d -exec rm -rf {} +
    -find . -name '.tox' -type d -exec rm -rf {} +
    -find . -name 'build' -type d -exec rm -rf {} +
    -find . -name 'dist' -type d -exec rm -rf {} +
    -find . -name '*.egg-info' -type d -exec rm -rf {} +
    -find . -name '*.pyc' -delete
    -find . -name '*.pyo' -delete
    -find . -name '*.pyd' -delete
    -find . -name '.coverage' -delete

# Run (pytest) across all supported python versions
python-sweep cmd="pytest":
    nix-shell test-envs/shell.py38.nix --pure --run 'python --version && {{cmd}}'
    nix-shell test-envs/shell.py39.nix --pure --run 'python --version && {{cmd}}'
    nix-shell test-envs/shell.py310.nix --pure --run 'python --version && {{cmd}}'
    nix-shell test-envs/shell.py311.nix --pure --run 'python --version && {{cmd}}'
    nix-shell test-envs/shell.py312.nix --pure --run 'python --version && {{cmd}}'
    nix-shell test-envs/shell.py313.nix --pure --run 'python --version && {{cmd}}'

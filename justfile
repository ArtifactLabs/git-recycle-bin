# Run unit tests
unittest:
    PYTHONPATH="$PYTHONPATH:$PWD:$PWD/src" pytest --cov=src --cov-report=xml

# Demonstrate help
demo0:
    git_recycle_bin.py --help


# for general flags look at push.justfile
# the other examples are only command specific
mod push 'demos/push.justfile'
mod list 'demos/list.justfile'
mod clean 'demos/clean.justfile'
mod download 'demos/download.justfile'

# Lint shell scripts
lint-shell:
    find . -name '*.sh' -print0 | xargs -0 shellcheck

# Lint Markdown files
lint-md:
    markdownlint '**/*.md'

# Run all linters
lint: lint-shell lint-md

# Build Sphinx documentation
# Output goes to docs/_build/html
# Use PYTHONPATH so autodoc can find modules
docs:
    PYTHONPATH="$PYTHONPATH:$PWD:$PWD/src" sphinx-build -b html docs docs/_build/html

# Lint documentation with Sphinx
# Treat warnings as errors to catch broken references
docs-lint:
    PYTHONPATH="$PYTHONPATH:$PWD:$PWD/src" sphinx-build -n -W -b dummy docs docs/_build/dummy

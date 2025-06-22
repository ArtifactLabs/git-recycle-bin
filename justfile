# Clean generated docs, lint reports, python caches, etc
clean: docs-clean

########################
# Run unit tests
unittest:
    PYTHONPATH="$PYTHONPATH:$PWD:$PWD/src" pytest --cov=src --cov-report=xml

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

# Lint shell scripts
lint-shell:
    find . -name '*.sh' -print0 | xargs -0 shellcheck

# Lint Markdown files
lint-md:
    markdownlint '**/*.md'

# Lint RST files for basic syntax issues (basic check only)
lint-rst-basic:
    find docs -name '*.rst' -print0 | xargs -0 restructuredtext-lint || echo "Note: Some Sphinx-specific errors are expected"

# Check RST files with rstcheck (ignoring Sphinx-specific elements)
lint-rst-syntax:
    find docs -name '*.rst' -print0 | xargs -0 rstcheck --ignore-directives toctree,automodule,grid --ignore-roles git-doc,git-book,doc,ref || echo "Note: Some Sphinx-specific errors may remain"

# Check RST line lengths (120 char limit)
lint-rst-length:
    find docs/ -name '*rst' | while read line; do awk 'length>120{print FILENAME ":" NR, "is too long. It is", length, "characters long"}' "$line"; done

# Run all RST linters (comprehensive but may show expected errors)
lint-rst: lint-rst-basic lint-rst-syntax lint-rst-length

# Run all linters (practical set)
lint: lint-shell lint-md lint-rst

########################

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
docs-lint: _docs-pre
    PYTHONPATH="$PYTHONPATH:$PWD:$PWD/src" sphinx-build -E -n -W -b dummy docs docs/_build/dummy

# Clean documentation build artifacts
docs-clean:
    -rm -rf docs/_build/

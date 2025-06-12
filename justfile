# Run unit tests
unittest:
    PYTHONPATH="$PYTHONPATH:$PWD:$PWD/src" pytest

# Demonstrate help
demo0:
    git_recycle_bin.py --help


# for general flags look at push.justfile
# the other examples are only command specific
mod push 'demos/push.justfile'
mod list 'demos/list.justfile'
mod clean 'demos/clean.justfile'
mod download 'demos/download.justfile'

# Lint shell scripts with shellcheck
shellcheck:
    shellcheck -- $(git ls-files '*.sh')

# Lint Markdown files with markdownlint
mdlint:
    markdownlint -- $(git ls-files '*.md')

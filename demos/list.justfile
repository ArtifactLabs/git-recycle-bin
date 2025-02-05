# there is problems with circular dependencies
# (even though they are not circular)
# import 'lib.justfile'
_remove_artifacts:
    git ls-remote --refs . \
    | grep "artifact" \
    | awk '{print $2}' \
    | xargs -I _ git update-ref -d _

# Demonstrate the list command with no artifacts
demo1: _remove_artifacts
    git_recycle_bin.py list .

# Demonstrate the list command with artifacts
demo2: _remove_artifacts
    just --justfile=push.justfile demo1
    git_recycle_bin.py list .

# Same as demo2 but with --name filter
demo3: _remove_artifacts
    just --justfile=push.justfile demo1
    git_recycle_bin.py list . --name "demo 1"

# Same as demo2 but with --path filter
demo4: _remove_artifacts
    just --justfile=push.justfile demo1
    # notice the path is demos as remote is .
    git_recycle_bin.py list . --path demos

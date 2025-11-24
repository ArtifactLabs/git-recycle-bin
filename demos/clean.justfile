# there is problems with circular dependencies
# (even though they are not circular)
# import 'lib.justfile'
_remove_artifacts:
    git ls-remote --refs . \
    | grep "artifact" \
    | awk '{print $2}' \
    | xargs -I _ git update-ref -d _

# Demonstrate cleaning
demo1: _remove_artifacts
    just --justfile=push.justfile demo4
    git ls-remote . | grep "artifact"
    git-recycle-bin clean .
    git ls-remote . | grep "artifact" || true

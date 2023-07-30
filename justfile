# Run unit tests
unittest:
    PYTHONPATH="$PYTHONPATH:$PWD:$PWD/src" pytest

# Demonstrate help
demo0:
    git_recycle_bin.py --help

# Demonstrate that bin-repo can be same as src-repo. Take this repo's own content (--path .) and push as an artifact to itself.
demo1:
    git_recycle_bin.py --path . --name "demo 1" --remote . --push --user-name "foo" --user-email "a@b"
    git branch -vv -a

# Same as demo1 but quiet
demo1_quiet:
    git_recycle_bin.py --path . --name "demo 1q" --remote . --push --quiet --user-name "foo" --user-email "a@b"
    git branch -vv -a

# Same as demo1 but verbose
demo1_verbose:
    git_recycle_bin.py --path . --name "demo 1v" --remote . --push -v --user-name "foo" --user-email "a@b"
    git branch -vv -a

# Same as demo1 but very verbose
demo1_vverbose:
    git_recycle_bin.py --path . --name "demo 1vv" --remote . --push -vv --user-name "foo" --user-email "a@b"
    git branch -vv -a

# Same as demo1 but push-tag only work if you're not ahead
demo2:
    git_recycle_bin.py --path . --name "demo 2" --remote . --push --push-tag --user-name "foo" --user-email "a@b"
    git branch -vv -a
    git tag -l

# Demonstrate expiry with fuzzy time denomination
demo3:
    git_recycle_bin.py --quiet --path . --name "demo 3" --remote . --push --expire "in 2 seconds" --user-name "foo" --user-email "a@b"
    git branch -vv
    sleep 3
    git_recycle_bin.py --quiet --path . --name "demo 3" --remote . --rm-expired --user-name "foo" --user-email "a@b"
    git branch -vv

# Demonstrate expiry in the past, relative time
demo4:
    git_recycle_bin.py --quiet --path . --name "demo 4" --remote . --push --expire "10 minutes ago" --user-name "foo" --user-email "a@b"
    git branch -vv
    git_recycle_bin.py -vv --path . --name "demo 4" --remote . --rm-expired --user-name "foo" --user-email "a@b"
    git branch -vv

# Demonstrate expiry in the past, absolute time
demo5:
    git_recycle_bin.py --quiet --path . --name "demo 5" --remote . --push --expire "Fri Jul 28 11:41:06 PM CEST 2023" --user-name "foo" --user-email "a@b"
    git branch -vv
    git_recycle_bin.py -vv --path . --name "demo 5" --remote . --rm-expired --user-name "foo" --user-email "a@b"
    git branch -vv

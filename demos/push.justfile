# Demonstrate that bin-repo can be same as src-repo. Take this repo's own content (--path .) and push as an artifact to itself.
demo1:
    git-recycle-bin push \
        . \
        --path . \
        --name "demo 1" \
        --user-name "foo" --user-email "a@b"
    git branch -vv -a

# Same as demo1 but quiet
demo1_quiet:
    git-recycle-bin push --quiet \
        . \
        --path . \
        --name "demo 1q" \
        --user-name "foo" --user-email "a@b"
    git branch -vv -a

# Same as demo1 but verbose
demo1_verbose:
    git-recycle-bin push -v \
        . \
        --path . \
        --name "demo 1v" \
        --user-name "foo" --user-email "a@b"
    git branch -vv -a

# Same as demo1 but very verbose
demo1_vverbose:
    git-recycle-bin push -vv \
        . \
        --path . \
        --name "demo 1vv" \
        --user-name "foo" --user-email "a@b"
    git branch -vv -a

# Same as demo1 but push-tag only work if you're not ahead
demo2:
    git-recycle-bin push . \
        --tag \
        --path . \
        --name "demo 2" \
        --user-name "foo" --user-email "a@b"
    git branch -vv -a
    git tag -l

# TODO: what to do about --rm-expired and --flush-meta?
# Demonstrate expiry with fuzzy time denomination
demo3:
    git-recycle-bin push . \
        --quiet \
        --path . \
        --name "demo 3" \
        --expire "in 2 seconds" \
        --user-name "foo" --user-email "a@b"
    git branch -vv
    sleep 3
    # git-recycle-bin --rm-expired --quiet --flush-meta \
    #     . \
    #     --path . \
    #     --name "demo 3" \
    #     --user-name "foo" --user-email "a@b"
    git branch -vv

# TODO: what to do about --rm-expired and --flush-meta?
# Demonstrate expiry in the past, relative time
demo4:
    git-recycle-bin push --quiet \
        . \
        --path . \
        --name "demo 4" \
        --expire "10 minutes ago" \
        --user-name "foo" --user-email "a@b"
    git branch -vv
    # git-recycle-bin --rm-expired -vv --flush-meta \
    #     . \
    #     --path . \
    #     --name "demo 4" \
    #     --user-name "foo" --user-email "a@b"
    git branch -vv

# TODO: what to do about --rm-expired and --flush-meta?
# Demonstrate expiry in the past, absolute time
demo5:
    git-recycle-bin push --quiet \
        . \
        --path . \
        --name "demo 5" \
        --expire "Fri Jul 28 11:41:06 PM CEST 2023" \
        --user-name "foo" --user-email "a@b"
    git branch -vv
    # git-recycle-bin --rm-expired -vv \
    #     . \
    #     --path . \
    #     --name "demo 5" \
    #     --user-name "foo" --user-email "a@b"
    git branch -vv

# Demonstrate pushing git note to src repo
demo6_note:
    git-recycle-bin push . --note -vv \
        --rm-expired \
        --path . \
        --name "demo 6 note" \
        --expire "in 10 seconds" \
        --user-name "foo" --user-email "a@b"
    git log -1 --notes="notes/artifact/*" | nl -ba

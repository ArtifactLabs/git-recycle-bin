demo1:
    @mkdir -p ../tmp
    touch ../tmp/{1..3} && ls ../tmp
    git-recycle-bin push \
        . \
        --path ../tmp \
        --name tmp \
        --add-ignored \
        --user-name "foo" --user-email "a@b"
    rm ../tmp/{1..2} && ls ../tmp
    git-recycle-bin list . \
    | xargs -I _ git-recycle-bin download --force . _
    ls ../tmp
    ls .
    @rm -rf ../tmp

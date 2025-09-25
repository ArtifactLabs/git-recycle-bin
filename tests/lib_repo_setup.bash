setup_src_remote_repo() {
    (
        cd "${SRC_REMOTE_SERVER}"
        info "Setting up source remote repository..."
        git init --bare . >/dev/null 2>&1
    )
}

setup_artifact_repo() {
    (
        cd "${BIN_REMOTE_SERVER}"
        info "Setting up artifact repository..."
        git init --bare . >/dev/null 2>&1
    )
}

setup_shared_src_history() {
    (
        cd "${SRC_SHARED_HISTORY}"
        info "Setting up common shared source history..."
        git init . >/dev/null 2>&1
        git config user.name "All users before"
        git config user.email "maintainer@example.com"

        # Create an initial commit
        echo "Initial content" > readme.md
        git add readme.md
        git commit -m "Initial commit"

        # Add a Hello World C program
        cat > hello.c << 'EOF'
            #include <stdio.h>
            int main() { printf("Hello, World!\n"); return 0; }
EOF
        git add hello.c
        git commit -m "Highly complex Hello World C program"

        # Add remote and push to establish history
        git remote add origin "${SRC_REMOTE_SERVER}"
        git push -u origin master
        
        info "Established common source code history on ${SRC_REMOTE_SERVER}"
    )
}

setup_publisher_repo() {
    (
        cd "${SRC_USER1_PUBLISHER}"
        info "Setting up publisher repository (User1)..."
        # Clone from the shared source history
        git clone "${SRC_REMOTE_SERVER}" . >/dev/null 2>&1
        git config user.name "User 1"
        git config user.email "user1@example.com"
    )
}

setup_consumer_repo() {
    (
        cd "${SRC_USER2_CONSUMER}"
        info "Setting up consumer repository (User2)..."
        # Clone from the shared source history
        git clone "${SRC_REMOTE_SERVER}" . >/dev/null 2>&1
        git config user.name "User 2"
        git config user.email "user2@example.com"
    )
}

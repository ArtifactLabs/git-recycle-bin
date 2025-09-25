# Build from source to create build-artifacts
# Built artifacts are not committed to the source repo, but are pushed to the artifact repo
publisher__make_artifacts() {
    (
        cd "${SRC_USER1_PUBLISHER}"
        info "Creating artifacts in publisher repository..."

        # Compile the Hello World program
        gcc hello.c -o a.out
        chmod +x a.out
        info "Compiled hello.c into a.out executable"

        # Imagine some other complex build artifacts
        mkdir -p build/subdir
        echo "Test file 1" > build/file1.txt
        echo "Test file 2" > build/file2.txt
        echo "Subdir file" > build/subdir/file3.txt

        # Note: We intentionally don't commit these files
        # as they represent artifacts that should be handled by git-recycle-bin
        # rather than being committed to the source repo
    )
}

# Run the push command to push artifacts
publisher__push_artifacts() {
    (
        cd "${SRC_USER1_PUBLISHER}"
        info "Pushing artifacts using git-recycle-bin..."

        # Push compiled executable artifact
        (set -x; git_recycle_bin.py push "${BIN_REMOTE_SERVER}" --path a.out --name "executable-artifact")

        # Push directory artifact
        (set -x; git_recycle_bin.py push "${BIN_REMOTE_SERVER}" --path build --name "dir-artifact")

        # Optional: List all artifacts to verify
        info "Listing artifacts:"
        (set -x; git_recycle_bin.py list "${BIN_REMOTE_SERVER}")
    )
}

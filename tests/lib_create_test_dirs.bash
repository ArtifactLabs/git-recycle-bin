# Create all temporary directories
create_test_dirs() {
    info "Creating test directories..."

    mkdir -p "${TEST_DIR_PREFIX}/src"
    mkdir -p "${TEST_DIR_PREFIX}/bin"

    # Temporary directory for setting up the shared source history between user1 and user2
    SRC_SHARED_HISTORY="$(mktemp -d ${TEST_DIR_PREFIX}/src/shared-history-XXXX)"
    
    # CI or local user who builds+pushes artifacts
    SRC_USER1_PUBLISHER="$(mktemp -d ${TEST_DIR_PREFIX}/src/publisher-local-XXXX)"
    # CI local user who wants artifacts (so they can skip building themselves)
    SRC_USER2_CONSUMER="$(mktemp -d ${TEST_DIR_PREFIX}/src/consumer-local-XXXX)"

    # Authoritative central source code remote server. Bare repo, i.e. has no checkout
    SRC_REMOTE_SERVER="$(mktemp -d ${TEST_DIR_PREFIX}/src/source-server-XXXX.git)"

    # Authoritative central artifact repo. Bare repo, i.e. has no checkout
    BIN_REMOTE_SERVER="$(mktemp -d ${TEST_DIR_PREFIX}/bin/artifact-server-XXXX.git)"

    info "Shared history:   '${SRC_SHARED_HISTORY}' - temporary repo for initial history"
    info "User1 local:      '${SRC_USER1_PUBLISHER}' - builds+pushes artifacts"
    info "Source remote:    '${SRC_REMOTE_SERVER}' - stores the source code"
    info "Artifact remote:  '${BIN_REMOTE_SERVER}' - stores the artifacts"
    info "User2 local:      '${SRC_USER2_CONSUMER}' - downloads artifacts to skip builds"
}

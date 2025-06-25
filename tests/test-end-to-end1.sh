#!/usr/bin/env bash
# Integration test script for git-recycle-bin
# Tests the end-to-end flow of pushing and downloading artifacts

# Add script directory to PATH and source common messaging functions
PATH="$(dirname "${BASH_SOURCE[0]}"):${PATH}"
# shellcheck disable=SC1091
source lib_msg.bash
# shellcheck disable=SC1091
source lib_export_test_dir.bash
# shellcheck disable=SC1091
source lib_create_test_dirs.bash
# shellcheck disable=SC1091
source lib_repo_setup.bash
# shellcheck disable=SC1091
source lib_publisher.bash
# shellcheck disable=SC1091
source lib_consumer.bash
# shellcheck disable=SC1091
source lib_verify.bash

{
    # Using a fresh directory from mktemp each time, no cleanup needed
    create_test_dirs

    info "Setting up test repositories..."
    setup_src_remote_repo
    setup_artifact_repo
    setup_shared_src_history
    setup_publisher_repo
    setup_consumer_repo

    # First build+push artifacts in the publisher repository
    publisher__make_artifacts
    publisher__push_artifacts        
    # Then download and verify in the consumer repository
    consumer__download_all_artifacts1

    # Then verify in both repositories, that we have the artifacts at same relative locations
    verify_executable_artifact "${SRC_USER1_PUBLISHER}" # sanity check
    verify_directory_artifact "${SRC_USER1_PUBLISHER}"  # sanity check
    verify_executable_artifact "${SRC_USER2_CONSUMER}" # actual test
    verify_directory_artifact "${SRC_USER2_CONSUMER}"  # actual test

    success "All integration tests passed!"
}

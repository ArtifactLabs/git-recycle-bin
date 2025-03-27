# Download artifacts
consumer__download_all_artifacts1() {
    (
        cd "${SRC_USER2_CONSUMER}"
        info "Downloading artifacts..."
        
        # Get all artifact SHAs
        ARTIFACTS_INFO=$(set -x;git_recycle_bin.py list "${BIN_REMOTE_SERVER}")
        ARTIFACT_SHAS=$(echo "${ARTIFACTS_INFO}" | awk '{print $1}')
        
        # Download all artifacts without filtering
        if [ -n "${ARTIFACT_SHAS}" ]; then
            for SHA in ${ARTIFACT_SHAS}; do
                info "Downloading artifact ${SHA}..."
                (set -x; git_recycle_bin.py download "${BIN_REMOTE_SERVER}" "${SHA}")
            done
        else
            error "No artifacts found to download"
        fi
    )
}

# Download artifacts
consumer__download_all_artifacts2() {
    (
        cd "${SRC_USER2_CONSUMER}"

        info "Querying server for available artifacts..."
        artifact_sha_exe=$(git_recycle_bin.py list "${BIN_REMOTE_SERVER}" --name "executable-artifact")
        artifact_sha_dir=$(git_recycle_bin.py list "${BIN_REMOTE_SERVER}" --name "dir-artifact")
        
        info "Downloading all available artifacts..."
        (set -x; git_recycle_bin.py download "${BIN_REMOTE_SERVER}" "${artifact_sha_exe}")
        (set -x; git_recycle_bin.py download "${BIN_REMOTE_SERVER}" "${artifact_sha_dir}")
    )
}

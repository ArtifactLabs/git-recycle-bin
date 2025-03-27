# Verify the executable artifact
verify_executable_artifact() {
    local dir_to_check="$1"
    local dir_name="$(basename "${dir_to_check}")"
    
    info "Verifying executable artifact in ${dir_name}..."

    # Check executable artifact
    if [ -f "${dir_to_check}/a.out" ]; then
        # Check if the file is executable
        if [ -x "${dir_to_check}/a.out" ]; then
            success "Executable artifact verified successfully in ${dir_name} (exists and is executable)"
        else
            error "Executable artifact in ${dir_name} is not executable"
        fi
    else
        error "Executable artifact was not found in ${dir_name}"
    fi
}

# Verify the directory artifact
verify_directory_artifact() {
    local dir_to_check="$1"
    local dir_name="$(basename "${dir_to_check}")"
    
    info "Verifying directory artifact in ${dir_name}..."

    # Check directory artifact
    if [ -d "${dir_to_check}/build" ]; then
        if [ "$(cat "${dir_to_check}/build/file1.txt")" = "Test file 1" ] && \
           [ "$(cat "${dir_to_check}/build/file2.txt")" = "Test file 2" ] && \
           [ "$(cat "${dir_to_check}/build/subdir/file3.txt")" = "Subdir file" ]; then
            success "Directory artifact verified successfully in ${dir_name}"
        else
            error "Directory artifact content verification failed in ${dir_name}"
        fi
    else
        error "Directory artifact was not found in ${dir_name}"
    fi
}

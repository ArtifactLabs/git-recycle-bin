#!/usr/bin/env bash
# Description:
# This script adds a new SSH remote with "_ssh" suffix to a Git repository
# that currently uses HTTPS for its remote. It's useful for several reasons:
#
# 1. Authentication: SSH uses key-based authentication, eliminating the need
#    for entering passwords or using personal access tokens.
# 2. Firewall friendliness: Some networks restrict HTTPS but allow SSH.
# 3. Convenience: Once set up, SSH doesn't require repeated authentication
#    or handling of tokens - just use your normal ssh keys.
#
# The script automatically converts the HTTPS URL to its SSH equivalent,
# stripping any authentication tokens in the process. This is particularly
# useful in CI/CD environments where HTTPS URLs might contain sensitive tokens.
#
# Usage: Run this script in a Git repository to add the SSH remote.
# After running, you can use 'git push origin_ssh <branch>' to push via SSH.
set -eu

# Show help if requested
show_help() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS] [REMOTE_NAME]

Add SSH remote with "_ssh" suffix to a Git repository, based on existing
(https) remote's URL.

E.g. if you have a remote named "origin" that is an https URL, this script
will add a new remote named "origin_ssh" that is the SSH equivalent of the
https URL.

Options:
  --help        Display this help message and exit

Arguments:
  REMOTE_NAME   Name of the remote to convert (default: origin)

Examples:
  $(basename "$0")           # Convert the 'origin' remote to SSH
  $(basename "$0") upstream  # Convert the 'upstream' remote to SSH
EOF
    exit 0
}

# Parse command line arguments
if [[ $# -gt 0 && "$1" == "--help" ]]; then
    show_help
fi

REMOTE_NAME="${1:-origin}"

# Function to extract the repository URL
get_repo_url() {
    git remote get-url "$1"
}

# Function to convert HTTPS URL to SSH URL and strip tokens
https_to_ssh() {
    local url="$1"
    # Breakdown:
    #   's#...#...#' : Substitution command, using # as delimiter
    #   https://     : Matches the protocol literally
    #   ([^@]+@)?    : Optionally matches and discards authentication token
    #   ([^/]+)      : Captures the domain name
    #   /            : Matches literal '/' after domain
    #   (.+)         : Captures everything else up to .git
    #   \.git$       : Matches .git at the end of the string
    # Replacement:
    #   git@ : Start of SSH URL format
    #   \2   : Second captured group (domain name)
    #   :    : Separator in SSH format
    #   \3   : Third captured group (repository path)
    #   .git : Appended at the end
    echo "$url" | sed -E 's#https://([^@]+@)?([^/]+)/(.+)\.git$#git@\2:\3.git#'
}

# Get the current HTTPS URL
remote_url=$(get_repo_url "${REMOTE_NAME}")

# Check if it's already an SSH URL
if [[ $remote_url == git@* ]]; then
    echo "The remote URL is already in SSH format. Adding ${REMOTE_NAME}_ssh as an alias anyway." 1>&2
    git remote add "${REMOTE_NAME}_ssh" "$remote_url" 2>/dev/null || true
else
    # Convert to SSH URL
    ssh_url=$(https_to_ssh "$remote_url")
    # Add new remote
    git remote add "${REMOTE_NAME}_ssh" "$ssh_url" 2>/dev/null || true
fi

echo "Remote '${REMOTE_NAME}_ssh' added: $(git remote get-url "${REMOTE_NAME}_ssh")" 1>&2

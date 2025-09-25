#!/usr/bin/env bash
# Test script for git_add_ssh_remote.sh

set -u  # Treat unset variables as errors

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
AUX_DIR="${PROJECT_ROOT}/aux"

# Script to test (Device Under Test)
DUT_SCRIPT="${AUX_DIR}/git_add_ssh_remote.sh"

# Create a shared temp directory for all tests
TEST_TMP_DIR="$(mktemp -d)"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test counter
TESTS_TOTAL=0
TESTS_PASSED=0

################

# Create a test repo with the specified remote URL
create_test_repo() {
    local test_dir="$1"
    local remote_url="$2"
    local remote_name="${3:-origin}"

    mkdir -p "${test_dir}"
    cd "${test_dir}" || exit

    # Initialize repo
    git init > /dev/null 2>&1

    # Create a test file and commit it
    echo "test content" > test.txt
    git add test.txt
    git config --local user.email "test@example.com"
    git config --local user.name "Test User"
    git commit -m "Initial commit" > /dev/null

    # Add the remote
    git remote add "${remote_name}" "${remote_url}"
}

################ 

# Function to run a single test
run_test() {
    local test_dir="$1"
    local test_name="$2"
    local expected="$3"
    local remote="${4:-origin}"

    # Capture both stdout and stderr
    local output
    output=$(cd "${test_dir}" && bash "${DUT_SCRIPT}" "${remote}" 2>&1)
    local dut_exit_code=$?

    if [[ ${dut_exit_code} -eq 0 ]]; then
        local remote_url
        remote_url=$(cd "${test_dir}" && git remote get-url "${remote}" 2>&1)
        local remote_ssh_url
        remote_ssh_url=$(cd "${test_dir}" && git remote get-url "${remote}_ssh" 2>&1)
        local get_url_exit=$?

        if [[ ${get_url_exit} -eq 0 && "${remote_ssh_url}" == "${expected}" ]]; then
            echo -e "${GREEN}PASS${NC}: ${test_name}:"
            echo -e "    Old ${remote}     := '${remote_url}'."
            echo -e "    New ${remote}_ssh := '${remote_ssh_url}'."
            return 0
        else
            echo -e "${RED}FAIL${NC}: ${test_name}:"
            echo -e "    Old ${remote}     := '${remote_url}'."
            echo -e "    New ${remote}_ssh := '${remote_ssh_url}' but expected '${expected}'."
            return 1
        fi
    else
        echo -e "${RED}FAIL${NC}: ${test_name}: DUT script failed with exit code ${dut_exit_code}"
        return 1
    fi
}

################ Individual test functions

test_convert_https_to_ssh() {
    local test_dir
    test_dir="$(mktemp -d "${TEST_TMP_DIR}/${FUNCNAME[0]}_XXXX")"
    create_test_repo "${test_dir}" "https://github.com/username/repo.git"
    run_test "${test_dir}" "Convert HTTPS to SSH" "git@github.com:username/repo.git"
}

test_already_ssh() {
    local test_dir
    test_dir="$(mktemp -d "${TEST_TMP_DIR}/${FUNCNAME[0]}_XXXX")"
    create_test_repo "${test_dir}" "git@github.com:username/repo.git"
    run_test "${test_dir}" "Already SSH" "git@github.com:username/repo.git"
}

test_custom_remote_name() {
    local test_dir
    test_dir="$(mktemp -d "${TEST_TMP_DIR}/${FUNCNAME[0]}_XXXX")"
    local remote_name="upstream"
    create_test_repo "${test_dir}" "https://github.com/username/repo.git" "${remote_name}"
    run_test "${test_dir}" "Custom remote name" "git@github.com:username/repo.git" "${remote_name}"
}

test_https_with_auth_token() {
    local test_dir
    test_dir="$(mktemp -d "${TEST_TMP_DIR}/${FUNCNAME[0]}_XXXX")"
    create_test_repo "${test_dir}" "https://token@github.com/username/repo.git"
    run_test "${test_dir}" "HTTPS with auth token" "git@github.com:username/repo.git"
}

test_git_protocol() {
    local test_dir
    test_dir="$(mktemp -d "${TEST_TMP_DIR}/${FUNCNAME[0]}_XXXX")"
    create_test_repo "${test_dir}" "git://github.com/username/repo.git"
    run_test "${test_dir}" "Git protocol" "git://github.com/username/repo.git"  # no change expected
}

test_ssh_with_protocol() {
    local test_dir
    test_dir="$(mktemp -d "${TEST_TMP_DIR}/${FUNCNAME[0]}_XXXX")"
    create_test_repo "${test_dir}" "ssh://git@github.com/username/repo.git"
    run_test "${test_dir}" "SSH with protocol" "ssh://git@github.com/username/repo.git"  # no change expected
}

test_gerrit_ssh_url() {
    local test_dir
    test_dir="$(mktemp -d "${TEST_TMP_DIR}/${FUNCNAME[0]}_XXXX")"
    create_test_repo "${test_dir}" "ssh://username@gerrit.example.com:29418/project/repository.git"
    run_test "${test_dir}" "Gerrit SSH URL with port" "ssh://username@gerrit.example.com:29418/project/repository.git"  # no change expected
}

test_https_with_credentials() {
    local test_dir
    test_dir="$(mktemp -d "${TEST_TMP_DIR}/${FUNCNAME[0]}_XXXX")"
    create_test_repo "${test_dir}" "https://username:password@github.com/username/repo.git"
    run_test "${test_dir}" "HTTPS with username/password" "git@github.com:username/repo.git"
}

test_subdirectory_path() {
    local test_dir
    test_dir="$(mktemp -d "${TEST_TMP_DIR}/${FUNCNAME[0]}_XXXX")"
    create_test_repo "${test_dir}" "https://github.com/org/subgroup/repo.git"
    run_test "${test_dir}" "Repository in subdirectory" "git@github.com:org/subgroup/repo.git"
}

test_help_option() {
    local output
    output=$(bash "${DUT_SCRIPT}" --help 2>&1)
    
    if [[ $? -eq 0 && "${output}" == *"Usage:"* && "${output}" == *"Options:"* ]]; then
        echo -e "${GREEN}PASS${NC}: Help option displays usage information"
        return 0
    else
        echo -e "${RED}FAIL${NC}: Help option test failed"
        echo "Got output: ${output}"
        return 1
    fi
}

################

{
    test_convert_https_to_ssh && ((TESTS_PASSED++))
    test_already_ssh && ((TESTS_PASSED++))
    test_custom_remote_name && ((TESTS_PASSED++))
    test_https_with_auth_token && ((TESTS_PASSED++))
    test_git_protocol && ((TESTS_PASSED++))
    test_ssh_with_protocol && ((TESTS_PASSED++))
    test_gerrit_ssh_url && ((TESTS_PASSED++))
    test_https_with_credentials && ((TESTS_PASSED++))
    test_subdirectory_path && ((TESTS_PASSED++))
    test_help_option && ((TESTS_PASSED++))
}

################

TESTS_TOTAL=10
echo -e "Tests passed: ${TESTS_PASSED}/${TESTS_TOTAL}"

if [[ "${TESTS_PASSED}" -eq "${TESTS_TOTAL}" ]]; then
    echo -e "${GREEN}All tests passed!${NC}"
    rm -rf "${TEST_TMP_DIR}"
    exit 0
else
    echo -e "${RED}Some tests failed!${NC}"
    echo "Test directories are left in ${TEST_TMP_DIR} for debugging"
    exit 1
fi

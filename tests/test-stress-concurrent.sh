#!/usr/bin/env bash
# Stress test for git-recycle-bin with concurrent producers and consumers
# Tests race conditions in artifact creation, expiration, and cleanup
#
# WORKING PRINCIPLE:
# ==================
# This stress test creates a high-concurrency environment to expose potential race
# conditions in git-recycle-bin's artifact management system. The test works by:
#
# 1. CONCURRENT PRODUCERS (default: 30)
#    - Each producer runs in a separate process with its own git repository
#    - Creates artifacts with unique content and short expiry times (5 seconds)
#    - Uses random timing delays to increase collision probability
#    - Pushes artifacts to the same shared artifact repository simultaneously
#    - Tests the system's ability to handle concurrent branch creation and updates
#
# 2. CONCURRENT CONSUMERS (default: 15) 
#    - Each consumer runs in a separate process
#    - Continuously lists available artifacts and attempts downloads
#    - Handles graceful failures when artifacts expire during download
#    - Uses random timing to create unpredictable access patterns
#    - Tests concurrent read operations and artifact retrieval
#
# 3. BACKGROUND CLEANER (single process)
#    - Runs periodic 'clean' operations every 3 seconds
#    - Tests expiration logic under concurrent load
#    - Ensures expired artifacts are properly removed while new ones are being created
#    - Tests the system's ability to safely clean up while other operations are active
#
# 4. RACE CONDITIONS TESTED:
#    - Multiple processes creating branches with similar names simultaneously
#    - Concurrent access to git repository during push/list/download operations  
#    - Expiration and cleanup racing with ongoing artifact creation
#    - Git repository integrity under high concurrent load
#    - Orphan branch creation and management with many simultaneous operations
#
# 5. VERIFICATION:
#    - Repository integrity check (git fsck) after stress test
#    - Functional verification that basic operations still work
#    - Final cleanup to ensure expiration logic remains functional
#
# The high concurrency (30+ processes) maximizes the chances of exposing timing
# issues, deadlocks, or corruption that might only appear under heavy load.

# Add script directory to PATH and source common messaging functions
PATH="$(dirname "${BASH_SOURCE[0]}"):${PATH}"
# Ensure we have git-recycle-bin in PATH
PATH="$(dirname "$(which git_recycle_bin.py)"):${PATH}"
source lib_msg.bash
source lib_export_test_dir.bash
source lib_create_test_dirs.bash
source lib_repo_setup.bash

# Configuration for stress test parameters - optimized for high concurrency
readonly NUM_PRODUCERS=${NUM_PRODUCERS:-30}
readonly NUM_CONSUMERS=${NUM_CONSUMERS:-15}
readonly NUM_ARTIFACTS_PER_PRODUCER=${NUM_ARTIFACTS_PER_PRODUCER:-10}
readonly EXPIRE_TIME=${EXPIRE_TIME:-"5 seconds"}
readonly TEST_DURATION=${TEST_DURATION:-30}

# Arrays to track producer and consumer PIDs
PRODUCER_PIDS=()
CONSUMER_PIDS=()

# Cleanup function to kill all background processes
cleanup_stress_test() {
    info "Cleaning up stress test processes..."
    
    # Kill all producer processes
    for pid in "${PRODUCER_PIDS[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid" || true
        fi
    done
    
    # Kill all consumer processes  
    for pid in "${CONSUMER_PIDS[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid" || true
        fi
    done
    
    # Wait for processes to terminate
    wait || true
}

# Set up cleanup trap
trap cleanup_stress_test EXIT INT TERM

# Create a producer that continuously creates and pushes artifacts
stress_producer() {
    local producer_id=$1
    local producer_dir="${TEST_DIR_PREFIX}/src/producer-${producer_id}"
    local log_file="${TEST_DIR_PREFIX}/producer-${producer_id}.log"
    
    # Redirect all output to per-worker log file with timestamps and worker ID
    exec &> >(ts '[%.s] [P'${producer_id}']' | tee -a "$log_file")
    
    # Clone from shared history to get a working repository
    git clone "${SRC_SHARED_HISTORY}" "${producer_dir}"
    cd "${producer_dir}"
    
    # Configure git for this producer
    git config user.name "Producer ${producer_id}"
    git config user.email "producer${producer_id}@test.local"
    
    # Add remote pointing to source server
    git remote add origin "${SRC_REMOTE_SERVER}"
    
    info "Producer ${producer_id} starting in ${producer_dir}"
    
    local artifact_count=0
    while [[ $artifact_count -lt $NUM_ARTIFACTS_PER_PRODUCER ]]; do
        # Create unique artifact content
        local artifact_name="artifact-p${producer_id}-${artifact_count}"
        local artifact_file="build-${artifact_count}.txt"
        
        # Create artifact with unique content and timestamp
        echo "Producer ${producer_id} - Artifact ${artifact_count} - $(date)" > "${artifact_file}"
        echo "Random data: $RANDOM-$RANDOM-$RANDOM" >> "${artifact_file}"
        
        # Push artifact with short expiry to test cleanup
        local push_cmd="git_recycle_bin.py -vv push \"${BIN_REMOTE_SERVER}\" --path \"${artifact_file}\" --name \"${artifact_name}\" --expire \"${EXPIRE_TIME}\""
        if eval "$push_cmd"; then
            info "Producer ${producer_id}: pushed ${artifact_name}"
        else
            error "Producer ${producer_id}: failed to push ${artifact_name} (cmd: $push_cmd)"
        fi
        
        # Create some timing variation to increase chances of race conditions
        sleep "0.$(($RANDOM % 500 + 100))" # 0.1 to 0.6 seconds
        
        ((artifact_count++))
    done
    
    info "Producer ${producer_id} completed ${NUM_ARTIFACTS_PER_PRODUCER} artifacts"
}

# Create a consumer that continuously lists and downloads artifacts
stress_consumer() {
    local consumer_id=$1
    local consumer_dir="${TEST_DIR_PREFIX}/src/consumer-${consumer_id}"
    local log_file="${TEST_DIR_PREFIX}/consumer-${consumer_id}.log"
    
    # Redirect all output to per-worker log file with timestamps and worker ID
    exec &> >(ts '[%.s] [C'${consumer_id}']' | tee -a "$log_file")
    
    # Clone from shared history to get a working repository
    git clone "${SRC_SHARED_HISTORY}" "${consumer_dir}"
    cd "${consumer_dir}"
    
    # Configure git for this consumer
    git config user.name "Consumer ${consumer_id}"
    git config user.email "consumer${consumer_id}@test.local"
    
    info "Consumer ${consumer_id} starting in ${consumer_dir}"
    
    local download_count=0
    local start_time=$(date +%s)
    
    while [[ $(($(date +%s) - start_time)) -lt $TEST_DURATION ]]; do
        # List available artifacts
        local artifacts
        local list_cmd="git_recycle_bin.py -vv list \"${BIN_REMOTE_SERVER}\""
        if artifacts=$(eval "$list_cmd"); then
            if [[ -n "$artifacts" ]]; then
                # Pick a random artifact SHA from the list
                local artifact_sha
                artifact_sha=$(echo "$artifacts" | head -n $(($RANDOM % 5 + 1)) | tail -n 1)
                
                if [[ -n "$artifact_sha" ]]; then
                    # Try to download the artifact
                    local download_cmd="git_recycle_bin.py -vv download \"${BIN_REMOTE_SERVER}\" \"$artifact_sha\""
                    if eval "$download_cmd"; then
                        info "Consumer ${consumer_id}: downloaded ${artifact_sha:0:8}..."
                        ((download_count++))
                    else
                        # Artifact might have expired or been cleaned up - this is expected
                        debug "Consumer ${consumer_id}: failed to download ${artifact_sha:0:8}... (possibly expired) (cmd: $download_cmd)"
                    fi
                fi
            fi
        else
            debug "Consumer ${consumer_id}: failed to list artifacts (cmd: $list_cmd)"
        fi
        
        # Vary timing to create race conditions
        sleep "0.$(($RANDOM % 300 + 50))" # 0.05 to 0.35 seconds
    done
    
    info "Consumer ${consumer_id} completed ${download_count} downloads"
}

# Run periodic cleanup to test expiration under load
stress_cleaner() {
    local log_file="${TEST_DIR_PREFIX}/cleaner.log"
    
    # Redirect all output to per-worker log file with timestamps and worker ID
    exec &> >(ts '[%.s] [CLEANER]' | tee -a "$log_file")
    
    info "Cleaner process starting"
    local start_time=$(date +%s)
    
    while [[ $(($(date +%s) - start_time)) -lt $TEST_DURATION ]]; do
        # Run cleanup on expired artifacts
        local clean_cmd="git_recycle_bin.py -vv clean \"${BIN_REMOTE_SERVER}\""
        if eval "$clean_cmd"; then
            debug "Cleaner: ran cleanup cycle"
        else
            debug "Cleaner: cleanup cycle failed (cmd: $clean_cmd)"
        fi
        
        # Clean every few seconds
        sleep 3
    done
    
    info "Cleaner process completed"
}

# Main stress test function
run_stress_test() {
    info "Starting HIGH CONCURRENCY stress test with ${NUM_PRODUCERS} producers, ${NUM_CONSUMERS} consumers"
    info "Test parameters: ${NUM_ARTIFACTS_PER_PRODUCER} artifacts/producer, ${EXPIRE_TIME} expiry, ${TEST_DURATION}s duration"
    info "Total concurrent processes: $((NUM_PRODUCERS + NUM_CONSUMERS + 1)) (including cleaner)"
    
    # Start producer processes in background
    for ((i=1; i<=NUM_PRODUCERS; i++)); do
        stress_producer "$i" &
        PRODUCER_PIDS+=($!)
    done
    
    # Start consumer processes in background
    for ((i=1; i<=NUM_CONSUMERS; i++)); do
        stress_consumer "$i" &
        CONSUMER_PIDS+=($!)
    done
    
    # Start cleaner process
    stress_cleaner &
    local cleaner_pid=$!
    
    # Wait for all producers to complete
    info "Waiting for producers to complete..."
    for pid in "${PRODUCER_PIDS[@]}"; do
        wait "$pid"
    done
    info "All producers completed"
    
    # Let consumers run for the full test duration
    info "Waiting for consumers and cleaner to complete..."
    wait "$cleaner_pid"
    
    # Stop consumers
    for pid in "${CONSUMER_PIDS[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid" || true
        fi
    done
    
    # Wait for consumers to stop
    for pid in "${CONSUMER_PIDS[@]}"; do
        wait "$pid" || true
    done
    
    info "Stress test completed"
}

# Verify repository integrity after stress test
verify_repository_integrity() {
    info "Verifying repository integrity..."
    
    # Check that git repository is still functional
    cd "${TEST_DIR_PREFIX}"
    if ! git -C "${BIN_REMOTE_SERVER}" fsck --full; then
        error "Repository integrity check failed!"
        return 1
    fi
    
    # Check that we can still perform basic operations
    local list_cmd="git_recycle_bin.py -vv list \"${BIN_REMOTE_SERVER}\""
    if ! eval "$list_cmd"; then
        error "Post-stress list operation failed! (cmd: $list_cmd)"
        return 1
    fi
    
    # Final cleanup to test expiration logic
    local clean_cmd="git_recycle_bin.py -vv clean \"${BIN_REMOTE_SERVER}\""
    if ! eval "$clean_cmd"; then
        error "Post-stress cleanup operation failed! (cmd: $clean_cmd)"
        return 1
    fi
    
    success "Repository integrity verified"
}

# Main test execution
{
    # Create test environment
    create_test_dirs
    
    info "Setting up test repositories for stress testing..."
    setup_src_remote_repo
    setup_artifact_repo  
    setup_shared_src_history
    
    # Run the stress test
    run_stress_test
    
    # Verify everything is still working
    verify_repository_integrity
    
    success "Stress test completed successfully!"
    
    # Print final statistics
    info "Final artifact count:"
    local final_count
    final_count=$(git_recycle_bin.py -vv list "${BIN_REMOTE_SERVER}" | wc -l)
    info "Artifacts remaining: ${final_count}"
    
    # List log files created
    info "Log files created:"
    find "${TEST_DIR_PREFIX}" -name "*.log" -type f | while read -r logfile; do
        local size=$(wc -l < "$logfile")
        info "  $logfile ($size lines)"
    done
}
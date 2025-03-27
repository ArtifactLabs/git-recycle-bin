#!/usr/bin/env bash
# Library for creating and exporting test directories
# This establishes a consistent temporary directory structure for tests

# Define a stable prefix for test directories
# User-specific directory early on, so users won't clobber each other's tests or permissions
export COMMON_TEST_DIR_PREFIX="/tmp/${USER:-$(whoami)}/gitrb-test"
# Ephemeral test directory for this particular test run
export TEST_DIR_PREFIX="${COMMON_TEST_DIR_PREFIX}/$(date +%Y%m%d-%H%M%S)-$$-$RANDOM"
mkdir -p "${TEST_DIR_PREFIX}"

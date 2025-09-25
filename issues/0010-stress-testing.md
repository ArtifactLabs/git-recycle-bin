# Stress testing under heavy load

## Purpose

Evaluate behaviour when many clients push and pull artifacts
in parallel to uncover race conditions in expiration logic.

## Acceptance Criteria

- ✅ Tests simulate concurrent producers and consumers with expiring artifacts.
- ✅ System remains stable and cleans up expired data correctly.
- ✅ Tests reuse existing bash framework for consistency.
- ✅ Configurable test parameters for different stress levels.

## Prerequisites

- ✅ Functioning concurrency in existing commands.

## Implementation Details

Created `tests/test-stress-concurrent.sh` that implements:

**Concurrent Producers:**
- Configurable number of producer processes (default: 5)
- Each creates and pushes multiple artifacts with short expiry times
- Random timing variations to increase race condition probability
- Unique artifact content per producer to avoid conflicts

**Concurrent Consumers:**
- Configurable number of consumer processes (default: 3)  
- Continuously list and download available artifacts
- Handle graceful failures when artifacts expire during download
- Random timing to create unpredictable access patterns

**Continuous Cleanup:**
- Background cleaner process runs periodic `clean` operations
- Tests expiration logic under concurrent load
- Ensures expired artifacts are properly removed

**Test Configuration:**
- `NUM_PRODUCERS`: Number of concurrent producers (default: 5)
- `NUM_CONSUMERS`: Number of concurrent consumers (default: 3)
- `NUM_ARTIFACTS_PER_PRODUCER`: Artifacts per producer (default: 10)
- `EXPIRE_TIME`: Artifact expiry time (default: "5 seconds")
- `TEST_DURATION`: Test duration in seconds (default: 30)

**Integration:**
- Added `just test_stress` recipe to justfile
- Reuses existing bash test framework (`lib_*.bash` modules)
- Includes repository integrity verification after stress test
- Proper cleanup of background processes

## Questions

- ✅ How should we coordinate workers to trigger potential races?
  **Answer:** Use random timing variations and overlapping operations with short expiry times.

## Status

✅ **DONE** - Comprehensive stress testing implemented

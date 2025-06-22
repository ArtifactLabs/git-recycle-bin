# BASH integration tests for cross-repository functionality

## Purpose

Create comprehensive BASH-based integration tests that validate the
complete push/download workflow across separate Git repositories to
prove end-to-end functionality works correctly.

## Acceptance Criteria

- BASH test scripts that create temporary Git repositories and test
  artifact push from one repo and download from another
- Tests verify that artifacts can be successfully pushed to a remote
  repository and then downloaded from a different local repository
- Integration tests cover various scenarios: different artifact types,
  expiry dates, and metadata handling
- Tests are runnable from justfile and integrated into CI pipeline
- Tests clean up temporary repositories after completion
- All integration tests must pass before merging changes to core
  functionality

## Prerequisites

- Unit tests must be stable and passing
- Core push/download functionality must be working
- Test infrastructure in place (justfile, CI configuration)

## Questions

- Should tests use real Git remotes or mock/local bare repositories?
- How should we handle test isolation and cleanup of temporary repos?
- What artifact types and scenarios should be prioritized for testing?

## Status

Open

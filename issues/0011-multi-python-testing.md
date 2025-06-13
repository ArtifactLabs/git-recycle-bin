# Multi-version Python testing

## Purpose
Ensure the codebase remains compatible across supported Python
releases by running the test suite against each version.

## Acceptance Criteria
- CI matrix covers Python 3.8 through 3.11 at minimum.
- All versions pass the same tests without conditional skips.

## Prerequisites
- Tests rely only on functionality present in all targeted versions.

## Questions
- When should we remove older Python versions from the matrix?

## Status
Open

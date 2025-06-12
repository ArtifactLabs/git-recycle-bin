# Convert tools into a reusable library

## Purpose
Make the artifact management functionality available as an importable
library so other projects can reuse it programmatically.

## Acceptance Criteria
- Package exposes stable APIs for listing, pushing and cleaning
  artifacts.
- CLI continues to operate using those APIs.

## Prerequisites
- Codebase currently implemented as command line scripts.

## Questions
- Which parts of the API need to remain backwards compatible?

## Status
Open

# Support for non-expiring artifacts

## Purpose

Keep certain artifacts forever, acting as releases or long-term
checkpoints that never expire.

## Acceptance Criteria

- Command line flag or configuration to mark an artifact as permanent.
- Garbage collection leaves these artifacts intact.

## Prerequisites

- Current pruning mechanism based on absolute expiry dates.

## Questions

- Should permanent artifacts be stored in a separate namespace?

## Status

Open

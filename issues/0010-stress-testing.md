# Stress testing under heavy load

## Purpose

Evaluate behaviour when many clients push and pull artifacts
in parallel to uncover race conditions in expiration logic.

## Acceptance Criteria

- Tests simulate concurrent producers and consumers with
  expiring artifacts.
- System remains stable and cleans up expired data correctly.

## Prerequisites

- Functioning concurrency in existing commands.

## Questions

- How should we coordinate workers to trigger potential races?

## Status

Open

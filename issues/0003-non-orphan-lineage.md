# Non-orphan branch lineage preservation

## Purpose

Allow artifact branches to retain the source commit as their parent so the
relationship between source and artifact is visible in normal history.

## Acceptance Criteria

- New option to create artifact branches with a parent commit.
- Lineage clearly shown when running standard git history commands.

## Prerequisites

- Understanding of how orphan branches are currently produced.

## Questions

- Should lineage branches be enabled by default or remain optional?

## Status

Open

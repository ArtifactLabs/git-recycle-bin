# Git notes integration for artifact discovery

## Purpose

Allow discovery of binary artifacts by storing metadata under
`git notes`.

## Acceptance Criteria

- Dedicated namespace such as `refs/notes/artifact/<TARGET>` or
  `refs/notes/artifact/<BIN_REMOTE>/<TARGET>` stores a note for each
  relevant commit.
- Notes contain sorted JSON lines describing the artifact:
  `{date:<BIN_SHA_COMMIT_DATE>, sha:<BIN_SHA>, target:<TARGET>, ttl:<TTL>,
  remote:<BIN_REMOTE>}`.
- CLI commands expose creation and reading of notes.

## Prerequisites

- Familiarity with `git notes` and the project's artifact scheme.

## Questions

- Should notes also capture artifact expiry information?

## Status

Done. Implementation was completed in commit `5ef2128` and described
in `design_notes.txt`.

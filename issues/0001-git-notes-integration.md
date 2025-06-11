# Git notes integration for artifact discovery

## Background
`git notes` allows attaching auxiliary metadata to commits without changing commit hashes. The project now uses git notes to advertise available binary artifacts.

## Proposed design
- Maintain a dedicated notes namespace such as `refs/notes/artifact/<TARGET>` or `refs/notes/artifact/<BIN_REMOTE>/<TARGET>`. Each note will attach to the corresponding source commit SHA.
- Note contents will be sorted lines of simple JSON with fields:
  `{date:<BIN_SHA_COMMIT_DATE>, sha:<BIN_SHA>, target:<TARGET>, ttl:<TTL>, remote:<BIN_REMOTE>}`
- Clients can fetch and display these notes to discover artifacts related to a source commit without knowing the binary remote upfront.
- Additional helper commands will be added to create and read these notes when pushing or listing artifacts.

This issue tracked implementation of the git notes scheme described above and in `design_notes.txt`.
Implementation landed in commit 5ef2128.

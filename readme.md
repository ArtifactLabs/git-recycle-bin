# Git Recycle Bin ♻️

**Turn any git host into your own artifact vault**.
Store build outputs right alongside your source, skip costly rebuilds and keep complete traceability.

## Why adopt?

- 🌱 *Self-governed*: no special server software or enterprise tools required. Any git host works.
- ♻️ *Reuse binaries*: retrieve previous build artifacts and avoid unnecessary rebuilds.
- 🔍 *Full traceability*: artifacts are tied to the exact source commit via git notes.
- 🗑️ *Garbage collect*: expired artifacts vanish with `git gc`.

## Installation

### Using Nix

```bash
nix-shell --pure --run "just unittest"
```

This drops you into a shell with all dependencies. From there run the tools directly.

### Via pip

```bash
pip install git-recycle-bin
```

You can also install from a checkout with `pip install .` (tested in CI 🎉).

## Quick start

Push an artifact to a binary repository:

```bash
git_recycle_bin.py push \
    git@example.com:documentation/generated/rst_html.git \
    --path ../obj/doc/html \
    --name "Example-RST-Documentation" --tag
```
Push with expiry:

```bash
git_recycle_bin.py push . --path build --name demo --expire "in 1 hour"
```

Download an artifact back into your working tree:

```bash
git_recycle_bin.py list . | head -n 1 | \
    xargs -I _ git_recycle_bin.py download . _
```
List artifacts:

```bash
git_recycle_bin.py list . --name "Example-RST-Documentation"
```

## How it works

`git-recycle-bin` keeps artifacts in their own branches while associating them with commits using git notes.
Because notes are non-destructive, you can look up previous binaries and reuse them.
The name comes from the ability to recycle artifacts and eventually remove them when no longer needed.
CI pipelines can fetch a matching artifact and skip rebuilding altogether.

## Technical details

Artifacts include metadata stored as trailer fields in the commit message. Key fields:

* `artifact-schema-version`
* `artifact-name`
* `artifact-mime-type`
* `artifact-tree-prefix`
* `src-git-relpath`
* `src-git-commit-sha`
* `src-git-branch`
* `src-git-repo-url`

For a full schema see [issue #1](issues/0001-git-notes-integration.md).


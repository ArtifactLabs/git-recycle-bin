# Git Recycle Bin ♻️

**Turn any git host into your own artifact vault**.
Store build outputs right alongside your source and skip costly rebuilds while
keeping complete traceability.

## Why adopt?

- 🌱 *Self-governed*: no special server software or enterprise tools required.
  Any git host works.
- ♻️ *Reuse binaries*: retrieve previous build artifacts and avoid unnecessary rebuilds.
- 🔍 *Full traceability*: artifacts are tied to the exact source commit via git notes.
- 🗑️ *Garbage collect*: expired artifacts vanish with `git gc`.

## Installation

### Using Nix

Fetch this repository via `fetchgit` or add it as a submodule.
You can then build the package with `nix build` and find the executables under
`./result/bin`.
For a development shell run:

```bash
nix-shell
```

### Via pip

```bash
pip install git+https://github.com/your-org/git-recycle-bin.git
```

You can also install from a local checkout with:

```bash
pip install .
```
(tested in CI 🎉)

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

`git-recycle-bin` stores artifacts in dedicated branches and links them to source
commits using git notes.
Because notes are non-destructive, you can look up previous binaries and reuse them.
The name comes from the ability to recycle artifacts.
Stale ones can be removed when no longer needed.
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


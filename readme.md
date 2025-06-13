# Git Recycle Bin ♻️

[![CI](https://github.com/ArtifactLabs/git-recycle-bin/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/ArtifactLabs/git-recycle-bin/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/ArtifactLabs/git-recycle-bin/branch/master/graph/badge.svg)](https://codecov.io/gh/ArtifactLabs/git-recycle-bin)

**Use any other git repo as an artifact build cache** 🤯.
With bidirectional traceability 🎉!
Store build outputs right alongside your source and skip costly rebuilds while
keeping complete traceability.

## What is Git Recycle Bin?

Git Recycle Bin uses Git so you can manage build artifacts in a
separate repository while keeping a clear link back to the source that
produced them. Artifacts can be pushed, fetched and automatically
removed when they expire.

## Features

- Push build outputs to a dedicated artifact repository
- Preserve metadata linking artifacts back to the exact source commit
- Garbage collect artifacts using expiry dates
- Create `latest` tags for easy discovery
- Enable skipping builds by downloading pre-built artifacts
- Use git-notes so source repos know which binaries exist
- Operates locally or with any remote Git server using your existing git+ssh
  authentication
- Requires no additional setup or deployment of other services so you can use
  your existing Git infrastructure

## Why adopt?

- 🌱 *Self-governed*: no special server software or enterprise tools
  required. Any git host works.
- ♻️ *Reuse binaries*: retrieve previous build artifacts and avoid
  unnecessary rebuilds.
- 🔍 *Full traceability*: artifacts are tied to the exact source commit
  via git notes.
- 🗑️ *Garbage collect*: expired artifacts vanish with `git gc`.

## Principle of Operation

Artifacts are stored in orphan branches using a structured naming
scheme:

```text
artifact/expire/{EXPIRY_DATE}/{SOURCE_REPO}@{SOURCE_SHA}/{ARTIFACT_PATH}
```

`latest` tags point at the most recent artifact for a branch:

```text
artifact/latest/{SOURCE_REPO}@{SOURCE_BRANCH}/{ARTIFACT_PATH}
```

Metadata-only refs allow querying
information without downloading the full artifact tree. Git notes on
source commits advertise available artifacts and are used to implement
build avoidance.

## Installation

### Using Nix

```nix
{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
  buildInputs = [
    (pkgs.callPackage (pkgs.fetchFromGitHub {
      owner = "artifactLabs";
      repo = "git-recycle-bin";
      rev = "<commit>";
      sha256 = "<hash>";
    } + "/default.nix") {})
  ];
}
```

Then enter the shell:

```bash
nix-shell
```

### Via pip

```bash
pip install git+https://github.com/ArtifactLabs/git-recycle-bin.git
```

You can also install from a local checkout:

```bash
pip install .
```

## Basic usage

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

Enable build avoidance in your build script by checking for an existing
artifact before building:

```bash
if git_recycle_bin.py list . --name demo | grep -q .; then
    git_recycle_bin.py list . --name demo | head -n 1 | \
        xargs -I _ git_recycle_bin.py download . _
    echo "Build skipped - using downloaded artifact"
else
    make all
    git_recycle_bin.py push . --path ./build --name demo
fi
```

## Advanced usage

Set a custom expiry date when pushing an artifact:

```bash
git_recycle_bin.py push . --path ./build --name demo --expire "1 month"
```

List all artifacts for the current repository:

```bash
git_recycle_bin.py list .
```

## How it works

`git-recycle-bin` stores artifacts in dedicated branches and
links them to source commits using git notes. Notes are non-destructive
so you can look up previous binaries and reuse them. Stale artifacts
disappear once expired and a `git gc` runs. CI pipelines can fetch
matching artifacts and skip rebuilding.

Artifacts include metadata stored as trailer fields in the commit
message. Key fields:

- `artifact-schema-version`
- `artifact-name`
- `artifact-mime-type`
- `artifact-tree-prefix`
- `src-git-relpath`
- `src-git-commit-sha`
- `src-git-branch`
- `src-git-repo-url`

For a full schema see [issue #1](issues/0001-git-notes-integration.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines. Run tests
with `just unittest` and check style with `just lint`
before submitting a
pull request.

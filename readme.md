# Git Recycle Bin ♻️

**Store and share build artifacts in any Git repository.** Git Recycle Bin makes a plain Git repo act as a lightweight artifact server with automatic clean‑up and full traceability to the sources that produced each artifact.

Thanks to orphan commits and non‑destructive Git notes everything lives inside Git itself – no extra infrastructure required. Use it with GitHub, GitLab or any other host.

## Why adopt Git Recycle Bin?

- **Self‑governed** – works with any Git host. No custom enterprise tools required.
- **One toolchain** – the Git commands you already know handle upload and download.
- **Skip rebuilds** – locate previous binaries via Git notes and reuse them instantly.
- **Traceable** – each artifact commit records the exact source commit and branch.
- **Self‑cleaning** – set an expiry when pushing and artifacts vanish after `git gc`.

## Installation

1. Clone this repository.
   ```bash
   git clone https://github.com/ArtifactLabs/git-recycle-bin.git
   cd git-recycle-bin
   ```
2. **Nix users**: enter the development shell for a ready‑made environment
   ```bash
   nix-shell   # or `nix develop` on flakes
   ```
3. **pip users**: install the package manually (preferably in a virtual environment)
   ```bash
   pip install .
   ```

## Quick start

Push an artifact directory to a separate Git repository:

```bash
git_recycle_bin.py push . \
    --path ../obj/doc/html \
    --name "Aurora-RST-Documentation" \
    --remote git@gitlab.ci.demant.com:csfw/documentation/generated/aurora_rst_html_mpeddemo.git \
    # or --remote git@github.com:yourorg/binaries.git
    --push \
    --push-tag
```

This will create a new orphan commit containing `../obj/doc/html`, tag it with metadata and push it to the binary repository. The branch/tag naming encodes the source commit so future downloads know exactly where it came from.

List available artifacts in the remote repository and download one by its commit SHA:

```bash
git_recycle_bin.py list git@gitlab.ci.demant.com:csfw/documentation/generated/aurora_rst_html_mpeddemo.git
# or git_recycle_bin.py list git@github.com:yourorg/binaries.git

# Suppose the list shows an artifact commit `1234abcd` – download it locally
git_recycle_bin.py download git@gitlab.ci.demant.com:csfw/documentation/generated/aurora_rst_html_mpeddemo.git 1234abcd
# or git_recycle_bin.py download git@github.com:yourorg/binaries.git 1234abcd
```

With these two commands you can push a build result and later retrieve it anywhere without rebuilding.

## Benefits

Git Recycle Bin keeps your artifacts versioned alongside code so you can easily reuse them. Skip entire rebuilds by fetching a previous binary via associative Git notes and share it with your team. Expired artifacts disappear after `git gc`, saving disk space with zero manual maintenance. Because everything is plain Git you can browse, clone and mirror using the tools you already know.

Why the name? We "recycle" your build results – store them for later reuse and
garbage collect them when they're obsolete. ♻️

## Technical details

Artifacts store structured metadata inside the commit message. Important fields include:

- `artifact-schema-version` – Schema version integer.
- `artifact-name` – Human readable name.
- `artifact-mime-type` – MIME type such as `directory` or `link`.
- `artifact-tree-prefix` – Directory prefix shared by all files in the commit.
- `src-git-relpath` – Path of the artifact in the source tree.
- `src-git-commit-title` – Title line of the source commit message.
- `src-git-commit-sha` – Full SHA of the source commit.
- `src-git-branch` – Source branch name or `Detached HEAD`.
- `src-git-repo-url` – Remote URL of the source repository.
- `src-git-status` – `clean` or a list of modified/deleted files when built.

Additional metadata such as build duration or dependencies can be added in the
future via Git notes. Notes are associative, so they never rewrite history while
letting you attach as much information as you like.

Our CI definitions live in both `.gitlab-ci.yml` and `.github/workflows/ci.yml`
so builds run the same way on GitLab and GitHub.


Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.


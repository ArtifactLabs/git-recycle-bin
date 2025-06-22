# Development Guide

This file provides comprehensive guidance for AI agents and developers
working with this Git-Recycle Bin repository.
This file is LLM-agnostic - used with both Claude and Codex.

This project provides a collection of Python scripts and utilities for
managing artifacts in a git repository.
It uses Nix for reproducible development environments but should remain
runnable outside of Nix as a normal Python package.

## Project Structure

The repository is organised into a few key folders:

- `src/` contains the application code and executable entrypoints.
- `tests/` holds unit and future integration tests.
- `demos/` shows practical usage of the tools.
- `aux/` holds helper scripts that are not part of the build itself but may be
  useful.
- `issues/` contains markdown tickets that track design ideas and open tasks.
  When starting new work, add a ticket here first.

### Issue ticket style

Tickets under `issues/` should outline:

- **Purpose** of the idea or feature
- **Acceptance Criteria** describing what must be true to close the ticket
- **Prerequisites** needed before work can begin
- **Questions** that remain open
- **Status** of the issue (e.g. Open, Done)

Wrap lines in these markdown files at roughly 72 characters for readability.


## General Conventions for AGENTS.md Implementation

- Keep this document in sync with the code base.
  Update guidelines alongside feature or behaviour changes.
- Clarify any new requirements or conventions in this file so agents know how
  to contribute.

## Available Commands

See `nix-shell --run 'just --list'` in general.

### Testing
- **Run unit tests**: `nix-shell --pure --run 'just unittest'`
- **Run single test**: `nix-shell --pure --run 'pytest tests/test_specific_file.py'`

### Linting
- **Run all linters**: `nix-shell --pure --run 'just lint'`
- **Shell scripts**: `nix-shell --pure --run 'just lint-shell'`
- **Markdown files**: `nix-shell --pure --run 'just lint-md'`
- **RST documentation**: `nix-shell --pure --run 'just lint-rst'`

### Documentation
- **Build Sphinx docs**: `nix-shell --pure --run 'just docs'`
- **Lint documentation**: `nix-shell --pure --run 'just docs-lint'`
- **Clean docs**: `nix-shell --pure --run 'just docs-clean'`

### Installation
- **With Nix**: Use `nix-shell --run 'just <command>'` for any just commands
- **Non-Nix**: create venv, install dependencies from `setup.py` and run `pytest` with
  `PYTHONPATH=$PWD:$PWD/src`.


## Pre-submit Checks

- Run `nix-shell --pure --run "just unittest"` and ensure all tests succeed.
- Run `nix-shell --pure --run 'just lint'` and fix any reported issues.
- Validate that documentation updates accompany code changes to prevent drift.
- When editing CLI examples, run `git_recycle_bin.py --help` to verify option
  names and arguments.


## Architecture

Git Recycle Bin is a Python CLI tool that uses Git repositories as artifact storage with bidirectional traceability.

### Core Components

- **`git_recycle_bin.py`**: Main entry point with command parsing and orchestration
- **`rbgit.py`**: RbGit class - Git operations wrapper for artifact repository management
- **`arg_parser.py`**: Command-line argument parsing with sub-commands (push, list, download, clean)
- **`commit_msg.py`**: Artifact commit message generation and parsing with metadata trailers
- **`list.py`**: List command implementation for querying artifacts
- **`download.py`**: Download command for retrieving artifacts

### Key Architecture Patterns

**Artifact Storage**: Uses orphan Git branches with structured naming:
- `artifact/expire/{EXPIRY_DATE}/{SOURCE_REPO}@{SOURCE_SHA}/{ARTIFACT_PATH}`
- `artifact/latest/{SOURCE_REPO}@{SOURCE_BRANCH}/{ARTIFACT_PATH}`

**Traceability**: Git notes link source commits to artifacts, enabling build avoidance and dependency tracking.

**Metadata**: Commit messages contain structured trailers with source repository information, expiry dates, and artifact details.

**Environment**: RbGit class manages separate Git directory/work-tree via `GIT_DIR` and `GIT_WORK_TREE` environment variables.

### Dependencies

Python packages: `maya`, `colorama`, `dateparser`

## Code Style

- Use `snake_case` for modules and functions, and `PascalCase` for classes.
- **PEP 8 compliance**: 4-space indentation, line length ≤88 characters
- **Type hints**: Use type hints where sensible.
- **Docstrings**: Required for all public functions and classes using restructuredtext style
- **Prefer standard library modules** over additional dependencies when possible.
- **Import organization**: Standard library, third-party, local imports (separated by blank lines)
- **Error handling**: Use specific exception types, never bare `except:`
- **Variable naming**: Descriptive names, no single-letter variables except loop counters
- **Function design**: Single responsibility principle, max 20 lines per function
- **Class design**: Composition over inheritance, explicit `__init__` parameters
- **Constants**: ALL_CAPS for module-level constants
- **File organization**: Modular design with utility modules (`util_*.py`)
- **Comments**: Explain why, not what. No obvious comments.
- **Testing**: All new code must have corresponding unit tests

Linting must pass before any commits. Run `nix-shell --run 'just lint'` to verify.

## Development Guidelines

### Environment Requirements
- Code must run with Python 3.9+
- Avoid Nix-specific runtime assumptions
- Project must remain installable with `pip install .`

### Quality Standards
- Keep code robust, correct-by-design, industrial, portable, readable
- Avoid breaking changes without integration tests
- Embrace UNIX and KISS philosophies
- Apply POLA (principle of least astonishment)
- Consider input/output and data structures first, then implementation
- Avoid refactoring unless explicitly approved. If refactoring occurs, ensure
  end-to-end tests exist and add unit tests.
- Wrap lines in Markdown to keep them reasonably short and readable.
- Keep documentation and design notes in sync with the implementation to avoid
  drift.

### Testing Requirements
- Integration tests comparing HEAD with prior tagged releases must pass before merging breaking changes
- All Pre-submit Checks must pass locally before opening PRs

### Pull Request Guidelines
- Keep PRs focused with clear summaries of changes and testing steps
- Ensure all Pre-submit Checks pass locally
- Update documentation alongside code changes to prevent drift
- When editing CLI examples, verify with `git_recycle_bin.py --help`

### Continuous Integration
- Maintain both GitHub and GitLab pipelines in sync
- Keep `.gitlab-ci.yml` and `.github/workflows/ci.yml` logically aligned


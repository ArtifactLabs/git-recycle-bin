# Repo Guidelines for Codex Agents

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

## Coding Conventions

- Follow PEP 8 style with four-space indentation and descriptive names.
- Use type hints where sensible and keep functions short and readable.
- Prefer standard library modules over additional dependencies when possible.
- Use `snake_case` for modules and functions, and `PascalCase` for classes.

## General Conventions for AGENTS.md Implementation

- Keep this document in sync with the code base.
  Update guidelines alongside feature or behaviour changes.
- Clarify any new requirements or conventions in this file so agents know how
  to contribute.

## Testing Requirements

- Preferred: `nix-shell shell.nix --pure --run "just unittest"`.
- Non-Nix: install dependencies from `setup.py` and run `pytest` with
  `PYTHONPATH=$PWD:$PWD/src`.
- Integration tests comparing HEAD with prior tagged releases must pass
  before merging breaking behaviour changes.

## Environment

- Code should run with Python 3.11+. Avoid Nix-specific runtime assumptions.
- Ensure the project remains installable with `pip install .`.

## Style and Quality

- Keep the code base robust and industrial readable. Use type hints and
  descriptive names.
- Avoid breaking changes. Introduce integration tests comparing HEAD with
  previous tagged releases when altering behaviour.
- Keep documentation and design notes in sync with the implementation to avoid
  drift.
- Wrap lines in Markdown to keep them reasonably short and readable.
- Embrace the UNIX and KISS philosophies and apply POLA (principle of least
  astonishment).
- Consider input/output and data-structures first, then implementation.
- Avoid refactoring unless explicitly approved. If refactoring occurs, ensure
  end-to-end tests exist and add unit tests.

## Pull Request Guidelines

- Keep PRs focused and include a summary of changes and testing steps.
- Ensure programmatic checks pass locally before opening a PR.

## Programmatic Checks

- Run `nix-shell shell.nix --pure --run "just unittest"` and ensure all tests
  succeed.
- Validate that documentation updates accompany code changes to prevent drift.

## Continuous Integration

The project maintains both GitHub and GitLab pipelines.
When changing one CI configuration, update the other in a comparable manner so
the steps remain logically aligned.
Keep `.gitlab-ci.yml` and `.github/workflows/ci.yml` synchronized to avoid
divergent behaviour.

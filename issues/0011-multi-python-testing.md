# Multi-version Python testing

## Purpose
Ensure the codebase remains compatible across supported Python
releases by running the test suite against each version.

## Acceptance Criteria
- ✅ CI matrix covers Python 3.8 through 3.13 (expanded beyond minimum).
- ✅ All versions pass the same tests without conditional skips.
- ✅ Both GitHub Actions and GitLab CI include python-sweep testing.
- ✅ Git version compatibility testing also implemented via git-sweep.

## Prerequisites
- ✅ Tests rely only on functionality present in all targeted versions.

## Implementation Details
- Added `python_sweep` job to both CI systems using `just python-sweep`
- Added `git_sweep` job to both CI systems using `just git-sweep`
- Python versions tested: 3.8, 3.9, 3.10, 3.11, 3.12, 3.13
- Git versions tested: 2.25, 2.30, 2.35, 2.38, 2.43, 2.44, 2.45, 2.46, 2.47, 2.49
- Test infrastructure uses Nix shells for deterministic environments

## Questions
- When should we remove older Python versions from the matrix?

## Status
✅ **DONE** - Multi-version testing implemented in CI

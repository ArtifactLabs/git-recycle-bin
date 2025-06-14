# Prepare project for PyPI upload

## Purpose

Package the code for publication on PyPI so it can be easily
installed via `pip`.

## Acceptance Criteria

- Build configuration produces a valid source distribution and
  wheel.
- Metadata such as description and license render correctly on
  PyPI.

## Prerequisites

- Complete versioning strategy and test coverage.

## Questions

- Should we use `twine` or another tool for uploading?

## Status

Open

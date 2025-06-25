# CLI Improvements: Human-Friendly Output and Better UX

## Purpose

The recent documentation fixes in commit d6765ee revealed that our CLI is quite 
basic and machine-oriented, lacking human-friendly features that would improve 
usability. The original documentation had imagined a much richer CLI interface 
with features like `--format json`, tabular output, and `--name` filtering that 
don't actually exist.

This issue outlines improvements to make git-recycle-bin more user-friendly while 
maintaining its current machine-readable interface for scripting.

## Current State vs Desired State

### Current `list` command:
- Outputs only artifact SHAs, one per line
- Basic filtering by `--name` and `--path`
- No format options
- No metadata display

### Current `download` command:
- Takes SHAs as positional arguments
- Minimal output
- No output directory control
- No progress indication

## Acceptance Criteria

### 1. Multiple Output Formats for `list`

**Human-readable table format (default for TTY):**
```
NAME           BRANCH    COMMIT    AGE         EXPIRES     SIZE   STATUS
📦 webapp-build   main      a1b2c3d4  2 hours ago 2024-12-25  2.3MB  ✅ Active
📚 api-docs       develop   b2c3d4e5  1 day ago   2024-12-20  890KB  ⏰ Expires soon
```

**JSON format (for programmatic use):**
```json
[
  {
    "name": "webapp-build",
    "artifact_sha": "9f8e7d6c5b4a3e2d...",
    "source_branch": "main", 
    "source_commit": "a1b2c3d4e5f6789...",
    "created": "2024-06-25T15:30:00Z",
    "expires": "2024-12-25T14:30:00Z",
    "path": "dist",
    "size_bytes": 2419200,
    "expired": false
  }
]
```

**Compact format (for scripting):**
```
📦 webapp-build:9f8e7d6c (main@a1b2c3d4, 2.3MB, ✅ expires 2024-12-25)
🗂️ api-docs:b2c3d4e5 (develop@b2c3d4e5, 890KB, ⏰ expires 2024-12-20)
```

**SHA-only format (current behavior, for backward compatibility):**
```
9f8e7d6c5b4a3e2d1c0b9a8f7e6d5c4b
a1b2c3d4e5f678901234567890abcdef
```

### 2. Enhanced Filtering Options

```bash
# Time-based filtering
git_recycle_bin.py list . --since "1 week ago"
git_recycle_bin.py list . --until "yesterday"

# Status filtering  
git_recycle_bin.py list . --expired
git_recycle_bin.py list . --active

# Pattern matching
git_recycle_bin.py list . --name "webapp-*"
git_recycle_bin.py list . --path "dist/*"

# Size filtering
git_recycle_bin.py list . --min-size 1MB
git_recycle_bin.py list . --max-size 100MB
```

### 3. Format Selection

```bash
# Auto-detect: table for TTY, SHA-only for pipes
git_recycle_bin.py list .

# Explicit format selection
git_recycle_bin.py list . --format table
git_recycle_bin.py list . --format json  
git_recycle_bin.py list . --format compact
git_recycle_bin.py list . --format sha     # current behavior
```

### 4. Enhanced `download` Command

```bash
# Download by name (gets latest)
git_recycle_bin.py download . --name "webapp-build"

# Download to specific directory
git_recycle_bin.py download . --output ./dist abc123def456

# Multiple downloads
git_recycle_bin.py download . abc123 def456 --output ./artifacts/

# Progress and verbosity
git_recycle_bin.py download . abc123 --verbose
git_recycle_bin.py download . abc123 --quiet
```

### 5. New `info` Command

Display detailed information about a specific artifact:

```bash
git_recycle_bin.py info . abc123def456
```

Output:
```
📦 Artifact: abc123def456
🏷️  Name: webapp-build
🌿 Source: main@a1b2c3d4e5f6 (My feature branch)
🕐 Created: 2024-06-25 15:30:00 +02:00 (2 hours ago)
⏰ Expires: 2024-12-25 14:30:00 +02:00 (✅ in 6 months)
📁 Path: dist/
📊 Size: 2.3 MB (2,419,200 bytes)
📄 Files: 127 files, 15 directories

📝 Recent commits:
  🔹 a1b2c3d4 Add new feature X
  🔹 b2c3d4e5 Fix bug in component Y
  
💬 Notes: Clean build from CI
```

### 6. Global CLI Improvements

**Consistent verbosity:**
- `--quiet` / `-q`: Minimal output
- Default: Normal output
- `--verbose` / `-v`: Detailed output  
- `--debug`: Debug information

**Color output:**
- Auto-detect TTY and use colors appropriately
- `--color=auto|always|never`
- Respect `NO_COLOR` environment variable

**Better error handling:**
- Meaningful error messages with emojis for visual clarity
- Consistent exit codes
- Suggestions for common mistakes

**Example error output:**
```
❌ Error: Artifact 'abc123def456' not found in repository
💡 Tip: Use 'git_recycle_bin.py list .' to see available artifacts
🔍 Did you mean one of these?
   📦 webapp-build (abc789def123)
   📚 api-docs (def456abc789)
```

## Prerequisites

- Review current argument parsing structure in `arg_parser.py`
- Analyze output formatting needs across commands
- Consider backward compatibility requirements
- Plan for testing different terminal environments

## Questions

1. Should we maintain strict backward compatibility for the current SHA-only 
   output, or is it acceptable to change the default format?

2. How should we handle the transition period? Feature flags? Version-based 
   behavior?

3. Should JSON format follow a specific schema standard?

4. How should we handle performance with large artifact repositories when 
   displaying rich information?

5. Should we add configuration file support for default formats and options?

## Implementation Notes

- Use format auto-detection: rich formats for TTY, machine-readable for pipes
- Consider using libraries like `rich` for table formatting and colors
- Implement pagination for long lists
- Add shell completion for better UX
- Consider adding `--help-formats` to explain output format options

**Emoji Guidelines:**
- Only show emojis in human-readable formats (table, compact, info)
- Never include emojis in JSON or SHA-only formats
- Respect `NO_COLOR` environment variable (disable emojis when colors disabled)
- Use consistent emoji mapping:
  - 📦 Artifacts/packages
  - 🌿 Git branches  
  - 🕐 Creation times
  - ⏰ Expiration times
  - ✅ Active/healthy status
  - ❌ Errors/expired
  - 💡 Tips/suggestions
  - 🔍 Search/discovery
  - 📁 Paths/directories
  - 📊 Size/statistics
  - 📄 Files
  - 📝 Commits/notes
  - 🏷️ Names/labels

## Status

**Open** - Awaiting design review and prioritization.

This enhancement would significantly improve the user experience while 
maintaining the tool's scriptability and automation-friendliness.
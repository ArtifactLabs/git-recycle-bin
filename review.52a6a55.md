# Code Review: Commit 52a6a55 "allow jq integration for list filters"

**Author:** Jacob Herbst
**Date:** Thu Sep 4 14:06:39 2025 +0200

## Summary

This commit adds jq integration to enable more powerful filtering on artifact metadata. While the concept is valuable, the implementation contains critical bugs and violates several MPED architectural principles.

## Critical Issues

### 1. **CRITICAL BUG - Infinite Recursion**

**File:** `git-recycle-bin/utils/extern.py` (lines 27-28)

```python
def jq(command, input, env={}):
    try:
        return jq(command, input, env)  # <-- INFINITE RECURSION
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        printer.error(f"jq command failed: {e}", file=sys.stderr)
        return None
```

**Issue:** The `jq()` function calls itself recursively instead of calling `jq_unsafe()`. This will cause a stack overflow on every invocation.

**Fix Required:** Line 28 should call `jq_unsafe(command, input, env)`.

### 2. **Mutable Default Arguments - Potential State Corruption**

**File:** `git-recycle-bin/utils/extern.py`

```python
def jq_unsafe(command, input, env={}):  # <-- Mutable default
def jq(command, input, env={}):         # <-- Mutable default
```

**Issue:** Using mutable dictionaries as default arguments creates shared state between function calls, leading to potential side effects and hard-to-debug issues.

**MPED Violation:** "Minimize State, Never Duplicate" and "Fail Fast and Verbosely" - this silent state sharing violates both principles.

**Fix Required:** Use `env=None` and initialize with `env = env or {}` inside the function.

### 3. **Architecture Inconsistency - Missing Query Type Integration**

**Analysis:** The commit diff shows addition of a `jq` option to the argument parser, but the current codebase uses a different query architecture with `Query` classes (`JqQuery`, `NameQuery`, etc.). The diff appears to show an older state that was later refactored.

**Current State:** The `jq_filter` function correctly uses the new architecture, but the commit message and diff don't align with the current implementation.

## Code Quality Issues

### 4. **Weak Error Handling**

**File:** `git-recycle-bin/commands/list.py` (line 118)

```python
return jq_res is not None and jq_res != "" and jq_res != "null" and jq_res != "[]"
```

**Issues:**
- String comparison with `"null"` and `"[]"` is fragile - jq output formatting may vary
- No validation that `jq_res` is actually the expected type
- Silent failure if jq returns unexpected formats

**MPED Violation:** "Fail Fast and Verbosely" - the function should validate jq output more rigorously.

**Recommendation:** Parse jq output as JSON when possible, handle parse errors explicitly.

### 5. **Inconsistent Debug Logging**

**File:** `git-recycle-bin/commands/list.py` (line 36)

```python
printer.debug(f"Filtering artifacts by {query.__class__} with {{ {query.query()} }}")
```

**Issue:** Using `query.__class__` instead of `query.__class__.__name__` produces unhelpful debug output like `<class 'JqQuery'>`.

**Fix:** Use `query.__class__.__name__` for readable logging.

### 6. **Missing Input Validation**

**File:** `git-recycle-bin/commands/list.py` (jq_filter function)

**Issues:**
- No validation that the jq query string is safe or well-formed
- No protection against jq command injection (though subprocess usage provides some safety)
- No timeout protection for potentially long-running jq operations

**Security Concern:** While subprocess usage provides protection, complex jq expressions could cause performance issues.

## MPED Principle Analysis

### ✅ **Composability Maintained**
The jq integration follows the existing filter pattern, allowing composition with other query types through `AndQuery`.

### ❌ **Fundamentals Violated**
- Critical bug shows insufficient testing before commit
- Mutable default arguments create hidden state dependencies

### ❌ **Fail Fast Violated**
- Infinite recursion bug will cause silent hangs until stack overflow
- Weak jq output validation allows unexpected behavior to propagate

### ⚠️ **Data Design Concerns**
- jq operates on JSON serialization of metadata, adding encoding/decoding overhead
- No consideration of metadata size limits for jq processing

## Recommendations

### Immediate Fixes Required

1. **Fix the infinite recursion bug** - This is a showstopper that will crash the application.

2. **Fix mutable default arguments** - Replace with None and proper initialization.

3. **Improve jq output validation** - Parse as JSON when possible, handle edge cases explicitly.

4. **Add timeout protection** - Prevent runaway jq processes from hanging the application.

### Architecture Improvements

1. **Add input validation** - Validate jq expressions for basic syntax before execution.

2. **Improve error reporting** - Provide specific error messages for different jq failure modes.

3. **Consider performance** - Add warnings or limits for complex jq operations on large metadata.

## Testing Requirements

Before this feature can be considered complete:

1. **Unit tests for jq_filter function** with various jq expressions
2. **Error handling tests** for malformed jq queries
3. **Performance tests** with large metadata objects
4. **Integration tests** combining jq with other query types

## Verdict

**❌ REQUIRES IMMEDIATE FIXES** - The infinite recursion bug makes this commit completely non-functional. The concept is sound and aligns well with the composable architecture, but the implementation needs significant fixes before it can be safely used.

The jq integration is a valuable feature that enhances the filtering capabilities, but it must be implemented correctly with proper error handling and input validation to meet MPED standards.
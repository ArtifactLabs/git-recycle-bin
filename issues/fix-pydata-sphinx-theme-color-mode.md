# Fix PyData Sphinx Theme Color Mode

**Status:** 🔄 OPEN (Temporary Workaround Applied)  
**Priority:** Medium  
**Component:** Documentation Infrastructure

## Purpose

The PyData Sphinx theme color mode switching is flaky and inconsistent,
causing pages to render in different themes (light/dark) when navigating
between pages. This creates a poor user experience and makes the
documentation appear broken.

**CURRENT STATUS:** Temporary light-theme-only workaround implemented to eliminate
immediate UX issues. **GOAL:** Implement proper theme switching that supports both
light and dark modes reliably.

## Problem Description

### Symptoms

- Theme mode changes inconsistently when navigating between pages
- Some pages render in light mode while others render in dark mode
- Theme switcher button behavior is unreliable
- Page refreshes may reset to different theme than expected
- localStorage theme state appears to be corrupted or ignored

### Root Causes Identified

1. **PyData Theme Version Issues**: Theme switcher behavior varies between
   PyData Sphinx theme versions, with inconsistent localStorage handling

2. **Mode vs Theme Confusion**: PyData theme uses both `data-mode` and
   `data-theme` attributes which can become desynchronized

3. **Auto Mode Problems**: The "auto" mode (following system preferences)
   can override explicit user choices unpredictably

4. **Cache State Corruption**: Invalid or corrupted theme states in
   browser localStorage prevent proper theme persistence

5. **Missing Theme Switcher**: Theme switcher component was removed from
   navbar configuration, leaving users with no way to control theme

## 🚧 TEMPORARY WORKAROUND (Current Implementation)

**Current Solution:** Force light theme only and completely disable theme switching.
This eliminates theme switching issues but **does not meet the actual requirement**
of supporting both light and dark themes.

**⚠️ LIMITATION:** Users cannot switch to dark theme, which is a desired feature.

### Current Implementation Details

#### 1. Sphinx Configuration Changes (`docs/conf.py`)

```python
html_theme_options = {
    "navbar_start": ["navbar-logo"],
    "navbar_center": ["navbar-nav"],
    "navbar_end": ["navbar-icon-links"],  # Removed "theme-switcher"
    # ... other options ...
    
    # Force light theme only - disable all theme switching
    "theme_switcher_button": False,
    "color_scheme": "light",
    "default_mode": "light",
}

# Add custom JavaScript to force light theme
html_js_files = [
    'force-light-theme.js',
]

html_context = {
    "default_mode": "light",
    "theme_mode": "light",
    "force_theme": "light",
    # ... other context ...
}
```

#### 2. CSS Overrides (`docs/_static/custom.css`)

Nuclear CSS rules to force light theme:

```css
/* FORCE LIGHT THEME ONLY - Override all theme switching */
html, html[data-theme], html[data-theme="dark"], html[data-theme="light"], html[data-theme="auto"] {
    --pst-color-primary: #059669 !important;
    --pst-color-secondary: #10b981 !important;
    --pst-color-accent: #34d399 !important;
    --pst-color-warning: #d97706 !important;
    --pst-color-danger: #dc2626 !important;
    --pst-color-background: #ffffff !important;
    background-color: #ffffff !important;
    color: #000000 !important;
}

/* Force light theme attributes */
html {
    data-theme: light !important;
    data-mode: light !important;
}

/* Hide any theme switcher elements that might still appear */
.theme-switch, .theme-switcher, [data-bs-target="#pst-theme-switcher"], #pst-theme-switcher {
    display: none !important;
    visibility: hidden !important;
}
```

#### 3. JavaScript Override (`docs/_static/force-light-theme.js`)

JavaScript to hijack all theme switching attempts:

```javascript
// Force light theme only - disable all theme switching
(function() {
    'use strict';
    
    // Override localStorage to always return light theme
    const originalGetItem = localStorage.getItem;
    const originalSetItem = localStorage.setItem;
    
    localStorage.getItem = function(key) {
        if (key === 'theme' || key === 'mode' || key === 'pst-theme') {
            return 'light';
        }
        return originalGetItem.call(this, key);
    };
    
    localStorage.setItem = function(key, value) {
        if (key === 'theme' || key === 'mode' || key === 'pst-theme') {
            value = 'light';
        }
        return originalSetItem.call(this, key, value);
    };
    
    // Force light theme on document
    function forceLight() {
        const html = document.documentElement;
        html.setAttribute('data-theme', 'light');
        html.setAttribute('data-mode', 'light');
        html.dataset.theme = 'light';
        html.dataset.mode = 'light';
        
        // Remove any dark theme classes
        html.classList.remove('dark', 'theme-dark');
        html.classList.add('light', 'theme-light');
        
        // Force localStorage to light
        localStorage.setItem('theme', 'light');
        localStorage.setItem('mode', 'light');
        localStorage.setItem('pst-theme', 'light');
    }
    
    // Apply immediately and on all DOM events
    forceLight();
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', forceLight);
    } else {
        forceLight();
    }
    
    window.addEventListener('load', forceLight);
    
    // Remove theme switcher buttons from DOM
    window.addEventListener('load', function() {
        const themeSwitchers = document.querySelectorAll('.theme-switch, .theme-switcher, [data-bs-toggle="dropdown"][aria-label*="theme"], [data-bs-toggle="dropdown"][aria-label*="Theme"]');
        themeSwitchers.forEach(function(switcher) {
            switcher.style.display = 'none';
            switcher.disabled = true;
            switcher.remove();
        });
    });
    
    // Monitor for any theme changes and force back to light
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'attributes' && 
                (mutation.attributeName === 'data-theme' || mutation.attributeName === 'data-mode')) {
                const target = mutation.target;
                if (target.getAttribute('data-theme') !== 'light' || target.getAttribute('data-mode') !== 'light') {
                    forceLight();
                }
            }
        });
    });
    
    observer.observe(document.documentElement, {
        attributes: true,
        attributeFilter: ['data-theme', 'data-mode', 'class']
    });
})();
```

### Temporary Workaround Results

✅ **Theme switcher completely removed** from navbar  
✅ **Documentation always renders in light theme**  
✅ **No theme switching possible** - even manual attempts are overridden  
✅ **Consistent experience** across all pages and navigation  
✅ **localStorage hijacking** prevents theme state corruption  
✅ **Mutation observer** prevents any theme changes  
⚠️ **LIMITATION: No dark theme support** - users cannot switch to dark mode

### Build Output

```
Running Sphinx v7.3.7
WARNING: unsupported theme option 'theme_switcher_button' given
WARNING: unsupported theme option 'color_scheme' given  
WARNING: unsupported theme option 'default_mode' given
build succeeded, 3 warnings.
```

## 🎯 REQUIRED SOLUTION

**Goal:** Implement proper theme switching that supports both light and dark modes reliably.

### Acceptance Criteria (Updated)

- [ ] Theme mode remains consistent across all documentation pages
- [ ] Theme switcher button appears in navigation and functions properly
- [ ] User theme choice persists across page navigation and browser sessions
- [ ] Theme state corruption is automatically detected and corrected
- [ ] Documentation renders correctly in **both light and dark modes**
- [ ] Theme switching works reliably without page flashing or inconsistencies
- [ ] **NEW:** Dark theme has proper styling for all custom elements
- [ ] **NEW:** Theme switching is accessible and follows UX best practices

### Technical Requirements

1. **Restore Theme Switcher Component**
   - Add "theme-switcher" back to navbar_end configuration
   - Ensure proper icon display for each theme mode
   - Make switcher accessible with proper ARIA labels

2. **Implement Reliable Theme State Management**
   - Fix localStorage synchronization issues
   - Implement proper synchronization between data-mode and data-theme
   - Add mutation observers to detect and fix state corruption
   - Handle edge cases like corrupted localStorage

3. **Enhanced CSS Theme Support**
   - Ensure all custom styles work properly in both light and dark modes
   - Fix theme-specific styling inconsistencies
   - Add proper theme icon visibility rules
   - Test custom CSS variables in both themes

4. **Robust JavaScript Implementation**
   - Replace current "force light" JavaScript with proper theme management
   - Implement theme persistence across page loads
   - Handle browser compatibility issues
   - Add fallback behavior for JavaScript-disabled users

## Technical Approach

### Proposed Solution: Proper Theme Switching

**Rationale:** Instead of forcing light theme only, implement reliable theme switching
that addresses the root causes while supporting both themes.

### Implementation Strategy

1. **Remove current workaround:**
   - Remove force-light-theme.js
   - Remove CSS overrides that force light theme
   - Restore theme switcher in navbar

2. **Implement proper theme management:**
   - Custom JavaScript for reliable localStorage handling
   - Proper theme state synchronization
   - Mutation observers for corruption detection

3. **Enhanced CSS support:**
   - Dark theme CSS variables for custom elements
   - Proper theme-aware styling
   - Accessibility improvements

4. **Testing and validation:**
   - Cross-browser testing
   - Theme persistence testing
   - Accessibility testing

## Questions

- [ ] Should we implement custom theme switcher logic vs. fixing PyData's built-in?
- [ ] How do we handle theme consistency for users with JavaScript disabled?
- [ ] Should we add theme preference detection (system dark/light mode)?
- [ ] Do we need fallback themes if PyData theme fails to load?

## Implementation Plan

### Phase 1: Remove Workaround and Restore Switcher
1. Remove force-light-theme.js and related CSS overrides
2. Add theme-switcher back to navbar configuration
3. Test basic light/dark mode switching functionality

### Phase 2: Fix Core Theme Management
1. Implement reliable theme state management JavaScript
2. Add localStorage corruption detection and cleanup
3. Fix data-mode and data-theme synchronization

### Phase 3: Enhanced Theme Support
1. Add comprehensive CSS theme support for custom elements
2. Implement proper theme icon visibility rules
3. Add accessibility improvements

### Phase 4: Testing and Polish
1. Cross-browser compatibility testing
2. Theme persistence and state management testing
3. Accessibility and UX testing
4. Performance optimization

## Current Status

**TEMPORARY WORKAROUND ACTIVE:** Documentation uses light theme only.

**NEXT STEPS:** 
1. Remove light-theme-only workaround
2. Implement proper theme switching solution
3. Test both light and dark themes thoroughly

## Notes

- **Current limitation:** Light theme only - does not meet user requirements
- **User feedback:** Both light and dark themes are desired
- **Priority:** Medium - affects user experience but workaround prevents broken state
- **Approach:** Systematic fix rather than permanent workaround

## Related Issues

- PyData Sphinx Theme GitHub issues related to theme switching
- Sphinx documentation on theme configuration
- Browser localStorage debugging documentation

---

**Last Updated:** 2025-01-23  
**Assignee:** TBD  
**Estimated Effort:** 6-10 hours (proper implementation)  
**Status:** 🔄 **OPEN - TEMPORARY WORKAROUND ACTIVE, PROPER SOLUTION NEEDED**
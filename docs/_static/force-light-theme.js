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
    
    // Apply immediately
    forceLight();
    
    // Apply on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', forceLight);
    } else {
        forceLight();
    }
    
    // Apply on window load
    window.addEventListener('load', forceLight);
    
    // Override any theme switching functions
    window.addEventListener('load', function() {
        // Disable theme switcher buttons
        const themeSwitchers = document.querySelectorAll('.theme-switch, .theme-switcher, [data-bs-toggle="dropdown"][aria-label*="theme"], [data-bs-toggle="dropdown"][aria-label*="Theme"]');
        themeSwitchers.forEach(function(switcher) {
            switcher.style.display = 'none';
            switcher.disabled = true;
            switcher.remove();
        });
        
        // Override any theme switching event listeners
        const buttons = document.querySelectorAll('button, a');
        buttons.forEach(function(button) {
            if (button.textContent && (button.textContent.includes('theme') || button.textContent.includes('Theme'))) {
                button.style.display = 'none';
                button.disabled = true;
            }
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
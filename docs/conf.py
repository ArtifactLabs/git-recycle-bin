import os
import sys


project = 'git-recycle-bin'
author = 'Mark Ruvald Pedersen'
copyright = 'Mark Ruvald Pedersen'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx.ext.autosummary',
    'sphinx.ext.extlinks',
    'sphinx_design',
    'sphinxcontrib.plantuml',
]

autodoc_member_order = 'bysource'
autosummary_generate = True

html_theme = 'pydata_sphinx_theme'

html_theme_options = {
    "navbar_start": ["navbar-logo"],
    "navbar_center": ["navbar-nav"],
    "navbar_end": ["navbar-icon-links"],
    "navbar_persistent": ["search-button"],
    "primary_sidebar_end": [],
    "secondary_sidebar_items": ["page-toc", "edit-this-page"],
    "footer_start": ["copyright", "sphinx-version"],
    "footer_end": ["theme-version"],
    "show_prev_next": True,
    "show_nav_level": 2,
    "navigation_depth": 4,
    "collapse_navigation": False,
    "show_toc_level": 3,
    "header_links_before_dropdown": 4,
    "sidebar_includehidden": True,
    "use_edit_page_button": True,
    "navigation_with_keys": False,
    "switcher": {
        "json_url": "_static/switcher.json",
        "version_match": "latest",
    },
    # Force light theme only - disable all theme switching
    "theme_switcher_button": False,
    "color_scheme": "light",
    "default_mode": "light",
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/ArtifactLabs/git-recycle-bin",
            "icon": "fab fa-github-square",
            "type": "fontawesome",
        },
        #{
        #    "name": "PyPI",
        #    "url": "https://pypi.org/project/git-recycle-bin/",
        #    "icon": "fas fa-box",
        #    "type": "fontawesome",
        #},
    ],
}

html_title = f"{project} Documentation"
html_short_title = project
html_logo = "artwork/grb/vector/flat1-color-dark.long.svg"

# Add custom CSS for even fancier styling
html_static_path = ['_static']
html_css_files = [
    'custom.css',
]

# Add custom JavaScript to force light theme
html_js_files = [
    'force-light-theme.js',
]

# Configure sidebars to show navigation on all pages
html_sidebars = {
    "**": ["globaltoc.html", "searchbox.html"]
}

# Ensure the master document is properly set
master_doc = 'index'

# Additional toctree configuration
html_use_index = True
html_split_index = False
html_show_sourcelink = False

# Toctree options
toctree_collapse = False
toctree_includehidden = True

# Intersphinx mapping for external documentation
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
}

# External links for Git documentation (since git-scm.com doesn't provide objects.inv)
extlinks = {
    'git-doc': ('https://git-scm.com/docs/%s', 'git-%s'),
    'git-book': ('https://git-scm.com/book/en/v2/%s', '%s'),
}

html_context = {
    "default_mode": "light",
    "theme_mode": "light",
    "force_theme": "light",
    "github_user": "ArtifactLabs",
    "github_repo": "git-recycle-bin",
    "github_version": "master",
    "doc_path": "docs",
}

# RST substitutions
rst_epilog = """
.. |grb| replace:: git-recycle-bin
"""

# PlantUML configuration
plantuml = 'plantuml'
plantuml_output_format = 'svg'

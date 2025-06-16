import os
import sys

sys.path.insert(0, os.path.abspath('../src'))

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
]

autodoc_member_order = 'bysource'
autosummary_generate = True

html_theme = 'pydata_sphinx_theme'

html_theme_options = {
    "navbar_start": ["navbar-logo"],
    "navbar_center": ["navbar-nav"],
    "navbar_end": ["navbar-icon-links", "theme-switcher"],
    "navbar_persistent": ["search-button"],
    "primary_sidebar_end": ["sidebar-ethical-ads"],
    "secondary_sidebar_items": ["page-toc", "edit-this-page"],
    "footer_start": ["copyright", "sphinx-version"],
    "footer_end": ["theme-version"],
    "show_prev_next": True,
    "show_nav_level": 2,
    "navigation_depth": 4,
    "collapse_navigation": False,
    "show_toc_level": 3,
    "header_links_before_dropdown": 4,
    "switcher": {
        "json_url": "_static/switcher.json",
        "version_match": "latest",
    },
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

# Add custom CSS for even fancier styling
html_static_path = ['_static']
html_css_files = [
    'custom.css',
]

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
    "default_mode": "auto",
    "github_user": "ArtifactLabs",
    "github_repo": "git-recycle-bin",
    "github_version": "master",
    "doc_path": "docs",
}

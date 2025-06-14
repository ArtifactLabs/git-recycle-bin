import os
import sys

sys.path.insert(0, os.path.abspath('../src'))

project = 'git-recycle-bin'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
]

autodoc_member_order = 'bysource'

html_theme = 'sphinx_material'
html_theme_options = {
    'nav_title': 'git-recycle-bin Documentation',
}

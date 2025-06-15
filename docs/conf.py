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
html_context = {}

# Prevent sphinx_material from inserting unpicklable objects in html_context
try:
    import sphinx_material

    def setup(app):
        sphinx_material.setup(app)
        def _clear_context(app, env):
            env.config.html_context = {}
        app.connect("env-updated", _clear_context)
except Exception:
    pass

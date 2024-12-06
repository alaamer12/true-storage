import os
import sys
from sphinx.directives.other import Include
from docutils.parsers.rst import directives

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath('../..'))

project = 'True storage'
copyright = '2024, True storage Team'
author = 'True storage Team'
version = '1.0'
release = '1.0'

extensions = [
    'sphinx_rtd_theme',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Allow including files from outside the docs directory
class ExternalInclude(Include):
    def run(self):
        old_file = self.state.document.current_source
        self.state.document.current_source = os.path.abspath(
            os.path.join(os.path.dirname(old_file), self.arguments[0])
        )
        nodes = super().run()
        self.state.document.current_source = old_file
        return nodes

def setup(app):
    app.add_directive('external-include', ExternalInclude)

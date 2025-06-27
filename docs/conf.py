# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
sys.path.insert(0, os.path.abspath('..'))

project = 'NOUS Personal Assistant'
copyright = '2025, NOUS Team'
author = 'NOUS Team'
release = '1.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx.ext.autosummary',
    'sphinx_autodoc_typehints',
    'sphinxcontrib.mermaid',
    'autoapi.extension',
    'myst_parser',
]

# AutoAPI settings
autoapi_dirs = ['../']
autoapi_type = 'python'
autoapi_file_patterns = ['*.py']
autoapi_ignore = [
    '*backup*',
    '*__pycache__*',
    '*tests*',
    '*venv*',
    '*env*',
    '*node_modules*',
    '*flask_session*',
    '*logs*',
    '*uploads*',
    '*instance*',
    '*attached_assets*'
]
autoapi_options = [
    'members',
    'undoc-members',
    'show-inheritance',
    'show-module-summary',
    'special-members',
    'imported-members',
]
autoapi_member_order = 'groupwise'
autoapi_python_class_content = 'both'

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False

# Mermaid settings
mermaid_version = "latest"
mermaid_init_js = "mermaid.initialize({startOnLoad:true});"

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_title = 'NOUS Personal Assistant Documentation'
html_short_title = 'NOUS Docs'

# Theme options
html_theme_options = {
    'analytics_id': '',
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    'vcs_pageview_mode': '',
    'style_nav_header_background': '#2980B9',
    'collapse_navigation': True,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_css_files = [
    'custom.css',
]

# Intersphinx mapping
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'flask': ('https://flask.palletsprojects.com/en/2.3.x/', None),
    'sqlalchemy': ('https://docs.sqlalchemy.org/en/20/', None),
}

# Source file suffixes
source_suffix = {
    '.rst': None,
    '.md': 'myst_parser',
}

# Master document
master_doc = 'index'

# Add numbered figures and tables
numfig = True
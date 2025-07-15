# conf.py

# Project information
project   = "morphkit"
author    = "Tony Jurg"
master_doc = "index" 
html_title = "Morphkit Documentation"
copyright = "2025, Tony Jurg"

# Release information
release = '1.0.0'

# Theme and layout
html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    "collapse_navigation": False,   # keep the whole tree expanded everywhere
    "navigation_depth": -1,         # unlimited depth
    "sticky_navigation": True,      # sidebar scrolls with the page
    'includehidden': True,
    'titles_only': False
}

# Logo
html_logo = '_static/logo.png'


# Autosummary and autodoc
autodoc_default_options = {
    'member-order': 'bysource',
    'special-members': True,
    'undoc-members': True
}

# extentions
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    'docxbuilder'
]

# Napoleon settings
napoleon_use_param = True


autodoc_default_options = {
    'typehints': True,
}

#linkcode_resolve = lambda domain, info: {
#    'python': ('https://github.com/tonyjurg/morphkit/blob/main/%s#L%s#L%s',
#               'https://github.com/tonyjurg/morphkit/blob/main/%s#L%s#L%s'),
#}[domain](info)

# import path so autodoc can find morphkit
import sys, pathlib
sys.path.insert(0, r"C:\Users\tonyj\OneDrive\Documents\GitHub\morphkit")

# prevent Sphinx from trying to import modules that aren't actually being used
def setup(app):
    app.config['autosummary_imported_members'] = False

html_theme_options = {
    "sidebar_title": "Morphkit Documentation",
    "description": "Analyze Greek morphology with Morpheus",
}
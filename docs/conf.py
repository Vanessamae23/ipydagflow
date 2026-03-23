# Configuration file for the Sphinx documentation builder.
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

project = "ipydagflow"
copyright = "2024, ipydagflow contributors"
author = "ipydagflow contributors"

# -- General configuration ---------------------------------------------------

extensions = [
    "myst_nb",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx_design",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- MyST configuration ------------------------------------------------------

myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "fieldlist",
    "tasklist",
]

# -- Notebook configuration --------------------------------------------------

nb_execution_mode = "auto"  # "off", "auto", or "force"
nb_execution_timeout = 120

# -- Options for HTML output -------------------------------------------------

html_theme = "furo"
html_static_path = ["_static"]

html_theme_options = {
    "source_repository": "https://github.com/your-org/ipydagflow",
    "source_branch": "main",
    "source_directory": "docs/",
}

# -- Intersphinx configuration -----------------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

# -- Autodoc configuration ---------------------------------------------------

autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}

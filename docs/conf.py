import importlib.metadata
import re

project = "imaged"
author = "Julian Berman"
copyright = f"2026, {author}"

release = importlib.metadata.version("imaged")
version, _, _ = release.rpartition(".")

language = "en"
default_role = "any"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.coverage",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinxcontrib.spelling",
    "sphinxext.opengraph",
]

pygments_style = "lovelace"
pygments_dark_style = "one-dark"

html_theme = "furo"


def entire_domain(host):
    return r"http.?://" + re.escape(host) + r"($|/.*)"


linkcheck_ignore = [
    entire_domain("img.shields.io"),
    "https://github.com/Julian/imaged/actions",
    "https://github.com/Julian/imaged/workflows/CI/badge.svg",
    # Links which only exist once we exist as a package.
    # Read the Docs has no stable version until something is released,
    # and a release can't happen while this is what fails the build.
    # TODO: remove both once the first release has been built.
    "https://pypi.org/project/imaged/",
    entire_domain("imaged.readthedocs.io"),
]


# = Extensions =

# -- autosectionlabel --

autosectionlabel_prefix_document = True

# -- sphinxcontrib-spelling --

spelling_word_list_filename = "spelling-wordlist.txt"
spelling_show_suggestions = True

"""Sphinx configuration for the nicegui-shadcn documentation.

Sources are MyST Markdown so that the tutorial pages can reuse the wording and
tables of README.md / README_zh.md directly.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# autodoc imports the package to read its docstrings. ``python -m sphinx`` puts
# the current directory on sys.path, but the ``sphinx-build`` entry point does
# not, so the checkout is added explicitly: a documentation build from a fresh
# clone then works without installing the package first.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# -- Project information -----------------------------------------------------

project = "nicegui-shadcn"
author = "XiangQinxi"
copyright = "2025, XiangQinxi"

_GITHUB_USER = "XiangQinxi"
_GITHUB_REPO = "nicegui-shadcn"
_GITHUB_BRANCH = "master"


def _read_version() -> str:
    """Read the version from pyproject.toml so docs and package cannot drift."""
    pyproject = Path(__file__).resolve().parent.parent / "pyproject.toml"
    try:
        text = pyproject.read_text(encoding="utf-8")
    except OSError:
        return "0.0.0"
    try:
        import tomllib

        return tomllib.loads(text)["project"]["version"]
    except Exception:  # pragma: no cover - only hit on a broken pyproject
        match = re.search(r'^version\s*=\s*"([^"]+)"', text, re.M)
        return match.group(1) if match else "0.0.0"


release = _read_version()
version = ".".join(release.split(".")[:2])

# -- General configuration ---------------------------------------------------

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_design",
    "sphinx_copybutton",
]

source_suffix = {".md": "markdown", ".rst": "restructuredtext"}
root_doc = "index"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "requirements.txt"]

# Default language is Chinese; the theme ships a zh_CN locale for its own UI
# strings (search, prev/next, ...).
language = "zh_CN"
locale_dirs = ["locale/"]

autosectionlabel_prefix_document = True

myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "fieldlist",
    "attrs_inline",
    "tasklist",
    "replacements",
    "linkify",
]
myst_heading_anchors = 3
myst_fence_as_directive = ["note", "warning", "tip", "important"]
myst_linkify_fuzzy_links = False

# nicegui.io does not publish an objects.inv, so only Python is mapped.
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

copybutton_exclude = ".linenos, .gp, .go"


# -- API reference (sphinx.ext.autodoc) ---------------------------------------
#
# The pages under ``docs/api/`` contain nothing but ``automodule`` directives, so
# the API reference is read straight out of the source docstrings and cannot
# drift from the code.  The house style is a reStructuredText field list::
#
#     :param text: the label of the button.
#
# which autodoc renders natively.  Napoleon is switched on as well, so a
# contributor who reaches for a Google- or NumPy-style section still gets
# formatted output instead of a raw paragraph.
autoclass_content = "class"
autodoc_member_order = "bysource"
autodoc_default_options = {
    "members": True,
    "show-inheritance": True,
}
# Without this, a member that has no docstring of its own silently inherits its
# parent's, which is how every element here ended up advertised as a
# "Generic Element".
autodoc_inherit_docstrings = False
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_use_rtype = False

html_static_path = ["_static"]
html_css_files = ["custom.css"]
# Without this the browser falls back to requesting /favicon.ico and logs a 404.
# Sphinx resolves html_favicon against the config directory, not html_static_path.
html_favicon = "_static/favicon.svg"


# -- Upstream workaround: Chinese search stemmer ------------------------------
def _install_chinese_stemmer_fix() -> None:
    """Keep site search working when ``language = 'zh_CN'``.

    ``SearchChinese`` reuses the bundled ``english-stemmer.js`` (which defines
    ``EnglishStemmer``) while declaring ``language_name = 'Chinese'``.  Sphinx
    closes ``_static/language_data.js`` with::

        window.Stemmer = <language_name>Stemmer;

    so a Chinese build emits ``window.Stemmer = ChineseStemmer;`` and every page
    raises ``ReferenceError: ChineseStemmer is not defined``, leaving the search
    index without a stemmer.  Chinese is the only language whose declared name
    differs from the bundled stemmer's, so the correction is scoped to it and
    becomes a no-op once upstream fixes the mismatch.

    Upstream: ``sphinx/search/__init__.py`` (``get_js_stemmer_code``) together
    with ``sphinx/search/zh.py`` (``SearchChinese``).
    """
    from sphinx.search import IndexBuilder

    original = IndexBuilder.get_js_stemmer_code

    def get_js_stemmer_code(self):  # type: ignore[no-untyped-def]
        code = original(self)
        lang = self.lang
        if (
            getattr(lang, "js_stemmer_rawcode", "") == "english-stemmer.js"
            and lang.language_name != "English"
        ):
            code = code.replace(
                f"window.Stemmer = {lang.language_name}Stemmer;",
                "window.Stemmer = EnglishStemmer;",
            )
        return code

    IndexBuilder.get_js_stemmer_code = get_js_stemmer_code  # type: ignore[method-assign]


_install_chinese_stemmer_fix()

# -- Options for HTML output -------------------------------------------------

html_theme = "pydata_sphinx_theme"
html_title = "nicegui-shadcn 文档"
html_short_title = "nicegui-shadcn"
html_last_updated_fmt = "%Y-%m-%d"

html_theme_options = {
    "logo": {"text": "nicegui-shadcn"},
    "search_bar_text": "搜索文档…",
    "github_url": f"https://github.com/{_GITHUB_USER}/{_GITHUB_REPO}",
    "navbar_align": "content",
    "navbar_start": ["navbar-logo"],
    "navbar_center": ["navbar-nav"],
    "navbar_end": ["theme-switcher", "navbar-icon-links"],
    "navbar_persistent": ["search-button"],
    "secondary_sidebar_items": ["page-toc", "edit-this-page"],
    "show_prev_next": True,
    "show_toc_level": 2,
    "navigation_with_keys": True,
    "use_edit_page_button": True,
    "footer_start": ["copyright"],
    "footer_center": ["sphinx-version"],
    "footer_end": ["theme-version"],
    "icon_links": [
        {
            "name": "GitHub",
            "url": f"https://github.com/{_GITHUB_USER}/{_GITHUB_REPO}",
            "icon": "fa-brands fa-github",
            "type": "fontawesome",
        },
        {
            "name": "PyPI",
            "url": "https://pypi.org/project/nicegui-shadcn/",
            "icon": "fa-solid fa-box",
            "type": "fontawesome",
        },
    ],
}

html_context = {
    # ``default_mode`` is read straight from the Jinja context by the theme
    # (layout.html / navbar-logo.html); it is *not* a theme.conf option, so
    # putting it in html_theme_options only earns
    # "WARNING: unsupported theme option 'default_mode' given" and leaves
    # <html> without data-mode, which makes the theme log
    # "Got invalid theme mode: . Resetting to auto." on every page load.
    "default_mode": "auto",
    "github_user": _GITHUB_USER,
    "github_repo": _GITHUB_REPO,
    "github_version": _GITHUB_BRANCH,
    "doc_path": "docs",
}

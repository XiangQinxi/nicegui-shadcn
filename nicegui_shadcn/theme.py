"""Asset plumbing for the shadcn/ui extension.

A NiceGUI extension has to get three things onto the page *before* the first
component renders:

1. the compiled Tailwind/shadcn stylesheet,
2. the ``reka-ui`` ESM bundle that the stateful components import, and
3. an import-map entry so that a ``.vue`` script can write the readable

   .. code-block:: js

       import { DialogRoot } from 'reka-ui';

   instead of a versioned, content-hashed URL.

All three are registered as a side effect of importing :mod:`nicegui_shadcn`,
which is early enough for both script mode and page-decorator mode.

Why a plain ``<link>`` and not ``ui.add_css``
---------------------------------------------
``ui.add_css`` *inlines* the stylesheet into a ``addStyle(...)`` JavaScript
call, so the browser only sees the rules once the socket handshake is done.
shadcn's look is entirely class-driven, so that would produce a visible flash
of unstyled content on every reload. A stylesheet link in the document head
paints with the first frame instead.

Why ``reka-ui`` is served from ``static/`` rather than from a CDN
-----------------------------------------------------------------
NiceGUI bundles Vue 3.5.22 and the import map already maps the bare specifier
``vue`` to it. The bundled ``reka-ui`` build keeps ``vue`` external, so both
the bundle and the components share one Vue instance; using a CDN copy would
either duplicate Vue or break the import map.
"""

from __future__ import annotations

from pathlib import Path

from nicegui import app, ui
from nicegui.dependencies import register_importmap_override

__all__ = ['CSS_URL', 'PACKAGE_DIR', 'STATIC_DIR', 'URL_PREFIX', 'setup']

PACKAGE_DIR = Path(__file__).parent
STATIC_DIR = PACKAGE_DIR / 'static'

URL_PREFIX = '/_nicegui_shadcn'
'''URL prefix under which the extension serves its static assets.'''

CSS_URL = f'{URL_PREFIX}/shadcn.css'
'''URL of the compiled shadcn/Tailwind stylesheet.'''

REKA_UI_URL = f'{URL_PREFIX}/vendor/reka-ui.js'
'''URL of the ``reka-ui`` ESM bundle.'''

REKA_UI_SPECIFIER = 'reka-ui'
'''Bare specifier that ``.vue`` scripts use to import ``reka-ui``.'''

_HEAD_HTML = f'<link rel="stylesheet" href="{CSS_URL}">'

_installed = False


def setup() -> None:
    """Register stylesheet, static files and the import-map override.

    This runs automatically when :mod:`nicegui_shadcn` is imported; calling it
    again is a cheap no-op. It exists so that a lazily imported package can be
    activated explicitly::

        from nicegui_shadcn import setup
        setup()
    """
    global _installed
    if _installed:
        return
    _installed = True

    app.add_static_files(URL_PREFIX, str(STATIC_DIR))
    register_importmap_override(REKA_UI_SPECIFIER, REKA_UI_URL)
    ui.add_head_html(_HEAD_HTML, shared=True)


setup()

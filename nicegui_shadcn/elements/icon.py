"""Icon helper.

shadcn/ui pairs with `lucide <https://lucide.dev>`_ icons. Bundling
``lucide-vue-next`` would mean shipping and serving another ~200 kB of
JavaScript just to draw a handful of glyphs, so :mod:`nicegui_shadcn.icons`
inlines the paths as raw SVG markup and this module wraps them in a NiceGUI
element.
"""

from __future__ import annotations

from typing import Any

from nicegui import ui

from .. import icons

__all__ = ['icon']


def icon(name: str, *, size: int | float = 16, classes: str = '', **attrs: Any) -> ui.html:
    """Create an inline SVG icon element.

    :param name: lucide icon name, e.g. ``'check'`` (see
        :data:`nicegui_shadcn.icons.ICON_NAMES`).
    :param size: width/height in pixels used for the SVG attributes. Components
        normally let CSS take over through shadcn's ``[&_svg]:size-4`` rules.
    :param classes: extra classes for the wrapping ``<span>``.
    :param attrs: extra SVG attributes.
    :return: the wrapping element, so it can be chained or stored.
    """
    element = ui.html(icons.svg(name, size=size, **attrs), sanitize=False, tag='span')
    if classes:
        element.classes(classes)
    return element

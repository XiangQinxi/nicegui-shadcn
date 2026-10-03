"""Scroll area: a styled, cross-browser replacement for the native scrollbar.

::

    with shadcn.scroll_area().classes('h-72 w-64 rounded-md border'):
        with ui.column().classes('gap-2 p-4'):
            ...

The whole structure -- viewport, both scrollbars and the corner -- is one
component, because the parts only work as siblings under reka-ui's root: the
viewport has to be the box that scrolls, and the scrollbars have to sit beside it
rather than inside it. Everything added with ``with`` therefore goes into the
viewport.

The class list is worth reading twice: without an explicit height the area grows to
fit its content and there is nothing to scroll, so set one (``h-72`` and friends
are in the runtime vocabulary).
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from .base import ShadcnElement, option

__all__ = ['ScrollArea', 'scroll_area']

_SCROLL_AREA_TYPES = {name: name for name in ('hover', 'scroll', 'auto', 'always')}


class ScrollArea(ShadcnElement, component='shadcn_scroll_area.vue'):
    """A container with styled scrollbars.

    :param type_: when the scrollbars are visible: ``'hover'`` (default, only
        while the pointer is over the area), ``'scroll'`` (fade out shortly after
        scrolling stops), ``'auto'`` (while scrolling, and whenever the content
        overflows) or ``'always'``.
    :param scroll_hide_delay: milliseconds a scrollbar stays visible after the
        interaction ends, for the types that hide themselves.
    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """

    def __init__(self,
                 *,
                 type_: str = 'hover',
                 scroll_hide_delay: int = 600,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(classes=classes, **kwargs)
        self._props['type'] = option('scroll area type', type_, _SCROLL_AREA_TYPES)
        self._props['scrollHideDelay'] = int(scroll_hide_delay)


def scroll_area(*, type_: str = 'hover', **kwargs: Any) -> ScrollArea:
    """Create a :class:`ScrollArea`.

    :param type_: when the scrollbars are visible: ``'hover'``, ``'scroll'``,
        ``'auto'`` or ``'always'``.
    """
    return ScrollArea(type_=type_, **kwargs)

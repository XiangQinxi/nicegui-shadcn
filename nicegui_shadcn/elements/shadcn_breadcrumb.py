"""Breadcrumb: the trail of links showing where the current page sits.

Every part is a plain styled element, so the trail is composed with ``with``
blocks and no client-side behaviour is involved beyond the links themselves.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from nicegui.elements.html import Html
from nicegui.elements.mixins.text_element import TextElement

from .. import icons
from .base import ShadcnElement

__all__ = [
    'Breadcrumb', 'BreadcrumbEllipsis', 'BreadcrumbItem', 'BreadcrumbLink', 'BreadcrumbList',
    'BreadcrumbPage', 'BreadcrumbSeparator',
    'breadcrumb', 'breadcrumb_ellipsis', 'breadcrumb_item', 'breadcrumb_link', 'breadcrumb_list',
    'breadcrumb_page', 'breadcrumb_separator',
]

_BREADCRUMB_CLASSES = 'text-muted-foreground'

_BREADCRUMB_LIST_CLASSES = 'text-muted-foreground flex flex-wrap items-center gap-1.5 text-sm break-words sm:gap-2.5'

_BREADCRUMB_ITEM_CLASSES = 'inline-flex items-center gap-1.5'

_BREADCRUMB_LINK_CLASSES = 'hover:text-foreground transition-colors'

_BREADCRUMB_PAGE_CLASSES = 'text-foreground font-normal'

_BREADCRUMB_SEPARATOR_CLASSES = "[&>svg]:size-3.5 flex items-center"

_BREADCRUMB_ELLIPSIS_CLASSES = 'flex size-9 items-center justify-center'


class Breadcrumb(ShadcnElement, default_classes=_BREADCRUMB_CLASSES):
    """The ``<nav>`` holding a :class:`BreadcrumbList`.

    The accessible name is fixed to ``'breadcrumb'``, which is what tells a screen
    reader that this group of links is a trail.
    """

    def __init__(self,
                 *,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(tag='nav', classes=classes, **kwargs)
        self._props['aria-label'] = 'breadcrumb'


class BreadcrumbList(ShadcnElement, default_classes=_BREADCRUMB_LIST_CLASSES):
    """The ``<ol>`` of :class:`BreadcrumbItem` entries."""

    def __init__(self,
                 *,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(tag='ol', classes=classes, **kwargs)


class BreadcrumbItem(ShadcnElement, default_classes=_BREADCRUMB_ITEM_CLASSES):
    """One ``<li>`` in the trail."""

    def __init__(self,
                 *,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(tag='li', classes=classes, **kwargs)


class BreadcrumbLink(ShadcnElement, TextElement, default_classes=_BREADCRUMB_LINK_CLASSES):
    """A clickable step in the trail.

    :param text: the label.
    :param href: target URL; without one the ``<a>`` is not focusable, so give it
        a real target or use :class:`BreadcrumbPage` for the current step.
    """

    def __init__(self,
                 text: str = '',
                 *,
                 href: str | None = None,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        kwargs.setdefault('tag', 'a')
        super().__init__(text=text, classes=classes, **kwargs)
        if href is not None:
            self._props['href'] = href


class BreadcrumbPage(ShadcnElement, TextElement, default_classes=_BREADCRUMB_PAGE_CLASSES):
    """The last step: the page you are already on.

    It is rendered as a span marked ``aria-current="page"`` rather than as a link,
    because there is nowhere to navigate to.
    """

    def __init__(self,
                 text: str = '',
                 *,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        kwargs.setdefault('tag', 'span')
        super().__init__(text=text, classes=classes, **kwargs)
        self._props['role'] = 'link'
        self._props['aria-disabled'] = 'true'
        self._props['aria-current'] = 'page'


class BreadcrumbSeparator(ShadcnElement, Html, default_classes=_BREADCRUMB_SEPARATOR_CLASSES):
    """The divider drawn between two steps.

    :param icon: name of the glyph to draw, or ``None`` for a bare ``<li>`` you
        can fill yourself.
    """

    def __init__(self,
                 *,
                 icon: str | None = 'chevron-right',
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        markup = icons.svg(icon, size=14) if icon else ''
        super().__init__(content=markup, sanitize=False, tag='li', classes=classes, **kwargs)
        self._props['role'] = 'presentation'
        self._props['aria-hidden'] = 'true'


class BreadcrumbEllipsis(ShadcnElement, Html, default_classes=_BREADCRUMB_ELLIPSIS_CLASSES):
    """A stand-in for steps that were collapsed away.

    The element is presentational, so the three dots are not read out, but the
    visually hidden ``More`` text inside it is -- which is why it carries no
    ``aria-hidden`` of its own (that would swallow the whole subtree).
    """

    def __init__(self,
                 *,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        markup = (
            icons.svg('ellipsis', size=16)
            + '<span class="sr-only">More</span>'
        )
        super().__init__(content=markup, sanitize=False, tag='span', classes=classes, **kwargs)
        self._props['role'] = 'presentation'


def breadcrumb(**kwargs: Any) -> Breadcrumb:
    """Create a :class:`Breadcrumb`."""
    return Breadcrumb(**kwargs)


def breadcrumb_list(**kwargs: Any) -> BreadcrumbList:
    """Create a :class:`BreadcrumbList`."""
    return BreadcrumbList(**kwargs)


def breadcrumb_item(**kwargs: Any) -> BreadcrumbItem:
    """Create a :class:`BreadcrumbItem`."""
    return BreadcrumbItem(**kwargs)


def breadcrumb_link(text: str = '', **kwargs: Any) -> BreadcrumbLink:
    """Create a :class:`BreadcrumbLink`."""
    return BreadcrumbLink(text, **kwargs)


def breadcrumb_page(text: str = '', **kwargs: Any) -> BreadcrumbPage:
    """Create a :class:`BreadcrumbPage`."""
    return BreadcrumbPage(text, **kwargs)


def breadcrumb_separator(*, icon: str | None = 'chevron-right', **kwargs: Any) -> BreadcrumbSeparator:
    """Create a :class:`BreadcrumbSeparator`."""
    return BreadcrumbSeparator(icon=icon, **kwargs)


def breadcrumb_ellipsis(**kwargs: Any) -> BreadcrumbEllipsis:
    """Create a :class:`BreadcrumbEllipsis`."""
    return BreadcrumbEllipsis(**kwargs)

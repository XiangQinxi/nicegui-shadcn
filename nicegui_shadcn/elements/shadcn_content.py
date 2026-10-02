"""Content and status display components.

Grouped in one module because they are all thin wrappers around a styled element
with no behaviour of their own: a spinner, a keyboard hint, a status marker, the
empty-state family and an aspect-ratio box.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from nicegui import ui
from nicegui.elements.html import Html
from nicegui.elements.mixins.text_element import TextElement

from .. import icons
from .base import ShadcnElement, Text, option
from .icon import icon as _icon

__all__ = [
    'AspectRatio', 'Empty', 'EmptyContent', 'EmptyDescription', 'EmptyHeader', 'EmptyMedia', 'EmptyTitle',
    'Kbd', 'Marker', 'Spinner',
    'aspect_ratio', 'empty', 'empty_content', 'empty_description', 'empty_header', 'empty_media', 'empty_title',
    'kbd', 'marker', 'spinner',
]

_SPINNER_CLASSES = 'inline-flex shrink-0'

_SPINNER_MARKUP = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" '
    'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
    'role="status" aria-label="{label}" class="animate-spin">{path}</svg>'
)

_KBD_CLASSES = (
    'bg-muted text-muted-foreground pointer-events-none inline-flex h-5 w-fit min-w-5 items-center justify-center '
    'gap-1 rounded-sm px-1 font-sans text-xs font-medium select-none '
    "[&_svg:not([class*='size-'])]:size-3"
)

_MARKER_CLASSES = 'flex items-center gap-2 text-sm'

_MARKER_DOT_CLASSES = 'size-2 rounded-full'

_MARKER_ICON_CLASSES = "[&_svg:not([class*='size-'])]:size-4 flex items-center"

_MARKER_VARIANTS = {
    'default': 'bg-primary',
    'success': 'bg-green-500',
    'warning': 'bg-yellow-500',
    'error': 'bg-red-500',
    'info': 'bg-blue-500',
}

# The icon variant paints the glyph with ``text-*`` rather than ``bg-*``: the glyph is drawn
# with ``stroke="currentColor"``, so a background colour would tint the whole wrapper box.
_MARKER_ICON_VARIANTS = {
    'default': 'text-primary',
    'success': 'text-green-500',
    'warning': 'text-yellow-500',
    'error': 'text-red-500',
    'info': 'text-blue-500',
}

_EMPTY_CLASSES = (
    'flex min-w-0 flex-1 flex-col items-center justify-center gap-6 rounded-lg border border-dashed p-6 '
    'text-center text-balance md:p-12'
)

_EMPTY_HEADER_CLASSES = 'flex max-w-sm flex-col items-center gap-2 text-center'

_EMPTY_MEDIA_CLASSES = 'mb-2 flex shrink-0 items-center justify-center [&_svg]:pointer-events-none [&_svg]:shrink-0'

_EMPTY_MEDIA_VARIANTS = {
    'default': 'bg-transparent',
    'icon': (
        'bg-muted text-foreground flex size-10 shrink-0 items-center justify-center rounded-lg '
        "[&_svg:not([class*='size-'])]:size-6"
    ),
}

_EMPTY_TITLE_CLASSES = 'text-lg font-medium tracking-tight'

_EMPTY_DESCRIPTION_CLASSES = (
    'text-muted-foreground text-sm leading-relaxed [&>a]:underline [&>a]:underline-offset-4 [&>a:hover]:text-primary'
)

_EMPTY_CONTENT_CLASSES = 'flex w-full max-w-sm min-w-0 flex-col items-center gap-4 text-sm text-balance'


class Spinner(ShadcnElement, Html, default_classes=_SPINNER_CLASSES):
    """A spinning indicator for work in progress.

    The element itself is a ``<span>`` wrapper -- like :func:`nicegui_shadcn.icons.svg`,
    which also hands back markup rather than an element tree -- so CSS classes given
    here land on the wrapper. Use ``size`` to resize the glyph itself.

    :param size: width and height of the SVG in pixels.
    :param label: accessible name announced to screen readers.
    """

    def __init__(self,
                 *,
                 size: int | float = 16,
                 label: str = 'Loading',
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        markup = _SPINNER_MARKUP.format(size=size, label=label, path=icons.glyph('loader-circle'))
        super().__init__(content=markup, sanitize=False, tag='span', classes=classes, **kwargs)


class Kbd(ShadcnElement, TextElement, default_classes=_KBD_CLASSES):
    """A keyboard key or shortcut hint, e.g. ``kbd('Ctrl')``.

    Renders a real ``<kbd>`` element, which is what tells a screen reader that a
    letter stands for a key rather than for text.
    """

    def __init__(self,
                 text: str = '',
                 *,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        kwargs.setdefault('tag', 'kbd')
        super().__init__(text=text, classes=classes, **kwargs)


class Marker(ShadcnElement, default_classes=_MARKER_CLASSES):
    """A status marker: a coloured dot or icon followed by a short label.

    :param text: the label.
    :param variant: ``'default'``, ``'success'``, ``'warning'``, ``'error'`` or
        ``'info'`` -- it colours the dot.
    :param icon: draw this glyph instead of a dot, e.g. ``'circle-check'``.
    :param pulse: pulse the dot to signal an in-progress state.
    """

    def __init__(self,
                 text: str = '',
                 *,
                 variant: str = 'default',
                 icon: str | None = None,
                 pulse: bool = False,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(classes=classes, **kwargs)
        dot_colour = option('marker variant', variant, _MARKER_VARIANTS)
        with self:
            if icon is None:
                dot_classes = f'{_MARKER_DOT_CLASSES} {dot_colour}'
                if pulse:
                    dot_classes = f'{dot_classes} animate-pulse'
                ui.element('span').classes(dot_classes)
            else:
                _icon(icon, size=16, classes=f'{_MARKER_ICON_CLASSES} {_MARKER_ICON_VARIANTS[variant]}')
            Text(text)


class Empty(ShadcnElement, default_classes=_EMPTY_CLASSES):
    """The placeholder shown when a list, table or page has nothing to display.

    Compose it from the parts::

        with shadcn.empty().classes('w-full'):
            with shadcn.empty_header():
                with shadcn.empty_media(variant='icon'):
                    shadcn.icon('search')
                shadcn.empty_title('No results')
                shadcn.empty_description('Try a different search term.')
                with shadcn.empty_content():
                    shadcn.button('Clear filters', variant='outline')
    """


class EmptyHeader(ShadcnElement, default_classes=_EMPTY_HEADER_CLASSES):
    """The centred stack inside an :class:`Empty`."""


class EmptyMedia(ShadcnElement, default_classes=_EMPTY_MEDIA_CLASSES):
    """Holds the illustration or icon at the top of an :class:`Empty`.

    :param variant: ``'default'`` leaves the box transparent, ``'icon'`` puts the
        content on a muted rounded square.
    """

    def __init__(self,
                 *,
                 variant: str = 'default',
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(
            variant_classes=option('empty media variant', variant, _EMPTY_MEDIA_VARIANTS),
            classes=classes,
            **kwargs,
        )


class EmptyTitle(ShadcnElement, TextElement, default_classes=_EMPTY_TITLE_CLASSES):
    """The headline of an :class:`Empty`."""

    def __init__(self,
                 text: str = '',
                 *,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(text=text, classes=classes, **kwargs)


class EmptyDescription(ShadcnElement, TextElement, default_classes=_EMPTY_DESCRIPTION_CLASSES):
    """The explanatory line under an :class:`EmptyTitle`."""

    def __init__(self,
                 text: str = '',
                 *,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(text=text, classes=classes, **kwargs)


class EmptyContent(ShadcnElement, default_classes=_EMPTY_CONTENT_CLASSES):
    """The call-to-action area at the bottom of an :class:`Empty`."""


class AspectRatio(ShadcnElement, component='shadcn_aspect_ratio.vue'):
    """A box that keeps a fixed width-to-height ratio.

    :param ratio: width divided by height, e.g. ``16 / 9``.
    """

    def __init__(self,
                 ratio: int | float = 1,
                 *,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        value = float(ratio)
        if not value > 0:
            raise ValueError(f'ratio must be positive, got {ratio!r}')
        super().__init__(classes=classes, **kwargs)
        self._props['ratio'] = value


def spinner(*, size: int | float = 16, label: str = 'Loading', **kwargs: Any) -> Spinner:
    """Create a :class:`Spinner`."""
    return Spinner(size=size, label=label, **kwargs)


def kbd(text: str = '', **kwargs: Any) -> Kbd:
    """Create a :class:`Kbd`."""
    return Kbd(text, **kwargs)


def marker(text: str = '', **kwargs: Any) -> Marker:
    """Create a :class:`Marker`."""
    return Marker(text, **kwargs)


def empty(**kwargs: Any) -> Empty:
    """Create an :class:`Empty`."""
    return Empty(**kwargs)


def empty_header(**kwargs: Any) -> EmptyHeader:
    """Create an :class:`EmptyHeader`."""
    return EmptyHeader(**kwargs)


def empty_media(*, variant: str = 'default', **kwargs: Any) -> EmptyMedia:
    """Create an :class:`EmptyMedia`."""
    return EmptyMedia(variant=variant, **kwargs)


def empty_title(text: str = '', **kwargs: Any) -> EmptyTitle:
    """Create an :class:`EmptyTitle`."""
    return EmptyTitle(text, **kwargs)


def empty_description(text: str = '', **kwargs: Any) -> EmptyDescription:
    """Create an :class:`EmptyDescription`."""
    return EmptyDescription(text, **kwargs)


def empty_content(**kwargs: Any) -> EmptyContent:
    """Create an :class:`EmptyContent`."""
    return EmptyContent(**kwargs)


def aspect_ratio(ratio: int | float = 1, **kwargs: Any) -> AspectRatio:
    """Create an :class:`AspectRatio`."""
    return AspectRatio(ratio, **kwargs)

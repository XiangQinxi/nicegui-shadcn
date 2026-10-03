"""Presentational components: badge, avatar, alert, progress and table."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from nicegui import ui
from nicegui.elements.mixins.text_element import TextElement

from .. import icons
from .base import ShadcnElement, option

__all__ = [
    'Alert', 'AlertDescription', 'AlertTitle', 'Avatar', 'Badge', 'Progress',
    'Table', 'TableBody', 'TableCaption', 'TableCell', 'TableFooter', 'TableHead',
    'TableHeader', 'TableRow',
    'alert', 'alert_description', 'alert_title', 'avatar', 'badge', 'progress',
    'table', 'table_body', 'table_caption', 'table_cell', 'table_container',
    'table_footer', 'table_head', 'table_header', 'table_row',
]

# --------------------------------------------------------------------------- #
# Badge
# --------------------------------------------------------------------------- #

_BADGE_BASE = (
    'inline-flex w-fit shrink-0 items-center justify-center gap-1 overflow-hidden '
    'whitespace-nowrap rounded-md border px-2 py-0.5 text-xs font-medium '
    'transition-[color,box-shadow] '
    '[&>svg]:pointer-events-none [&>svg]:size-3'
)

_BADGE_VARIANTS = {
    'default': 'border-transparent bg-primary text-primary-foreground',
    'secondary': 'border-transparent bg-secondary text-secondary-foreground',
    'destructive': (
        'border-transparent bg-destructive text-white '
        'dark:bg-destructive/60'
    ),
    'outline': 'text-foreground',
}


class Badge(ShadcnElement, TextElement, default_classes=_BADGE_BASE):
    """A small status label.

    :param text: the text to display.
    :param variant: ``default``, ``secondary``, ``destructive`` or ``outline``.
    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """

    def __init__(self,
                 text: str = '',
                 *,
                 variant: str = 'default',
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(
            tag='span',
            text=text,
            classes=classes,
            variant_classes=option('badge variant', variant, _BADGE_VARIANTS),
            **kwargs,
        )


# --------------------------------------------------------------------------- #
# Avatar
# --------------------------------------------------------------------------- #

_AVATAR_SIZES = {
    'default': 'size-8',
    'sm': 'size-6',
    'lg': 'size-10',
    'xl': 'size-12',
}


class Avatar(ShadcnElement, default_classes='relative flex shrink-0 overflow-hidden rounded-full'):
    """A circular avatar showing an image or a text fallback.

    :param src: image URL. When omitted (or when the image fails to load) the
        fallback text is shown instead.
    :param fallback: initials shown when there is no image.
    :param size: ``default``, ``sm``, ``lg`` or ``xl``.
    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """

    def __init__(self,
                 *,
                 src: str | None = None,
                 fallback: str = '',
                 size: str = 'default',
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(
            tag='div',
            classes=classes,
            variant_classes=option('avatar size', size, _AVATAR_SIZES),
            **kwargs,
        )
        self._image: ShadcnElement | None = None
        self._fallback: ShadcnElement | None = None
        if src:
            with self:
                self._image = ShadcnElement(
                    tag='img',
                    variant_classes='aspect-square size-full object-cover',
                )
                self._image._props['src'] = src  # pylint: disable=protected-access
                self._image._props['alt'] = fallback or 'avatar'  # pylint: disable=protected-access
        if fallback:
            with self:
                self._fallback = ShadcnElement(
                    tag='span',
                    variant_classes=(
                        'flex size-full items-center justify-center rounded-full '
                        'bg-muted text-xs font-medium'
                    ),
                )
                self._fallback._text = fallback  # pylint: disable=protected-access


# --------------------------------------------------------------------------- #
# Alert
# --------------------------------------------------------------------------- #

_ALERT_BASE = (
    'relative grid w-full items-start gap-y-0.5 rounded-lg border px-4 py-3 text-sm '
    'grid-cols-[1rem_1fr] gap-x-3 [&>svg]:size-4 [&>svg]:translate-y-0.5'
)

_ALERT_VARIANTS = {
    'default': 'bg-card text-card-foreground',
    'destructive': 'bg-card text-destructive',
}

_ALERT_ICONS = {
    'default': 'info',
    'destructive': 'triangle-alert',
}


class Alert(ShadcnElement, default_classes=_ALERT_BASE):
    """A callout for important messages.

    :param variant: ``default`` or ``destructive``.
    :param icon: lucide icon name. Defaults to ``info`` / ``triangle-alert``.
    :param title: optional shortcut that creates an :class:`AlertTitle` child.
    :param description: optional shortcut that creates an
        :class:`AlertDescription` child.
    :param classes: extra utility classes, merged with ``cn()`` semantics.

    Children added with ``with`` are appended after the icon, so the usual
    shadcn composition works too::

        with shadcn.alert():
            shadcn.alert_title('Heads up!')
            shadcn.alert_description('You can add components with the CLI.')
    """

    def __init__(self,
                 *,
                 variant: str = 'default',
                 icon: str | None = None,
                 title: str | None = None,
                 description: str | None = None,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(
            tag='div',
            classes=classes,
            variant_classes=option('alert variant', variant, _ALERT_VARIANTS),
            **kwargs,
        )
        self._props['role'] = 'alert'
        with self:
            ui.html(icons.svg(icon or _ALERT_ICONS[variant]), sanitize=False, tag='span')
        if title is not None:
            with self:
                AlertTitle(title)
        if description is not None:
            with self:
                AlertDescription(description)


class AlertTitle(ShadcnElement, TextElement, default_classes='col-start-2 min-h-4 font-medium tracking-tight'):
    """The title line of an :class:`Alert`.

    :param text: the text to display.
    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """

    def __init__(self, text: str = '', *, classes: str | Iterable[str] | None = None, **kwargs: Any) -> None:
        super().__init__(tag='div', text=text, classes=classes, **kwargs)


class AlertDescription(ShadcnElement, TextElement, default_classes='col-start-2 grid gap-1 text-sm text-muted-foreground'):
    """The body of an :class:`Alert`.

    :param text: the text to display.
    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """

    def __init__(self, text: str = '', *, classes: str | Iterable[str] | None = None, **kwargs: Any) -> None:
        super().__init__(tag='div', text=text, classes=classes, **kwargs)


# --------------------------------------------------------------------------- #
# Progress
# --------------------------------------------------------------------------- #


class Progress(ShadcnElement, default_classes='relative h-2 w-full overflow-hidden rounded-full bg-primary/20'):
    """A horizontal progress bar.

    :param value: progress between 0 and 100.
    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """

    def __init__(self,
                 value: float = 0,
                 *,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(tag='div', classes=classes, **kwargs)
        self._props['role'] = 'progressbar'
        with self:
            self._indicator = ShadcnElement(
                tag='div',
                variant_classes='h-full w-full flex-1 bg-primary transition-all',
            )
        self.set_value(value)

    def set_value(self, value: float) -> None:
        """Set the progress value (clamped to 0..100).

        :param value: the new progress between 0 and 100; anything outside that
            range is clamped to the nearer end.
        """
        clamped = max(0.0, min(100.0, float(value)))
        self._value = clamped
        self._props['aria-valuenow'] = clamped
        self._indicator.style(f'transform: translateX(-{100 - clamped}%)')
        self.update()


# --------------------------------------------------------------------------- #
# Table
# --------------------------------------------------------------------------- #


class Table(ShadcnElement, default_classes='w-full caption-bottom text-sm'):
    """A shadcn/ui table. Wrap it in ``shadcn.table_container()`` to scroll.

    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """

    def __init__(self, *, classes: str | Iterable[str] | None = None, **kwargs: Any) -> None:
        super().__init__(tag='table', classes=classes, **kwargs)


class TableHeader(ShadcnElement, default_classes='[&_tr]:border-b'):
    """The ``<thead>`` of a :class:`Table`.

    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """

    def __init__(self, *, classes: str | Iterable[str] | None = None, **kwargs: Any) -> None:
        super().__init__(tag='thead', classes=classes, **kwargs)


class TableBody(ShadcnElement, default_classes='[&_tr:last-child]:border-0'):
    """The ``<tbody>`` of a :class:`Table`.

    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """

    def __init__(self, *, classes: str | Iterable[str] | None = None, **kwargs: Any) -> None:
        super().__init__(tag='tbody', classes=classes, **kwargs)


class TableFooter(ShadcnElement, default_classes='border-t bg-muted/50 font-medium'):
    """The ``<tfoot>`` of a :class:`Table`.

    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """

    def __init__(self, *, classes: str | Iterable[str] | None = None, **kwargs: Any) -> None:
        super().__init__(tag='tfoot', classes=classes, **kwargs)


class TableRow(ShadcnElement, default_classes='border-b transition-colors hover:bg-muted/50'):
    """A ``<tr>`` of a :class:`Table`.

    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """

    def __init__(self, *, classes: str | Iterable[str] | None = None, **kwargs: Any) -> None:
        super().__init__(tag='tr', classes=classes, **kwargs)


class TableHead(ShadcnElement, TextElement, default_classes='h-10 whitespace-nowrap px-2 text-left align-middle font-medium text-foreground'):
    """A header ``<th>`` of a :class:`Table`.

    :param text: the text to display.
    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """

    def __init__(self, text: str = '', *, classes: str | Iterable[str] | None = None, **kwargs: Any) -> None:
        super().__init__(tag='th', text=text, classes=classes, **kwargs)


class TableCell(ShadcnElement, TextElement, default_classes='whitespace-nowrap p-2 align-middle'):
    """A body ``<td>`` of a :class:`Table`.

    :param text: the text to display.
    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """

    def __init__(self, text: str = '', *, classes: str | Iterable[str] | None = None, **kwargs: Any) -> None:
        super().__init__(tag='td', text=text, classes=classes, **kwargs)


class TableCaption(ShadcnElement, TextElement, default_classes='mt-4 text-sm text-muted-foreground'):
    """The ``<caption>`` of a :class:`Table`.

    :param text: the text to display.
    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """

    def __init__(self, text: str = '', *, classes: str | Iterable[str] | None = None, **kwargs: Any) -> None:
        super().__init__(tag='caption', text=text, classes=classes, **kwargs)


def table_container(*, classes: str | Iterable[str] | None = None, **kwargs: Any) -> ShadcnElement:
    """Create the scroll container that shadcn wraps every table in.

    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """
    return ShadcnElement(
        tag='div',
        variant_classes='relative w-full overflow-x-auto',
        classes=classes,
        **kwargs,
    )


# --------------------------------------------------------------------------- #
# Factories
# --------------------------------------------------------------------------- #


def badge(text: str = '', **kwargs: Any) -> Badge:
    """Create a :class:`Badge`.

    :param text: the text to display.
    """
    return Badge(text, **kwargs)


def avatar(**kwargs: Any) -> Avatar:
    """Create an :class:`Avatar`."""
    return Avatar(**kwargs)


def alert(**kwargs: Any) -> Alert:
    """Create an :class:`Alert`."""
    return Alert(**kwargs)


def alert_title(text: str = '', **kwargs: Any) -> AlertTitle:
    """Create an :class:`AlertTitle`.

    :param text: the text to display.
    """
    return AlertTitle(text, **kwargs)


def alert_description(text: str = '', **kwargs: Any) -> AlertDescription:
    """Create an :class:`AlertDescription`.

    :param text: the text to display.
    """
    return AlertDescription(text, **kwargs)


def progress(value: float = 0, **kwargs: Any) -> Progress:
    """Create a :class:`Progress`.

    :param value: the progress percentage in ``0..100``; values outside the
        range are clamped.
    """
    return Progress(value, **kwargs)


def table(**kwargs: Any) -> Table:
    """Create a :class:`Table`."""
    return Table(**kwargs)


def table_header(**kwargs: Any) -> TableHeader:
    """Create a :class:`TableHeader`."""
    return TableHeader(**kwargs)


def table_body(**kwargs: Any) -> TableBody:
    """Create a :class:`TableBody`."""
    return TableBody(**kwargs)


def table_footer(**kwargs: Any) -> TableFooter:
    """Create a :class:`TableFooter`."""
    return TableFooter(**kwargs)


def table_row(**kwargs: Any) -> TableRow:
    """Create a :class:`TableRow`."""
    return TableRow(**kwargs)


def table_head(text: str = '', **kwargs: Any) -> TableHead:
    """Create a :class:`TableHead`.

    :param text: the text to display.
    """
    return TableHead(text, **kwargs)


def table_cell(text: str = '', **kwargs: Any) -> TableCell:
    """Create a :class:`TableCell`.

    :param text: the text to display.
    """
    return TableCell(text, **kwargs)


def table_caption(text: str = '', **kwargs: Any) -> TableCaption:
    """Create a :class:`TableCaption`.

    :param text: the text to display.
    """
    return TableCaption(text, **kwargs)

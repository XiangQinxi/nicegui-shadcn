"""Item: the flexible row used for list entries, settings and media objects.

The parts describe one row -- media, content, actions, an optional header and
footer -- and can be nested in any combination.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from nicegui.elements.mixins.text_element import TextElement

from .base import ShadcnElement, option

__all__ = [
    'Item', 'ItemActions', 'ItemContent', 'ItemDescription', 'ItemFooter', 'ItemGroup',
    'ItemHeader', 'ItemMedia', 'ItemSeparator', 'ItemTitle',
    'item', 'item_actions', 'item_content', 'item_description', 'item_footer', 'item_group',
    'item_header', 'item_media', 'item_separator', 'item_title',
]

_ITEM_GROUP_CLASSES = 'flex flex-col'

_ITEM_BASE = (
    'flex flex-wrap items-center gap-4 rounded-md border border-transparent p-4 text-sm '
    'transition-colors outline-none focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50 '
    "[a]:transition-colors [a]:duration-100 [a]:outline-none [a]:focus-visible:ring-2 [a]:focus-visible:ring-ring/50"
)

_ITEM_VARIANTS = {
    'default': '',
    'outline': 'border-border',
    'muted': 'bg-muted/50',
}

_ITEM_SIZES = {
    'default': '',
    'sm': 'gap-2.5 px-4 py-3',
}

_ITEM_MEDIA_CLASSES = 'flex shrink-0 items-center justify-center gap-2'

_ITEM_MEDIA_VARIANTS = {
    'default': '',
    'icon': "bg-muted size-8 rounded-sm [&_svg:not([class*='size-'])]:size-4",
    'image': 'size-10 overflow-hidden rounded-sm [&_img]:size-full [&_img]:object-cover',
}

_ITEM_CONTENT_CLASSES = 'flex flex-1 flex-col gap-1.5'

_ITEM_TITLE_CLASSES = 'flex w-fit items-center gap-2 text-sm leading-snug font-medium'

_ITEM_DESCRIPTION_CLASSES = 'text-muted-foreground line-clamp-2 text-sm leading-normal font-normal'

_ITEM_ACTIONS_CLASSES = 'flex items-center gap-2'

_ITEM_HEADER_CLASSES = 'flex basis-full items-center justify-between gap-2'

_ITEM_FOOTER_CLASSES = 'flex basis-full items-center justify-between gap-2'

_ITEM_SEPARATOR_CLASSES = 'bg-border -mx-4 h-px shrink-0'


class ItemGroup(ShadcnElement, default_classes=_ITEM_GROUP_CLASSES):
    """A vertical stack of :class:`Item` rows that reads as one list."""

    def __init__(self,
                 *,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(classes=classes, **kwargs)
        self._props['role'] = 'list'


class Item(ShadcnElement, default_classes=_ITEM_BASE):
    """A single row.

    :param variant: ``'default'`` is borderless, ``'outline'`` draws the border and
        ``'muted'`` fills the row with the muted colour.
    :param size: ``'default'`` or ``'sm'`` for tighter padding.
    """

    def __init__(self,
                 *,
                 variant: str = 'default',
                 size: str = 'default',
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(
            variant_classes=' '.join([
                option('item variant', variant, _ITEM_VARIANTS),
                option('item size', size, _ITEM_SIZES),
            ]),
            classes=classes,
            **kwargs,
        )
        self._props['data-slot'] = 'item'
        self._props['data-variant'] = variant
        self._props['data-size'] = size


class ItemMedia(ShadcnElement, default_classes=_ITEM_MEDIA_CLASSES):
    """The leading box of an :class:`Item`: an avatar, an icon or an image.

    :param variant: ``'default'`` leaves the box bare, ``'icon'`` puts the glyph on a
        muted rounded square and ``'image'`` clips a picture to a rounded square.
    """

    def __init__(self,
                 *,
                 variant: str = 'default',
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(
            variant_classes=option('item media variant', variant, _ITEM_MEDIA_VARIANTS),
            classes=classes,
            **kwargs,
        )
        self._props['data-slot'] = 'item-media'


class ItemContent(ShadcnElement, default_classes=_ITEM_CONTENT_CLASSES):
    """The stretchy column holding an :class:`ItemTitle` and :class:`ItemDescription`."""

    def __init__(self,
                 *,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(classes=classes, **kwargs)
        self._props['data-slot'] = 'item-content'


class ItemTitle(ShadcnElement, TextElement, default_classes=_ITEM_TITLE_CLASSES):
    """The primary line of an :class:`Item`."""

    def __init__(self,
                 text: str = '',
                 *,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(text=text, classes=classes, **kwargs)
        self._props['data-slot'] = 'item-title'


class ItemDescription(ShadcnElement, TextElement, default_classes=_ITEM_DESCRIPTION_CLASSES):
    """The secondary line, clipped to two lines."""

    def __init__(self,
                 text: str = '',
                 *,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(text=text, classes=classes, **kwargs)
        self._props['data-slot'] = 'item-description'


class ItemActions(ShadcnElement, default_classes=_ITEM_ACTIONS_CLASSES):
    """The trailing buttons or controls of an :class:`Item`."""

    def __init__(self,
                 *,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(classes=classes, **kwargs)
        self._props['data-slot'] = 'item-actions'


class ItemHeader(ShadcnElement, default_classes=_ITEM_HEADER_CLASSES):
    """A full-width line above the row's main content."""

    def __init__(self,
                 *,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(classes=classes, **kwargs)
        self._props['data-slot'] = 'item-header'


class ItemFooter(ShadcnElement, default_classes=_ITEM_FOOTER_CLASSES):
    """A full-width line below the row's main content."""

    def __init__(self,
                 *,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(classes=classes, **kwargs)
        self._props['data-slot'] = 'item-footer'


class ItemSeparator(ShadcnElement, default_classes=_ITEM_SEPARATOR_CLASSES):
    """A hairline between two rows of an :class:`ItemGroup`."""

    def __init__(self,
                 *,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(classes=classes, **kwargs)
        self._props['role'] = 'none'
        self._props['data-slot'] = 'item-separator'


def item_group(**kwargs: Any) -> ItemGroup:
    """Create an :class:`ItemGroup`."""
    return ItemGroup(**kwargs)


def item(*, variant: str = 'default', size: str = 'default', **kwargs: Any) -> Item:
    """Create an :class:`Item`."""
    return Item(variant=variant, size=size, **kwargs)


def item_media(*, variant: str = 'default', **kwargs: Any) -> ItemMedia:
    """Create an :class:`ItemMedia`."""
    return ItemMedia(variant=variant, **kwargs)


def item_content(**kwargs: Any) -> ItemContent:
    """Create an :class:`ItemContent`."""
    return ItemContent(**kwargs)


def item_title(text: str = '', **kwargs: Any) -> ItemTitle:
    """Create an :class:`ItemTitle`."""
    return ItemTitle(text, **kwargs)


def item_description(text: str = '', **kwargs: Any) -> ItemDescription:
    """Create an :class:`ItemDescription`."""
    return ItemDescription(text, **kwargs)


def item_actions(**kwargs: Any) -> ItemActions:
    """Create an :class:`ItemActions`."""
    return ItemActions(**kwargs)


def item_header(**kwargs: Any) -> ItemHeader:
    """Create an :class:`ItemHeader`."""
    return ItemHeader(**kwargs)


def item_footer(**kwargs: Any) -> ItemFooter:
    """Create an :class:`ItemFooter`."""
    return ItemFooter(**kwargs)


def item_separator(**kwargs: Any) -> ItemSeparator:
    """Create an :class:`ItemSeparator`."""
    return ItemSeparator(**kwargs)

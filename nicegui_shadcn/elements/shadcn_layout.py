"""Layout primitives: the card family, separators and skeletons.

None of these need any client-side JavaScript — shadcn's card is a handful of
styled ``<div>``s — so they are plain NiceGUI elements with ``default_classes``.
That keeps them cheap: no extra ``.vue`` file is compiled or downloaded.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from nicegui.elements.mixins.text_element import TextElement

from .base import ShadcnElement, option

__all__ = [
    'Card', 'CardContent', 'CardDescription', 'CardFooter', 'CardHeader', 'CardTitle',
    'Separator', 'Skeleton',
    'card', 'card_content', 'card_description', 'card_footer', 'card_header', 'card_title',
    'separator', 'skeleton',
]


class Card(ShadcnElement, default_classes='flex flex-col gap-6 rounded-xl border bg-card py-6 text-card-foreground shadow-sm'):
    """A shadcn/ui card.

    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """

    def __init__(self, *, classes: str | Iterable[str] | None = None, **kwargs: Any) -> None:
        super().__init__(tag='div', classes=classes, **kwargs)


class CardHeader(ShadcnElement, default_classes='grid auto-rows-min items-start gap-1.5 px-6'):
    """The header section of a :class:`Card`.

    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """

    def __init__(self, *, classes: str | Iterable[str] | None = None, **kwargs: Any) -> None:
        super().__init__(tag='div', classes=classes, **kwargs)


class CardTitle(ShadcnElement, TextElement, default_classes='leading-none font-semibold'):
    """The title of a :class:`Card`.

    :param text: the text to display.
    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """

    def __init__(self, text: str = '', *, classes: str | Iterable[str] | None = None, **kwargs: Any) -> None:
        super().__init__(tag='div', text=text, classes=classes, **kwargs)


class CardDescription(ShadcnElement, TextElement, default_classes='text-sm text-muted-foreground'):
    """The description of a :class:`Card`.

    :param text: the text to display.
    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """

    def __init__(self, text: str = '', *, classes: str | Iterable[str] | None = None, **kwargs: Any) -> None:
        super().__init__(tag='div', text=text, classes=classes, **kwargs)


class CardContent(ShadcnElement, default_classes='px-6'):
    """The main content section of a :class:`Card`.

    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """

    def __init__(self, *, classes: str | Iterable[str] | None = None, **kwargs: Any) -> None:
        super().__init__(tag='div', classes=classes, **kwargs)


class CardFooter(ShadcnElement, default_classes='flex items-center px-6'):
    """The footer section of a :class:`Card`.

    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """

    def __init__(self, *, classes: str | Iterable[str] | None = None, **kwargs: Any) -> None:
        super().__init__(tag='div', classes=classes, **kwargs)


_ORIENTATIONS = {
    'horizontal': 'h-px w-full',
    'vertical': 'h-full w-px',
}


class Separator(ShadcnElement, default_classes='shrink-0 bg-border'):
    """A visual divider, horizontal or vertical.

    :param orientation: ``horizontal`` for a full-width rule or ``vertical``
        for a full-height one.
    :param decorative: mark the divider as purely presentational; when
        ``False`` it is exposed to assistive technology with
        ``role="separator"`` and the matching ``aria-orientation``.
    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """

    def __init__(self,
                 *,
                 orientation: str = 'horizontal',
                 decorative: bool = True,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(
            tag='div',
            classes=classes,
            variant_classes=option('orientation', orientation, _ORIENTATIONS),
            **kwargs,
        )
        self._props['role'] = 'none' if decorative else 'separator'
        if not decorative:
            self._props['aria-orientation'] = orientation


class Skeleton(ShadcnElement, default_classes='animate-pulse rounded-md bg-accent'):
    """A placeholder shown while content loads.

    :param width: CSS width, e.g. ``'12rem'`` or ``'100%'``.
    :param height: CSS height, e.g. ``'1rem'``.
    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """

    def __init__(self,
                 *,
                 width: str | None = None,
                 height: str | None = None,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(tag='div', classes=classes, **kwargs)
        if width:
            self.style(f'width: {width}')
        if height:
            self.style(f'height: {height}')


def card(*, classes: str | Iterable[str] | None = None, **kwargs: Any) -> Card:
    """Create a :class:`Card`.

    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """
    return Card(classes=classes, **kwargs)


def card_header(*, classes: str | Iterable[str] | None = None, **kwargs: Any) -> CardHeader:
    """Create a :class:`CardHeader`.

    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """
    return CardHeader(classes=classes, **kwargs)


def card_title(text: str = '', *, classes: str | Iterable[str] | None = None, **kwargs: Any) -> CardTitle:
    """Create a :class:`CardTitle`.

    :param text: the text to display.
    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """
    return CardTitle(text, classes=classes, **kwargs)


def card_description(text: str = '', *, classes: str | Iterable[str] | None = None, **kwargs: Any) -> CardDescription:
    """Create a :class:`CardDescription`.

    :param text: the text to display.
    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """
    return CardDescription(text, classes=classes, **kwargs)


def card_content(*, classes: str | Iterable[str] | None = None, **kwargs: Any) -> CardContent:
    """Create a :class:`CardContent`.

    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """
    return CardContent(classes=classes, **kwargs)


def card_footer(*, classes: str | Iterable[str] | None = None, **kwargs: Any) -> CardFooter:
    """Create a :class:`CardFooter`.

    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """
    return CardFooter(classes=classes, **kwargs)


def separator(*, classes: str | Iterable[str] | None = None, **kwargs: Any) -> Separator:
    """Create a :class:`Separator`.

    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """
    return Separator(classes=classes, **kwargs)


def skeleton(*, classes: str | Iterable[str] | None = None, **kwargs: Any) -> Skeleton:
    """Create a :class:`Skeleton`.

    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """
    return Skeleton(classes=classes, **kwargs)

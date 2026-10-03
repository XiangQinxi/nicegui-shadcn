"""Typography: the class recipes shadcn/ui documents, wrapped as elements.

Upstream ships these as a page of recipes rather than as a component, so each one
here is a plain styled element -- no behaviour, just the right tag and the right
default classes, both of which ``classes=`` can override.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from nicegui.elements.mixins.text_element import TextElement

from .base import ShadcnElement, option

__all__ = [
    'Blockquote', 'BulletList', 'Heading', 'InlineCode', 'Large', 'Lead', 'Muted', 'Paragraph', 'Small',
    'blockquote', 'bullet_list', 'h1', 'h2', 'h3', 'h4', 'heading', 'inline_code', 'large', 'lead',
    'muted', 'paragraph', 'small',
]

_HEADING_VARIANTS = {
    1: 'scroll-m-20 text-4xl font-extrabold tracking-tight text-balance',
    2: 'scroll-m-20 border-b pb-2 text-3xl font-semibold tracking-tight first:mt-0',
    3: 'scroll-m-20 text-2xl font-semibold tracking-tight',
    4: 'scroll-m-20 text-xl font-semibold tracking-tight',
}

_PARAGRAPH_CLASSES = 'leading-7 [&:not(:first-child)]:mt-6'

_LEAD_CLASSES = 'text-muted-foreground text-xl'

_LARGE_CLASSES = 'text-lg font-semibold'

_SMALL_CLASSES = 'text-sm leading-none font-medium'

_MUTED_CLASSES = 'text-muted-foreground text-sm'

_BLOCKQUOTE_CLASSES = 'mt-6 border-l-2 pl-6 italic'

_INLINE_CODE_CLASSES = 'bg-muted relative rounded px-[0.3rem] py-[0.2rem] font-mono text-sm font-semibold'

_BULLET_LIST_CLASSES = 'my-6 ml-6 list-disc [&>li]:mt-2'


class Heading(ShadcnElement, TextElement):
    """A section heading rendered as a real ``<h1>``-``<h4>``.

    :param text: the heading.
    :param level: 1 to 4; each level carries the size and weight shadcn/ui gives it.
        Use ``classes=`` to change the scale, and pick the level by document outline
        rather than by size.
    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """

    def __init__(self,
                 text: str = '',
                 *,
                 level: int = 1,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        valid = sorted(_HEADING_VARIANTS)
        if level not in _HEADING_VARIANTS:
            raise ValueError(f'Unknown heading level {level!r}. Valid options are: {valid}')
        kwargs.setdefault('tag', f'h{level}')
        super().__init__(
            variant_classes=option('heading level', level, _HEADING_VARIANTS),
            text=text,
            classes=classes,
            **kwargs,
        )


class Paragraph(ShadcnElement, TextElement, default_classes=_PARAGRAPH_CLASSES):
    """A body paragraph with the leading and spacing shadcn/ui uses.

    :param text: the text to display.
    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """

    def __init__(self,
                 text: str = '',
                 *,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        kwargs.setdefault('tag', 'p')
        super().__init__(text=text, classes=classes, **kwargs)


class Lead(ShadcnElement, TextElement, default_classes=_LEAD_CLASSES):
    """The larger, muted opening line under a page title.

    :param text: the text to display.
    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """

    def __init__(self,
                 text: str = '',
                 *,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        kwargs.setdefault('tag', 'p')
        super().__init__(text=text, classes=classes, **kwargs)


class Large(ShadcnElement, TextElement, default_classes=_LARGE_CLASSES):
    """Emphasised text, one step below a heading.

    :param text: the text to display.
    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """

    def __init__(self,
                 text: str = '',
                 *,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(text=text, classes=classes, **kwargs)


class Small(ShadcnElement, TextElement, default_classes=_SMALL_CLASSES):
    """Small print, rendered as the semantic ``<small>`` element.

    :param text: the text to display.
    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """

    def __init__(self,
                 text: str = '',
                 *,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        kwargs.setdefault('tag', 'small')
        super().__init__(text=text, classes=classes, **kwargs)


class Muted(ShadcnElement, TextElement, default_classes=_MUTED_CLASSES):
    """Secondary text: captions, hints, timestamps.

    :param text: the text to display.
    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """

    def __init__(self,
                 text: str = '',
                 *,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        kwargs.setdefault('tag', 'p')
        super().__init__(text=text, classes=classes, **kwargs)


class Blockquote(ShadcnElement, TextElement, default_classes=_BLOCKQUOTE_CLASSES):
    """A quotation, set off by a left rule.

    :param text: the text to display.
    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """

    def __init__(self,
                 text: str = '',
                 *,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        kwargs.setdefault('tag', 'blockquote')
        super().__init__(text=text, classes=classes, **kwargs)


class InlineCode(ShadcnElement, TextElement, default_classes=_INLINE_CODE_CLASSES):
    """A code snippet inside a sentence, rendered as ``<code>``.

    :param text: the text to display.
    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """

    def __init__(self,
                 text: str = '',
                 *,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        kwargs.setdefault('tag', 'code')
        super().__init__(text=text, classes=classes, **kwargs)


class BulletList(ShadcnElement, default_classes=_BULLET_LIST_CLASSES):
    """A ``<ul>`` with the shadcn/ui markers and item spacing.

    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """

    def __init__(self,
                 *,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(tag='ul', classes=classes, **kwargs)


def heading(text: str = '', *, level: int = 1, **kwargs: Any) -> Heading:
    """Create a :class:`Heading`.

    :param text: the heading.
    :param level: 1 to 4; each level carries the size and weight shadcn/ui gives it.
    """
    return Heading(text, level=level, **kwargs)


def h1(text: str = '', **kwargs: Any) -> Heading:
    """Create a first-level :class:`Heading`.

    :param text: the heading.
    """
    return Heading(text, level=1, **kwargs)


def h2(text: str = '', **kwargs: Any) -> Heading:
    """Create a second-level :class:`Heading`.

    :param text: the heading.
    """
    return Heading(text, level=2, **kwargs)


def h3(text: str = '', **kwargs: Any) -> Heading:
    """Create a third-level :class:`Heading`.

    :param text: the heading.
    """
    return Heading(text, level=3, **kwargs)


def h4(text: str = '', **kwargs: Any) -> Heading:
    """Create a fourth-level :class:`Heading`.

    :param text: the heading.
    """
    return Heading(text, level=4, **kwargs)


def paragraph(text: str = '', **kwargs: Any) -> Paragraph:
    """Create a :class:`Paragraph`.

    :param text: the text to display.
    """
    return Paragraph(text, **kwargs)


def lead(text: str = '', **kwargs: Any) -> Lead:
    """Create a :class:`Lead`.

    :param text: the text to display.
    """
    return Lead(text, **kwargs)


def large(text: str = '', **kwargs: Any) -> Large:
    """Create a :class:`Large`.

    :param text: the text to display.
    """
    return Large(text, **kwargs)


def small(text: str = '', **kwargs: Any) -> Small:
    """Create a :class:`Small`.

    :param text: the text to display.
    """
    return Small(text, **kwargs)


def muted(text: str = '', **kwargs: Any) -> Muted:
    """Create a :class:`Muted`.

    :param text: the text to display.
    """
    return Muted(text, **kwargs)


def blockquote(text: str = '', **kwargs: Any) -> Blockquote:
    """Create a :class:`Blockquote`.

    :param text: the text to display.
    """
    return Blockquote(text, **kwargs)


def inline_code(text: str = '', **kwargs: Any) -> InlineCode:
    """Create an :class:`InlineCode`.

    :param text: the text to display.
    """
    return InlineCode(text, **kwargs)


def bullet_list(**kwargs: Any) -> BulletList:
    """Create a :class:`BulletList`."""
    return BulletList(**kwargs)

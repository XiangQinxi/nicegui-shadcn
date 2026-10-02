"""Direction: the left-to-right / right-to-left context for a subtree.

Wrapping content in :class:`Direction` sets the HTML ``dir`` attribute, which the
browser then applies to everything below it: text runs, scrollbars, form controls
and every shadcn class that uses a logical property (``ps-*``, ``border-s``,
``start-*``) instead of a physical one. The wrapper itself is laid out with
``display: contents`` so it adds no box of its own.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from .base import ShadcnElement, option

__all__ = ['Direction', 'direction']

_DIRECTION_CLASSES = 'contents'

_DIRECTIONS = {
    'ltr': 'ltr',
    'rtl': 'rtl',
}


class Direction(ShadcnElement, default_classes=_DIRECTION_CLASSES):
    """Sets ``dir`` for everything nested inside it.

    :param direction: ``'ltr'`` or ``'rtl'``.
    :param inline: render a ``<span>`` instead of a ``<div>``; with
        ``display: contents`` the choice only matters for HTML validity, so use
        ``inline=True`` inside a paragraph or a heading.

    The direction is inherited, so the outermost :class:`Direction` on the page is
    usually enough; nest another one only to flip a single region.
    """

    def __init__(self,
                 direction: str = 'ltr',
                 *,
                 inline: bool = False,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        kwargs.setdefault('tag', 'span' if inline else 'div')
        super().__init__(classes=classes, **kwargs)
        self._props['dir'] = option('direction', direction, _DIRECTIONS)

    @property
    def direction(self) -> str:
        """The direction currently applied."""
        return str(self._props['dir'])

    @direction.setter
    def direction(self, value: str) -> None:
        self._props['dir'] = option('direction', value, _DIRECTIONS)
        self.update()


def direction(direction: str = 'ltr', **kwargs: Any) -> Direction:
    """Create a :class:`Direction`."""
    return Direction(direction, **kwargs)

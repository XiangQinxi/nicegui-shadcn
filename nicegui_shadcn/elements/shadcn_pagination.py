"""Pagination: a pager that reports the page the user chose.

The page range is computed in the Vue template so that the ellipsis placeholders
stay correct no matter how the numbers are re-bound from Python.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any

from nicegui.elements.mixins.value_element import ValueElement

from .base import ShadcnElement

__all__ = ['Pagination', 'pagination']


class Pagination(ShadcnElement, ValueElement, component='shadcn_pagination.vue'):
    """A pager with previous/next buttons and ellipsis placeholders.

    :param page: the page to show as current, counting from 1.
    :param total: how many pages there are.
    :param siblings: how many page numbers to keep on each side of the current
        one before the range is collapsed into an ellipsis.
    :param on_change: callback invoked with the value-change event when another
        page is chosen; read ``e.value`` for the new page number.
    """

    def __init__(self,
                 page: int = 1,
                 total: int = 1,
                 *,
                 siblings: int = 1,
                 on_change: Callable[..., Any] | None = None,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(value=int(page), on_value_change=on_change, classes=classes, **kwargs)
        self._props['total'] = int(total)
        self._props['siblings'] = int(siblings)

    def _value_to_model_value(self, value: Any) -> int:
        return int(value)

    @property
    def total(self) -> int:
        """How many pages the pager shows."""
        return int(self._props['total'])

    @total.setter
    def total(self, value: int) -> None:
        self._props['total'] = int(value)
        self.update()


def pagination(page: int = 1, total: int = 1, **kwargs: Any) -> Pagination:
    """Create a :class:`Pagination`."""
    return Pagination(page, total, **kwargs)

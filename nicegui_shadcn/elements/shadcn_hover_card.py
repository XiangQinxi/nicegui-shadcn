"""The hover card: a rich preview that appears while the pointer rests on a trigger.

Unlike the tooltip -- which is a plain text hint -- a hover card holds arbitrary
content, stays open while the pointer is inside it, and can also be opened from
the keyboard by focusing the trigger.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any

from nicegui.elements.mixins.value_element import ValueElement

from .base import ShadcnElement, _Openable

__all__ = [
    'HoverCard', 'HoverCardContent', 'HoverCardTrigger',
    'hover_card', 'hover_card_content', 'hover_card_trigger',
]


class HoverCard(_Openable, ShadcnElement, ValueElement, component='shadcn_hover_card.vue'):
    """A rich preview shown on hover.

    :param value: force the card open (``True``) or closed (``False``). Leave it
        as ``None`` to let the pointer decide.
    :param open_delay: milliseconds to wait before opening.
    :param close_delay: milliseconds to wait before closing once the pointer leaves.
    :param on_change: callback invoked with the value-change event when the open state changes; read ``e.value`` for the new state.
    """

    def __init__(self,
                 value: bool | None = None,
                 *,
                 open_delay: int = 200,
                 close_delay: int = 150,
                 on_change: Callable[..., Any] | None = None,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(value=value, on_value_change=on_change, classes=classes, **kwargs)
        self._props['openDelay'] = int(open_delay)
        self._props['closeDelay'] = int(close_delay)

    def _value_to_model_value(self, value: Any) -> bool | None:
        return None if value is None else bool(value)


class HoverCardTrigger(ShadcnElement, component='shadcn_hover_card_trigger.vue'):
    """The element that opens a :class:`HoverCard` on hover.

    By default the trigger's attributes are handed to whatever single element you
    nest inside it, which is what you want for a link or a button::

        with shadcn.hover_card_trigger():
            shadcn.button('@ada', variant='link')

    Pass ``as_child=False`` to wrap the content in an anchor of our own instead.
    """

    def __init__(self,
                 *,
                 as_child: bool = True,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(classes=classes, **kwargs)
        self._props['asChild'] = bool(as_child)


class HoverCardContent(ShadcnElement, component='shadcn_hover_card_content.vue'):
    """The floating panel of a :class:`HoverCard`.

    :param side: ``'top'``, ``'right'``, ``'bottom'`` or ``'left'``.
    :param align: ``'start'``, ``'center'`` or ``'end'``.
    """

    def __init__(self,
                 *,
                 side: str = 'bottom',
                 align: str = 'center',
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(classes=classes, **kwargs)
        self._props['side'] = side
        self._props['align'] = align


def hover_card(value: bool | None = None, **kwargs: Any) -> HoverCard:
    """Create a :class:`HoverCard`."""
    return HoverCard(value, **kwargs)


def hover_card_trigger(**kwargs: Any) -> HoverCardTrigger:
    """Create a :class:`HoverCardTrigger`."""
    return HoverCardTrigger(**kwargs)


def hover_card_content(**kwargs: Any) -> HoverCardContent:
    """Create a :class:`HoverCardContent`."""
    return HoverCardContent(**kwargs)

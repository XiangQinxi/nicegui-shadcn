"""The drawer: a panel that can be dragged away, typically up from the bottom.

ReKa's drawer keeps the open state on the root and the *geometry* on the
content, and it derives the drag axis from the root's ``swipeDirection``. Both
halves therefore have to agree on the edge, which is why :class:`Drawer` and
:class:`DrawerContent` both take a ``side`` -- keep the two in sync.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from typing import Any

from nicegui.elements.mixins.text_element import TextElement
from nicegui.elements.mixins.value_element import ValueElement

from .base import ShadcnElement, _Openable, option
from .shadcn_button import button_classes as _button_classes

__all__ = [
    'Drawer', 'DrawerContent', 'DrawerFooter', 'DrawerTrigger',
    'drawer', 'drawer_content', 'drawer_footer', 'drawer_trigger',
]

_DRAWER_SIDES = {name: name for name in ('bottom', 'top', 'right', 'left')}


class Drawer(_Openable, ShadcnElement, ValueElement, component='shadcn_drawer.vue'):
    """A draggable panel.

    :param value: whether the drawer starts out open.
    :param side: the edge the drawer comes from: ``'bottom'`` (default),
        ``'top'``, ``'right'`` or ``'left'``. It should match the ``side`` of the
        matching :class:`DrawerContent`, because it also sets the drag axis.
    :param modal: block interaction with the rest of the page while open.
    :param snap_points: optional sequence of heights the drawer can rest at,
        e.g. ``[0.4, 0.9]`` or ``['200px', 1]``.
    :param snap_point: the snap point to start at.
    :param on_change: callback invoked with the value-change event when the open state changes; read ``e.value`` for the new state.
    """

    def __init__(self,
                 value: bool = False,
                 *,
                 side: str = 'bottom',
                 modal: bool = True,
                 snap_points: Sequence[float | str] | None = None,
                 snap_point: float | str | None = None,
                 on_change: Callable[..., Any] | None = None,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(value=bool(value), on_value_change=on_change, classes=classes, **kwargs)
        self._props['swipeDirection'] = option('drawer side', side, _DRAWER_SIDES)
        if not modal:
            self._props['modal'] = False
        if snap_points is not None:
            self._props['snapPoints'] = list(snap_points)
        if snap_point is not None:
            self._props['snapPoint'] = snap_point

    def _value_to_model_value(self, value: Any) -> bool:
        return bool(value)


class DrawerTrigger(ShadcnElement, TextElement, component='shadcn_drawer_trigger.vue',
                    default_classes=_button_classes('outline')):
    """The element that opens a :class:`Drawer` when clicked."""

    def __init__(self,
                 text: str = '',
                 *,
                 as_child: bool = False,
                 on_click: Callable[..., Any] | None = None,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(text=text, classes=classes, **kwargs)
        if as_child:
            self._props['asChild'] = True
        if on_click is not None:
            self.on('click', on_click)


class DrawerContent(ShadcnElement, component='shadcn_drawer_content.vue'):
    """The panel of a :class:`Drawer`.

    :param title: heading text. When omitted the drawer stays accessible but
        visually untitled, so the title is rendered for screen readers only.
    :param description: optional supporting text below the title.
    :param side: which edge the panel hugs. Keep it in sync with the
        :class:`Drawer` it belongs to.
    :param closable: render the small close button in the panel corner.
    """

    def __init__(self,
                 title: str | None = None,
                 *,
                 description: str | None = None,
                 side: str = 'bottom',
                 closable: bool = True,
                 aria_label: str = 'Drawer',
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(classes=classes, **kwargs)
        self._props['title'] = title
        self._props['description'] = description
        self._props['ariaLabel'] = aria_label
        self._props['side'] = option('drawer side', side, _DRAWER_SIDES)
        if not closable:
            self._props['closable'] = False


class DrawerFooter(ShadcnElement, default_classes='mt-auto flex flex-col gap-2'):
    """The action row at the bottom of a :class:`DrawerContent`."""


def drawer(value: bool = False, **kwargs: Any) -> Drawer:
    """Create a :class:`Drawer`."""
    return Drawer(value, **kwargs)


def drawer_trigger(text: str = '', **kwargs: Any) -> DrawerTrigger:
    """Create a :class:`DrawerTrigger`."""
    return DrawerTrigger(text, **kwargs)


def drawer_content(title: str | None = None, **kwargs: Any) -> DrawerContent:
    """Create a :class:`DrawerContent`."""
    return DrawerContent(title, **kwargs)


def drawer_footer(**kwargs: Any) -> DrawerFooter:
    """Create a :class:`DrawerFooter`."""
    return DrawerFooter(**kwargs)

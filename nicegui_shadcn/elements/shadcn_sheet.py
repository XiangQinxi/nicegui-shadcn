"""The sheet: a dialog that slides in from an edge of the viewport.

A sheet shares its root and trigger with :mod:`shadcn_overlay` -- it *is* a
dialog, down to the Reka primitive -- and only swaps the panel geometry, which
is why the root reuses ``shadcn_dialog.vue``. The difference the user sees is
that :class:`SheetContent` always hugs an edge and defaults to ``'right'``
instead of floating in the centre.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any

from nicegui.elements.mixins.text_element import TextElement
from nicegui.elements.mixins.value_element import ValueElement

from .base import ShadcnElement, _Openable, option
from .shadcn_button import button_classes as _button_classes

__all__ = [
    'Sheet', 'SheetContent', 'SheetFooter', 'SheetTrigger',
    'sheet', 'sheet_content', 'sheet_footer', 'sheet_trigger',
]

_SHEET_SIDES = {name: name for name in ('right', 'left', 'top', 'bottom')}


class Sheet(_Openable, ShadcnElement, ValueElement, component='shadcn_dialog.vue'):
    """A panel that slides in from an edge of the viewport.

    :param value: whether the sheet starts out open.
    :param on_change: callback invoked with the value-change event when the open state changes; read ``e.value`` for the new state.
    """

    def __init__(self,
                 value: bool = False,
                 *,
                 on_change: Callable[..., Any] | None = None,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(value=bool(value), on_value_change=on_change, classes=classes, **kwargs)

    def _value_to_model_value(self, value: Any) -> bool:
        return bool(value)


class SheetTrigger(ShadcnElement, TextElement, component='shadcn_dialog_trigger.vue',
                   default_classes=_button_classes('outline')):
    """The element that opens a :class:`Sheet` when clicked."""

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


class SheetContent(ShadcnElement, component='shadcn_sheet_content.vue'):
    """The sliding panel of a :class:`Sheet`.

    :param title: heading text. When omitted the sheet stays accessible but
        visually untitled, so the title is rendered for screen readers only.
    :param description: optional supporting text below the title.
    :param side: which edge to slide in from: ``'right'`` (default), ``'left'``,
        ``'top'`` or ``'bottom'``.
    :param closable: render the small close button in the panel corner.
    """

    def __init__(self,
                 title: str | None = None,
                 *,
                 description: str | None = None,
                 side: str = 'right',
                 closable: bool = True,
                 aria_label: str = 'Sheet',
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(classes=classes, **kwargs)
        self._props['title'] = title
        self._props['description'] = description
        self._props['ariaLabel'] = aria_label
        self._props['side'] = option('sheet side', side, _SHEET_SIDES)
        if not closable:
            self._props['closable'] = False


class SheetFooter(ShadcnElement, default_classes='flex flex-col-reverse gap-2 sm:flex-row sm:justify-end'):
    """The action row at the bottom of a :class:`SheetContent`."""


def sheet(value: bool = False, **kwargs: Any) -> Sheet:
    """Create a :class:`Sheet`."""
    return Sheet(value, **kwargs)


def sheet_trigger(text: str = '', **kwargs: Any) -> SheetTrigger:
    """Create a :class:`SheetTrigger`."""
    return SheetTrigger(text, **kwargs)


def sheet_content(title: str | None = None, **kwargs: Any) -> SheetContent:
    """Create a :class:`SheetContent`."""
    return SheetContent(title, **kwargs)


def sheet_footer(**kwargs: Any) -> SheetFooter:
    """Create a :class:`SheetFooter`."""
    return SheetFooter(**kwargs)

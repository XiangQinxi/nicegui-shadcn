"""Overlays: dialog, popover, tooltip and dropdown menu.

All four share the same shape: a persistent *root* element that holds the open
state, an optional *trigger*, and a *content* element whose markup ends up in a
portal appended to ``<body>`` -- which is why the visible parts style themselves
from the component templates while the caller's ``classes`` are forwarded to the
panel through ``$attrs``.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from typing import Any

from nicegui.elements.mixins.text_element import TextElement
from nicegui.elements.mixins.value_element import ValueElement

from .base import ShadcnElement, _Openable, normalize_options
from .shadcn_button import button_classes as _button_classes

__all__ = [
    'Dialog', 'DialogContent', 'DialogFooter', 'DialogTrigger',
    'DropdownMenu', 'Popover', 'PopoverContent', 'PopoverTrigger', 'Tooltip',
    'dialog', 'dialog_content', 'dialog_footer', 'dialog_trigger',
    'dropdown_menu', 'popover', 'popover_content', 'popover_trigger', 'tooltip',
]


class Dialog(_Openable, ShadcnElement, ValueElement, component='shadcn_dialog.vue'):
    """A modal dialog.

    :param value: whether the dialog starts out open.
    :param on_change: callback invoked with the value-change event when the open state changes; read ``e.value`` for the new state.
        A click on the backdrop or on the close button also lands here, so a
        ``dialog.on('...')``-free way to react to dismissal is ``on_change``.
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


class DialogTrigger(ShadcnElement, TextElement, component='shadcn_dialog_trigger.vue',
                    default_classes=_button_classes('outline')):
    """The element that opens a :class:`Dialog` when clicked."""

    def __init__(self,
                 text: str = '',
                 *,
                 as_child: bool = False,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(text=text, classes=classes, **kwargs)
        if as_child:
            self._props['asChild'] = True


class DialogContent(ShadcnElement, component='shadcn_dialog_content.vue'):
    """The panel of a :class:`Dialog`.

    :param title: heading text. When omitted the dialog stays accessible but
        visually untitled, so the title is rendered for screen readers only.
    :param description: optional supporting text below the title.
    :param side: ``'center'`` (default) or one of ``'top'``, ``'right'``,
        ``'bottom'``, ``'left'`` for an edge sheet.
    :param closable: render the small close button in the top-right corner.
    :param classes: classes for the panel itself, which lives in a portal.
    """

    def __init__(self,
                 title: str | None = None,
                 *,
                 description: str | None = None,
                 side: str = 'center',
                 closable: bool = True,
                 aria_label: str = 'Dialog',
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(classes=classes, **kwargs)
        self._props['title'] = title
        self._props['description'] = description
        self._props['ariaLabel'] = aria_label
        self._props['side'] = side
        if not closable:
            self._props['closable'] = False


class DialogFooter(ShadcnElement, default_classes='flex flex-col-reverse gap-2 sm:flex-row sm:justify-end'):
    """The action row at the bottom of a :class:`DialogContent`."""


class Tooltip(ShadcnElement, component='shadcn_tooltip.vue'):
    """A hover/focus hint attached to whatever elements are nested inside.

    :param text: the hint shown in the bubble.
    :param side: ``'top'``, ``'right'``, ``'bottom'`` or ``'left'``.
    :param delay: milliseconds to wait before showing the hint.
    """

    def __init__(self,
                 text: str,
                 *,
                 side: str = 'top',
                 delay: int = 200,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(classes=classes, **kwargs)
        self._props['text'] = text
        self._props['side'] = side
        self._props['delay'] = delay


class Popover(_Openable, ShadcnElement, ValueElement, component='shadcn_popover.vue'):
    """A floating panel anchored to a trigger.

    :param value: whether the popover starts out open.
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


class PopoverTrigger(ShadcnElement, TextElement, component='shadcn_popover_trigger.vue',
                     default_classes=_button_classes('outline')):
    """The element that opens a :class:`Popover` when clicked."""

    def __init__(self,
                 text: str = '',
                 *,
                 as_child: bool = False,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(text=text, classes=classes, **kwargs)
        if as_child:
            self._props['asChild'] = True


class PopoverContent(ShadcnElement, component='shadcn_popover_content.vue'):
    """The floating panel of a :class:`Popover`.

    :param side: preferred placement relative to the trigger.
    :param align: ``'start'``, ``'center'`` or ``'end'``.
    :param side_offset: gap in pixels between trigger and panel.
    """

    def __init__(self,
                 *,
                 side: str = 'bottom',
                 align: str = 'center',
                 side_offset: int = 4,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(classes=classes, **kwargs)
        self._props['side'] = side
        self._props['align'] = align
        self._props['sideOffset'] = side_offset


class DropdownMenu(ShadcnElement, component='shadcn_dropdown_menu.vue'):
    """A menu of actions, opened by clicking whatever is nested inside.

    The items are data because they are rendered inside a portal::

        shadcn.dropdown_menu(
            [{'value': 'edit', 'label': 'Edit'},
             {'kind': 'separator'},
             {'value': 'delete', 'label': 'Delete', 'variant': 'destructive'}],
            on_select=lambda e: print(e.args),
        )

    :param items: the entries, in any shape
        :func:`nicegui_shadcn.elements.base.normalize_options` accepts. Use
        ``kind='label'``/``kind='separator'`` for non-interactive entries and
        ``variant='destructive'`` to tint an item red.
    :param align: ``'start'``, ``'center'`` or ``'end'``.
    :param on_select: callback invoked with the event when an item is chosen.
    """

    def __init__(self,
                 items: Mapping[str, Any] | Iterable[Any] | None = None,
                 *,
                 align: str = 'start',
                 side_offset: int = 4,
                 on_select: Callable[..., Any] | None = None,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(classes=classes, **kwargs)
        self._props['items'] = normalize_options(items or [])
        self._props['align'] = align
        self._props['sideOffset'] = side_offset
        if on_select is not None:
            self.on('select', on_select)

    def set_items(self, items: Mapping[str, Any] | Iterable[Any]) -> None:
        """Replace the menu entries."""
        self._props['items'] = normalize_options(items)
        self.update()


def dialog(value: bool = False, **kwargs: Any) -> Dialog:
    """Create a :class:`Dialog`."""
    return Dialog(value, **kwargs)


def dialog_trigger(text: str = '', **kwargs: Any) -> DialogTrigger:
    """Create a :class:`DialogTrigger`."""
    return DialogTrigger(text, **kwargs)


def dialog_content(title: str | None = None, **kwargs: Any) -> DialogContent:
    """Create a :class:`DialogContent`."""
    return DialogContent(title, **kwargs)


def dialog_footer(**kwargs: Any) -> DialogFooter:
    """Create a :class:`DialogFooter`."""
    return DialogFooter(**kwargs)


def tooltip(text: str, **kwargs: Any) -> Tooltip:
    """Create a :class:`Tooltip`."""
    return Tooltip(text, **kwargs)


def popover(value: bool = False, **kwargs: Any) -> Popover:
    """Create a :class:`Popover`."""
    return Popover(value, **kwargs)


def popover_trigger(text: str = '', **kwargs: Any) -> PopoverTrigger:
    """Create a :class:`PopoverTrigger`."""
    return PopoverTrigger(text, **kwargs)


def popover_content(**kwargs: Any) -> PopoverContent:
    """Create a :class:`PopoverContent`."""
    return PopoverContent(**kwargs)


def dropdown_menu(items: Mapping[str, Any] | Iterable[Any] | None = None, **kwargs: Any) -> DropdownMenu:
    """Create a :class:`DropdownMenu`."""
    return DropdownMenu(items, **kwargs)

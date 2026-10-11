"""Overlays: dialog, popover, tooltip and dropdown menu.

All four share the same shape: a persistent *root* element that holds the open
state, an optional *trigger*, and a *content* element whose markup ends up in a
portal appended to ``<body>``. The caller's ``classes`` are forwarded to that
panel through ``$attrs``, so the panel's own classes are declared in this module
rather than in the templates: ``tw_merge`` can only resolve a caller's class
against a default it can see, and a literal in the template would be applied by
Vue *after* the merge ran and would therefore always win.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from typing import Any

from nicegui.elements.mixins.text_element import TextElement
from nicegui.elements.mixins.value_element import ValueElement

from .base import ShadcnElement, _ALIGNMENTS, _SIDES, _Openable, normalize_options, option
from .shadcn_button import button_classes as _button_classes

__all__ = [
    'Dialog', 'DialogContent', 'DialogFooter', 'DialogTrigger',
    'DropdownMenu', 'Popover', 'PopoverContent', 'PopoverTrigger', 'Tooltip',
    'dialog', 'dialog_content', 'dialog_footer', 'dialog_trigger',
    'dropdown_menu', 'popover', 'popover_content', 'popover_trigger', 'tooltip',
]

#: The tooltip bubble; the caller's ``classes`` reach it through ``$attrs``.
_TOOLTIP_CLASSES = (
    'z-50 w-fit rounded-md bg-primary px-3 py-1.5 text-xs text-balance text-primary-foreground '
    'data-[state=closed]:animate-out data-[state=closed]:fade-out-0 '
    'data-[state=delayed-open]:animate-in data-[state=delayed-open]:fade-in-0 '
    'data-[state=delayed-open]:zoom-in-95'
)

#: The popover panel; the caller's ``classes`` reach it through ``$attrs``.
_POPOVER_CLASSES = (
    'z-50 w-72 rounded-md border bg-popover p-4 text-popover-foreground shadow-md outline-none '
    'data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:animate-in '
    'data-[state=open]:fade-in-0 data-[state=open]:zoom-in-95'
)


#: The parts shared by every dialog panel; the caller's ``classes`` reach it
#: through ``$attrs`` while the geometry below arrives as ``variant_classes``.
_DIALOG_PANEL_CLASSES = (
    'fixed z-50 flex flex-col gap-4 border bg-background shadow-lg '
    'data-[state=closed]:animate-out data-[state=closed]:fade-out-0 '
    'data-[state=open]:animate-in data-[state=open]:fade-in-0'
)

_DIALOG_PANEL_VARIANTS = {
    'center': 'top-1/2 left-1/2 w-full max-w-[calc(100%-2rem)] -translate-x-1/2 -translate-y-1/2 '
              'rounded-xl p-6 sm:max-w-lg',
    'right': 'inset-y-0 right-0 h-full w-3/4 p-6 sm:max-w-sm '
             'sm:data-[state=closed]:slide-out-to-right sm:data-[state=open]:slide-in-from-right',
    'left': 'inset-y-0 left-0 h-full w-3/4 p-6 sm:max-w-sm '
            'sm:data-[state=closed]:slide-out-to-left sm:data-[state=open]:slide-in-from-left',
    'top': 'inset-x-0 top-0 h-auto p-6 data-[state=closed]:slide-out-to-top '
           'data-[state=open]:slide-in-from-top',
    'bottom': 'inset-x-0 bottom-0 h-auto p-6 data-[state=closed]:slide-out-to-bottom '
              'data-[state=open]:slide-in-from-bottom',
}

_DIALOG_SIDES = {name: name for name in _DIALOG_PANEL_VARIANTS}


class Dialog(_Openable, ShadcnElement, ValueElement, component='shadcn_dialog.vue'):
    """A modal dialog.

    :param value: whether the dialog starts out open.
    :param on_change: callback invoked with the value-change event when the open state changes; read ``e.value`` for the new state.
        A click on the backdrop or on the close button also lands here, so a
        ``dialog.on('...')``-free way to react to dismissal is ``on_change``.
    :param classes: extra utility classes, merged with ``cn()`` semantics.
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
    """The element that opens a :class:`Dialog` when clicked.

    :param text: the text to display.
    :param as_child: render the child element instead of a wrapper.
    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """

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


class DialogContent(ShadcnElement, component='shadcn_dialog_content.vue',
                    default_classes=_DIALOG_PANEL_CLASSES):
    """The panel of a :class:`Dialog`.

    :param title: heading text. When omitted the dialog stays accessible but
        visually untitled, so the title is rendered for screen readers only.
    :param description: optional supporting text below the title.
    :param side: ``'center'`` (default) or one of ``'top'``, ``'right'``,
        ``'bottom'``, ``'left'`` for an edge sheet.
    :param closable: render the small close button in the top-right corner.
    :param aria_label: fallback heading used when ``title`` is empty.
    :param classes: classes for the panel itself, which lives in a portal, merged
        with ``cn()`` semantics -- so ``classes='p-8'`` wins over the panel's own
        ``p-6``. Utilities that do not collide are kept, so a ``sm:``-prefixed
        class such as the panel's ``sm:max-w-lg`` is unaffected by
        ``classes='max-w-2xl'``.
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
        side = option('dialog side', side, _DIALOG_SIDES)
        super().__init__(classes=classes, variant_classes=_DIALOG_PANEL_VARIANTS[side], **kwargs)
        self._props['title'] = title
        self._props['description'] = description
        self._props['ariaLabel'] = aria_label
        self._props['side'] = side
        if not closable:
            self._props['closable'] = False


class DialogFooter(ShadcnElement, default_classes='flex flex-col-reverse gap-2 sm:flex-row sm:justify-end'):
    """The action row at the bottom of a :class:`DialogContent`.

    :param classes: extra utility classes, merged with ``cn()`` semantics.
    :param variant_classes: classes implied by the variant, set by the component itself.
    """


class Tooltip(ShadcnElement, component='shadcn_tooltip.vue', default_classes=_TOOLTIP_CLASSES):
    """A hover/focus hint attached to whatever elements are nested inside.

    :param text: the hint shown in the bubble.
    :param side: ``'top'``, ``'right'``, ``'bottom'`` or ``'left'``.
    :param delay: milliseconds to wait before showing the hint.
    :param classes: extra utility classes for the bubble, merged with ``cn()``
        semantics.
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
        self._props['side'] = option('tooltip side', side, _SIDES)
        self._props['delay'] = delay


class Popover(_Openable, ShadcnElement, ValueElement, component='shadcn_popover.vue'):
    """A floating panel anchored to a trigger.

    :param value: whether the popover starts out open.
    :param on_change: callback invoked with the value-change event when the open state changes; read ``e.value`` for the new state.
    :param classes: extra utility classes, merged with ``cn()`` semantics.
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
    """The element that opens a :class:`Popover` when clicked.

    :param text: the text to display.
    :param as_child: render the child element instead of a wrapper.
    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """

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


class PopoverContent(ShadcnElement, component='shadcn_popover_content.vue', default_classes=_POPOVER_CLASSES):
    """The floating panel of a :class:`Popover`.

    :param side: preferred placement relative to the trigger.
    :param align: ``'start'``, ``'center'`` or ``'end'``.
    :param side_offset: gap in pixels between trigger and panel.
    :param classes: classes for the panel itself, which lives in a portal.
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
        self._props['side'] = option('popover side', side, _SIDES)
        self._props['align'] = option('popover align', align, _ALIGNMENTS)
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
    :param side_offset: gap in pixels between trigger and panel.
    :param on_select: callback invoked with the event when an item is chosen.
    :param classes: extra utility classes, merged with ``cn()`` semantics.
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
        """Replace the menu entries.

        :param items: the new entries, in any shape
            :func:`nicegui_shadcn.elements.base.normalize_options` accepts.
        """
        self._props['items'] = normalize_options(items)
        self.update()


def dialog(value: bool = False, **kwargs: Any) -> Dialog:
    """Create a :class:`Dialog`.

    :param value: whether the dialog starts out open.
    """
    return Dialog(value, **kwargs)


def dialog_trigger(text: str = '', **kwargs: Any) -> DialogTrigger:
    """Create a :class:`DialogTrigger`.

    :param text: the text to display.
    """
    return DialogTrigger(text, **kwargs)


def dialog_content(title: str | None = None, **kwargs: Any) -> DialogContent:
    """Create a :class:`DialogContent`.

    :param title: heading text, rendered for screen readers only when omitted.
    """
    return DialogContent(title, **kwargs)


def dialog_footer(**kwargs: Any) -> DialogFooter:
    """Create a :class:`DialogFooter`."""
    return DialogFooter(**kwargs)


def tooltip(text: str, **kwargs: Any) -> Tooltip:
    """Create a :class:`Tooltip`.

    :param text: the hint shown in the bubble.
    """
    return Tooltip(text, **kwargs)


def popover(value: bool = False, **kwargs: Any) -> Popover:
    """Create a :class:`Popover`.

    :param value: whether the popover starts out open.
    """
    return Popover(value, **kwargs)


def popover_trigger(text: str = '', **kwargs: Any) -> PopoverTrigger:
    """Create a :class:`PopoverTrigger`.

    :param text: the text to display.
    """
    return PopoverTrigger(text, **kwargs)


def popover_content(**kwargs: Any) -> PopoverContent:
    """Create a :class:`PopoverContent`."""
    return PopoverContent(**kwargs)


def dropdown_menu(items: Mapping[str, Any] | Iterable[Any] | None = None, **kwargs: Any) -> DropdownMenu:
    """Create a :class:`DropdownMenu`.

    :param items: the entries, in any shape
        :func:`nicegui_shadcn.elements.base.normalize_options` accepts.
    """
    return DropdownMenu(items, **kwargs)

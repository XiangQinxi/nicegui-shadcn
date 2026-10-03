"""Menus: the context menu, and (later) the menubar and navigation menu.

Every menu in this module is *data driven* for the same reason the dropdown
menu is: the entries are rendered inside a portal, so the caller cannot nest
NiceGUI elements into them -- the item list travels as one prop and each
selection is reported back through an ``on_select`` callback.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from typing import Any

from nicegui.elements.mixins.text_element import TextElement

from .base import ShadcnElement, normalize_options

__all__ = [
    'ContextMenu', 'ContextMenuContent', 'ContextMenuTrigger',
    'context_menu', 'context_menu_content', 'context_menu_trigger',
]


class ContextMenu(ShadcnElement, component='shadcn_context_menu.vue'):
    """A menu opened by right-clicking the trigger inside it.

    This element only carries the shared menu state; the visible parts are the
    :class:`ContextMenuTrigger` and the :class:`ContextMenuContent` nested
    inside it.

    :param classes: extra utility classes, merged with ``cn()`` semantics.
    :param variant_classes: classes implied by the variant, set by the component itself.
    """


class ContextMenuTrigger(ShadcnElement, TextElement, component='shadcn_context_menu_trigger.vue',
                         default_classes='flex h-32 w-64 select-none items-center justify-center rounded-md '
                                         'border border-dashed text-sm text-muted-foreground'):
    """The area whose right-click opens the menu.

    :param text: label rendered inside the area. Nest elements instead when the
        area needs more than text.
    :param as_child: forward the trigger's attributes to the nested element
        rather than rendering a wrapper around it.
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


class ContextMenuContent(ShadcnElement, component='shadcn_context_menu_content.vue'):
    """The item list of a :class:`ContextMenu`.

    :param items: the entries, in any shape
        :func:`nicegui_shadcn.elements.base.normalize_options` accepts. Use
        ``kind='label'``/``kind='separator'`` for non-interactive entries and
        ``variant='destructive'`` to tint an item red.
    :param on_select: callback invoked with the event when an item is chosen.
    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """

    def __init__(self,
                 items: Mapping[str, Any] | Iterable[Any] | None = None,
                 *,
                 on_select: Callable[..., Any] | None = None,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(classes=classes, **kwargs)
        self._props['items'] = normalize_options(items or [])
        if on_select is not None:
            self.on('select', on_select)

    def set_items(self, items: Mapping[str, Any] | Iterable[Any]) -> None:
        """Replace the menu entries.

        :param items: the new entries, in any shape
            :func:`nicegui_shadcn.elements.base.normalize_options` accepts.
        """
        self._props['items'] = normalize_options(items)
        self.update()


def context_menu(**kwargs: Any) -> ContextMenu:
    """Create a :class:`ContextMenu`."""
    return ContextMenu(**kwargs)


def context_menu_trigger(text: str = '', **kwargs: Any) -> ContextMenuTrigger:
    """Create a :class:`ContextMenuTrigger`.

    :param text: label rendered inside the area.
    """
    return ContextMenuTrigger(text, **kwargs)


def context_menu_content(items: Mapping[str, Any] | Iterable[Any] | None = None, **kwargs: Any) -> ContextMenuContent:
    """Create a :class:`ContextMenuContent`.

    :param items: the entries, in any shape
        :func:`nicegui_shadcn.elements.base.normalize_options` accepts. Use
        ``kind='label'``/``kind='separator'`` for non-interactive entries and
        ``variant='destructive'`` to tint an item red.
    """
    return ContextMenuContent(items, **kwargs)

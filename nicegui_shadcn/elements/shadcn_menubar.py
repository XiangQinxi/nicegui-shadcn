"""Menubar: the horizontal application menu bar.

The bar is *data driven* like the other menus of this library: the triggers are
rendered inline, but every open menu lives in a portal, so the entries travel as
one prop and each selection is reported back through ``on_select``::

    from nicegui import ui
    from nicegui_shadcn import shadcn

    shadcn.menubar(
        {'File': [{'value': 'new', 'label': 'New'},
                  {'kind': 'separator'},
                  {'kind': 'label', 'label': 'Recent'}],
         'Edit': [{'value': 'undo', 'label': 'Undo', 'disabled': True}]},
        on_select=lambda e: ui.notify(e.args),
    )
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from typing import Any

from .base import ShadcnElement, normalize_options

__all__ = ['Menubar', 'menubar']

_MENUBAR_CLASSES = 'flex h-9 items-center gap-1 rounded-md border bg-background p-1 shadow-sm'


def _normalize_menus(menus: Mapping[str, Any] | Iterable[Any]) -> list[dict[str, Any]]:
    """Coerce the menu descriptions into the plain shape the template expects.

    A mapping is read as ``label -> items``; an iterable yields one mapping per
    menu (``{'label': ..., 'items': [...]}``, or a bare string for an empty
    menu). The entries of every ``items`` list go through
    :func:`normalize_options`, so they accept exactly the same shapes.
    """
    if isinstance(menus, Mapping):
        entries: Iterable[Any] = [{'label': label, 'items': items} for label, items in menus.items()]
    else:
        entries = menus

    result: list[dict[str, Any]] = []
    for index, entry in enumerate(entries):
        menu: Any = {'label': entry} if isinstance(entry, str) else entry
        result.append({
            'value': str(menu.get('value') or f'menu-{index}'),
            'label': str(menu.get('label', '')),
            'items': normalize_options(menu.get('items') or []),
        })
    return result


class Menubar(ShadcnElement, component='shadcn_menubar.vue', default_classes=_MENUBAR_CLASSES):
    """A horizontal bar of menu triggers, each opening its own menu.

    :param menus: a mapping of ``label -> items`` or an iterable of
        ``{'label': ..., 'items': [...]}`` mappings. The nested ``items`` accept
        everything :func:`nicegui_shadcn.elements.base.normalize_options`
        accepts -- including ``kind='label'``/``kind='separator'`` for
        non-interactive entries and ``variant='destructive'`` to tint an item
        red.
    :param align: ``'start'``, ``'center'`` or ``'end'``.
    :param side_offset: gap in pixels between trigger and panel.
    :param on_select: callback invoked with the event when an item is chosen.
        The chosen value is ``e.args`` (the template emits it as the single
        argument of the event).
    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """

    def __init__(self,
                 menus: Mapping[str, Any] | Iterable[Any] | None = None,
                 *,
                 align: str = 'start',
                 side_offset: int = 8,
                 on_select: Callable[..., Any] | None = None,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(classes=classes, **kwargs)
        self._props['menus'] = _normalize_menus(menus or [])
        self._props['align'] = align
        self._props['sideOffset'] = side_offset
        if on_select is not None:
            self.on('select', on_select)

    def set_menus(self, menus: Mapping[str, Any] | Iterable[Any]) -> None:
        """Replace every menu of the bar.

        :param menus: the new menus, in any of the shapes the constructor's
            ``menus`` accepts.
        """
        self._props['menus'] = _normalize_menus(menus)


def menubar(menus: Mapping[str, Any] | Iterable[Any] | None = None, **kwargs: Any) -> Menubar:
    """Create a horizontal menu bar. See :class:`Menubar`.

    :param menus: a mapping of ``label -> items`` or an iterable of
        ``{'label': ..., 'items': [...]}`` mappings.
    """
    return Menubar(menus, **kwargs)

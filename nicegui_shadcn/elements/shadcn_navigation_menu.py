"""shadcn/ui Navigation Menu — a horizontal navigation bar with hover/focus panels.

The menu is data driven, like :class:`~nicegui_shadcn.elements.shadcn_overlay.DropdownMenu`.
Each entry is either a plain link (``href``) or a trigger that opens a panel of
child links (``items``)::

    from nicegui import ui
    from nicegui_shadcn import shadcn

    shadcn.navigation_menu(
        [
            {'label': 'Home', 'href': '/'},
            {
                'label': 'Products',
                'items': [
                    {'label': 'Analytics', 'href': '/analytics',
                     'description': 'Track your metrics end to end.'},
                    {'label': 'Reports', 'href': '/reports'},
                ],
            },
        ],
        on_select=lambda e: ui.notify(f'Clicked {e.args}'),
    )

Every click on a link emits ``select`` with that entry's ``value``, which
defaults to its ``label``.
"""

from __future__ import annotations

from typing import Any, Callable, Iterable, Mapping

from .base import ShadcnElement, normalize_options

__all__ = ['NavigationMenu', 'navigation_menu']

_NAVIGATION_MENU_CLASSES = (
    'relative flex max-w-max flex-1 items-center justify-center text-sm font-medium'
)


def _leaf_options(items: Iterable[Any] | Mapping[Any, Any]) -> list[dict[str, Any]]:
    """Normalize a panel's child links, keeping the extra navigation fields.

    :func:`~nicegui_shadcn.elements.base.normalize_options` resolves ``value`` and
    ``label`` with the same rules the dropdown menu uses, but it only carries the
    menu-item fields; a navigation link additionally needs ``href`` (and reads
    better with a ``description``), so those are folded back in from the source
    mapping at the matching index.
    """
    if isinstance(items, Mapping):
        items = [{'label': key, 'href': value} for key, value in items.items()]
    children = list(items)
    options = normalize_options(children)
    for option, child in zip(options, children):
        extra = child if isinstance(child, Mapping) else {}
        option['href'] = '' if extra.get('href') is None else str(extra['href'])
        option['description'] = str(extra.get('description', ''))
        option['active'] = bool(extra.get('active', False))
    return options


def _normalize_items(items: Iterable[Any] | Mapping[Any, Any]) -> list[dict[str, Any]]:
    """Turn the public ``items`` vocabulary into the structure the template expects.

    A mapping is turned into ``[{'label': key, 'href': value}]`` entries (the shape
    ``shadcn.navigation_menu({'Home': '/', 'Docs': '/docs'})`` implies); a sequence
    is accepted item by item.  Each item needs ``label`` and either ``href`` (a leaf
    link) or ``items`` (a trigger with a panel).
    """
    if isinstance(items, Mapping):
        items = [{'label': key, 'href': value} for key, value in items.items()]

    normalized: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, Mapping):
            raise ValueError(f'Invalid navigation menu item {item!r}. Expected a mapping.')
        children = item.get('items')
        href = item.get('href')
        label = item.get('label', href)
        if label is None:
            raise ValueError(f'Invalid navigation menu item {item!r}. Expected a "label".')
        if href is None and not children:
            raise ValueError(
                f'Invalid navigation menu item {item!r}. Expected an "href" or a non-empty "items" list.'
            )
        entry: dict[str, Any] = {
            'label': str(label),
            'value': str(item.get('value', label)),
            'description': str(item.get('description', '')),
            'disabled': bool(item.get('disabled', False)),
            'active': bool(item.get('active', False)),
            'href': '' if href is None else str(href),
            'items': _leaf_options(children) if children else [],
        }
        normalized.append(entry)
    return normalized


class NavigationMenu(ShadcnElement, component='shadcn_navigation_menu.vue',
                     default_classes=_NAVIGATION_MENU_CLASSES):
    """A horizontal navigation bar whose entries either link out or open a panel.

    :param items: sequence of mappings with ``label`` plus either ``href`` (a leaf
        link) or ``items`` (a list of ``{'label', 'href'}`` child links).  Panel
        children also accept ``description``.
    :param value: value of the entry whose panel should be open on first render.
    :param on_select: handler called with the clicked entry's value whenever a
        link is activated.
    :param classes: extra Tailwind classes for the root element.
    """

    def __init__(
        self,
        items: Iterable[Any] | Mapping[Any, Any] | None = None,
        *,
        value: str | None = None,
        on_select: Callable[..., Any] | None = None,
        classes: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(classes=classes, **kwargs)
        self._props['items'] = _normalize_items(items or [])
        if value is not None:
            self._props['modelValue'] = str(value)
        if on_select is not None:
            self.on('select', on_select)

    def set_items(self, items: Iterable[Any] | Mapping[Any, Any]) -> None:
        """Replace the entries and re-render the menu.

        :param items: the new entries, in the same vocabulary as ``__init__``.
        """
        self._props['items'] = _normalize_items(items)
        self.update()


def navigation_menu(items: Iterable[Any] | Mapping[Any, Any] | None = None,
                    **kwargs: Any) -> NavigationMenu:
    """Create a :class:`NavigationMenu`.

    :param items: the entries to render (see :class:`NavigationMenu`).
    :param kwargs: forwarded to :class:`NavigationMenu`.
    """
    return NavigationMenu(items, **kwargs)

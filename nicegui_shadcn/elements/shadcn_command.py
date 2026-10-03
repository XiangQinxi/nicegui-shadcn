"""A command palette: a searchable, grouped list of actions.

.. code-block:: python

   shadcn.command(
       [
           {'value': 'calendar', 'label': 'Calendar', 'group': 'Suggestions', 'shortcut': '⌘C'},
           {'value': 'emoji', 'label': 'Emoji', 'group': 'Suggestions'},
           {'kind': 'separator'},
           {'value': 'profile', 'label': 'Profile', 'group': 'Settings', 'shortcut': '⌘P'},
       ],
       on_select=lambda e: ui.notify(e.args),
   )

The items are filtered in the browser as the user types, so no server round-trip is
needed per keystroke. Pass ``filter=False`` to filter on the server instead and
listen to ``on_search``.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from typing import Any

from nicegui.elements.mixins.value_element import ValueElement

from .base import ShadcnElement

__all__ = ['Command', 'command']

_COMMAND_CLASSES = (
    'flex h-full w-full flex-col overflow-hidden rounded-md border bg-popover text-popover-foreground'
)


def _normalize_commands(items: Mapping[str, Any] | Iterable[Any] | None) -> list[dict[str, Any]]:
    """Normalise the commands into the JSON-safe shape the Vue component expects.

    Accepts a mapping ``{value: label}``, a sequence of strings, a sequence of
    ``(value, label)`` pairs, or a sequence of mappings.
    """
    if items is None:
        return []
    if isinstance(items, Mapping):
        return [
            {'value': str(value), 'label': str(label), 'kind': 'item', 'disabled': False, 'keywords': []}
            for value, label in items.items()
        ]
    commands: list[dict[str, Any]] = []
    for item in items:
        if isinstance(item, str):
            commands.append({'value': item, 'label': item, 'kind': 'item', 'disabled': False, 'keywords': []})
            continue
        if isinstance(item, Mapping):
            value = str(item.get('value', item.get('label', '')))
            keywords = item.get('keywords') or []
            if isinstance(keywords, str):
                keywords = [keywords]
            command: dict[str, Any] = {
                'value': value,
                'label': str(item.get('label', value)),
                'kind': str(item.get('kind', 'item')),
                'disabled': bool(item.get('disabled', False)),
                'keywords': [str(word).lower() for word in keywords],
            }
            for key in ('group', 'shortcut'):
                if item.get(key) is not None:
                    command[key] = str(item[key])
            commands.append(command)
            continue
        try:
            value, label = item
        except (TypeError, ValueError):
            raise ValueError(
                f'Command item {item!r} is not a (value, label) pair, a string or a mapping. '
                'Expected a string, a (value, label) pair, or a mapping with a "value" key.'
            ) from None
        commands.append(
            {'value': str(value), 'label': str(label), 'kind': 'item', 'disabled': False, 'keywords': []}
        )
    return commands


class Command(ShadcnElement, ValueElement, component='shadcn_command.vue', default_classes=_COMMAND_CLASSES):
    """A command palette: a searchable, grouped list of actions.

    :param items: the commands, as a mapping ``{value: label}``, a sequence of strings,
        a sequence of ``(value, label)`` pairs, or a sequence of mappings with the keys
        ``value``, ``label``, ``group``, ``keywords``, ``shortcut``, ``disabled`` and
        ``kind`` (``'item'`` or ``'separator'``).
    :param value: the initially highlighted value.
    :param placeholder: placeholder of the search field.
    :param empty_text: text shown when the search matches nothing.
    :param filter: filter the items in the browser while typing; set this to ``False``
        to filter on the server and use ``on_search`` instead.
    :param autofocus: focus the search field as soon as the element is created.
    :param aria_label: accessible name of the search field and of the result list.
    :param on_change: callback invoked with the newly selected value.
    :param on_select: callback invoked when a command is chosen.
    :param on_search: callback invoked with the current query while the user types.
    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """

    LOOPBACK = False

    def __init__(
        self,
        items: Mapping[str, Any] | Iterable[Any] | None = None,
        *,
        value: str | None = None,
        placeholder: str = 'Type a command or search...',
        empty_text: str = 'No results found.',
        filter: bool = True,  # noqa: A002 - the name matches the Vue prop, as elsewhere in this package
        autofocus: bool = False,
        aria_label: str = 'Command menu',
        on_change: Callable[..., Any] | None = None,
        on_select: Callable[..., Any] | None = None,
        on_search: Callable[..., Any] | None = None,
        classes: str | Iterable[str] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(value=value, on_value_change=on_change, classes=classes, **kwargs)
        self._props['items'] = _normalize_commands(items)
        self._props['placeholder'] = placeholder
        self._props['empty-text'] = empty_text
        self._props['filter'] = bool(filter)
        self._props['autofocus'] = bool(autofocus)
        self._props['aria-label'] = aria_label
        if on_select is not None:
            self.on('select', on_select)
        if on_search is not None:
            self.on('search', lambda e: on_search(e.args))

    def _value_to_model_value(self, value: Any) -> str:
        return '' if value is None else str(value)

    def set_items(self, items: Mapping[str, Any] | Iterable[Any] | None) -> None:
        """Replace the commands.

        :param items: the new commands, in any of the shapes the constructor's
            ``items`` accepts.
        """
        self._props['items'] = _normalize_commands(items)
        self.update()


def command(
    items: Mapping[str, Any] | Iterable[Any] | None = None,
    **kwargs: Any,
) -> Command:
    """Create a :class:`Command`.

    :param items: the commands, in any of the shapes accepted by :class:`Command`:
        a mapping ``{value: label}``, a sequence of strings, a sequence of
        ``(value, label)`` pairs, or a sequence of mappings.
    """
    return Command(items, **kwargs)

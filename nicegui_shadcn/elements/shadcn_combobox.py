"""An autocomplete input combining a trigger button with a searchable option list.

```python
shadcn.combobox(
    ['Next.js', 'SvelteKit', 'Nuxt.js', 'Remix', 'Astro'],
    placeholder='Select framework...',
    on_change=lambda e: ui.notify(e.value),
)
```

The options are filtered in the browser as the user types, so no server round-trip is
needed per keystroke.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from typing import Any

from nicegui.elements.mixins.value_element import ValueElement

from .base import ShadcnElement, normalize_options

__all__ = ['Combobox', 'combobox']

_COMBOBOX_CLASSES = 'relative w-[200px]'


class Combobox(ShadcnElement, ValueElement, component='shadcn_combobox.vue', default_classes=_COMBOBOX_CLASSES):
    """A searchable single-select input.

    :param options: the options, as a mapping ``{value: label}``, a sequence of strings,
        a sequence of ``(value, label)`` pairs, or a sequence of mappings with the keys
        ``value``, ``label`` and ``disabled``.
    :param value: the initially selected value.
    :param placeholder: text shown while nothing is selected.
    :param search_placeholder: placeholder of the search field inside the panel.
    :param empty_text: text shown when the search matches nothing.
    :param filter: filter the options in the browser while typing.
    :param on_change: callback invoked with the newly selected value.
    :param on_select: callback invoked when an option is chosen.
    """

    LOOPBACK = False

    def __init__(
        self,
        options: Mapping[str, Any] | Iterable[Any] | None = None,
        *,
        value: str | None = None,
        placeholder: str = 'Select an option...',
        search_placeholder: str = 'Search...',
        empty_text: str = 'No results found.',
        filter: bool = True,  # noqa: A002 - the name matches the Vue prop, as elsewhere in this package
        aria_label: str = 'Combobox',
        on_change: Callable[..., Any] | None = None,
        on_select: Callable[..., Any] | None = None,
        classes: str | Iterable[str] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(value=value, on_value_change=on_change, classes=classes, **kwargs)
        self._props['options'] = normalize_options(options or [])
        self._props['placeholder'] = placeholder
        self._props['search-placeholder'] = search_placeholder
        self._props['empty-text'] = empty_text
        self._props['filter'] = bool(filter)
        self._props['aria-label'] = aria_label
        if on_select is not None:
            self.on('select', on_select)

    def _value_to_model_value(self, value: Any) -> str:
        return '' if value is None else str(value)

    def set_options(self, options: Mapping[str, Any] | Iterable[Any] | None) -> None:
        """Replace the options."""
        self._props['options'] = normalize_options(options or [])
        self.update()


def combobox(
    options: Mapping[str, Any] | Iterable[Any] | None = None,
    **kwargs: Any,
) -> Combobox:
    """Create a :class:`Combobox`."""
    return Combobox(options, **kwargs)

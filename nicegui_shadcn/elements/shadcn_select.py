"""``shadcn.select`` — a listbox built on reka-ui's select primitives.

The options are data, not children: a select's menu lives in a portal and is
entirely generated, so there is nothing for the caller to nest. Pass a mapping,
a list of strings, or a list of ``{'value', 'label', 'disabled'}`` mappings::

    shadcn.select({'light': 'Light', 'dark': 'Dark'}, value='light',
                  on_change=lambda e: print(e.value))
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from typing import Any

from nicegui.elements.mixins.value_element import ValueElement

from .base import ShadcnElement, normalize_options

__all__ = ['Select', 'select']


class Select(ShadcnElement, ValueElement, component='shadcn_select.vue'):
    """A dropdown list of options.

    :param options: the choices, in any of the shapes
        :func:`nicegui_shadcn.elements.base.normalize_options` accepts.
    :param value: the initially selected value.
    :param placeholder: text shown while nothing is selected.
    :param disabled: render the control disabled.
    :param on_change: callback invoked with the new value when the selection changes.
    """

    def __init__(self,
                 options: Mapping[str, Any] | Iterable[Any] | None = None,
                 *,
                 value: str | None = None,
                 placeholder: str = 'Select an option',
                 disabled: bool = False,
                 on_change: Callable[..., Any] | None = None,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(value=value, on_value_change=on_change, classes=classes, **kwargs)
        self._props['options'] = normalize_options(options or [])
        self._props['placeholder'] = placeholder
        if disabled:
            self._props['disabled'] = True

    def _value_to_model_value(self, value: Any) -> str:
        # reka-ui shows the placeholder for `undefined`, and `''` is simply not a
        # valid item value, so both mean "nothing selected".
        return '' if value is None else str(value)

    def set_options(self, options: Mapping[str, Any] | Iterable[Any]) -> None:
        """Replace the list of choices."""
        self._props['options'] = normalize_options(options)
        self.update()


def select(options: Mapping[str, Any] | Iterable[Any] | None = None, **kwargs: Any) -> Select:
    """Create a :class:`Select`."""
    return Select(options, **kwargs)

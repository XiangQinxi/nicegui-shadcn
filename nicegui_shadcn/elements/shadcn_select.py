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

# The trigger's classes live here rather than in the template: the caller's ``classes``
# reach that button through ``$attrs``, and a literal class list in the template is
# merged by Vue *after* ``tw_merge`` ran, so it would always win. Keeping the list in
# Python lets ``tw_merge`` resolve it against ``classes='h-12'`` and friends.
_SELECT_TRIGGER_CLASSES = (
    'flex h-9 w-full items-center justify-between gap-2 rounded-md border border-input '
    'bg-transparent px-3 py-2 text-sm whitespace-nowrap shadow-xs outline-none '
    'transition-[color,box-shadow] focus-visible:border-ring focus-visible:ring-[3px] '
    'focus-visible:ring-ring/50 disabled:cursor-not-allowed disabled:opacity-50 '
    'dark:bg-input/30 dark:hover:bg-input/50'
)


class Select(ShadcnElement, ValueElement, component='shadcn_select.vue',
             default_classes=_SELECT_TRIGGER_CLASSES):
    """A dropdown list of options.

    :param options: the choices, in any of the shapes
        :func:`nicegui_shadcn.elements.base.normalize_options` accepts.
    :param value: the initially selected value.
    :param placeholder: text shown while nothing is selected.
    :param disabled: render the control disabled.
    :param on_change: callback invoked with the value-change event when the selection
        changes; read ``e.value`` for the new value.
    :param classes: extra utility classes for the trigger button, merged with ``cn()``
        semantics.
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
        self._props['disabled'] = bool(disabled)

    def _value_to_model_value(self, value: Any) -> str:
        # reka-ui shows the placeholder for `undefined`, and `''` is simply not a
        # valid item value, so both mean "nothing selected".
        return '' if value is None else str(value)

    @property
    def disabled(self) -> bool:
        """Whether the control can be changed."""
        return bool(self._props['disabled'])

    @disabled.setter
    def disabled(self, value: bool) -> None:
        self._props['disabled'] = bool(value)
        self.update()

    def set_options(self, options: Mapping[str, Any] | Iterable[Any]) -> None:
        """Replace the list of choices.

        :param options: the new choices, in any of the shapes
            :func:`nicegui_shadcn.elements.base.normalize_options` accepts.
        """
        self._props['options'] = normalize_options(options)
        self.update()


def select(options: Mapping[str, Any] | Iterable[Any] | None = None, **kwargs: Any) -> Select:
    """Create a :class:`Select`.

    :param options: the choices to offer.
    """
    return Select(options, **kwargs)

"""Native select: the platform ``<select>`` wearing the shadcn styles.

A native control is the right answer inside a ``<form>``, on touch devices and
whenever the browser's own picker is better than a custom popup. Use
:class:`nicegui_shadcn.shadcn.Select` (``shadcn.select``) when you want the
styled reka-ui listbox instead.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from typing import Any

from nicegui.elements.mixins.value_element import ValueElement

from .base import ShadcnElement, normalize_options

__all__ = ['NativeSelect', 'native_select']

# The wrapper's layout classes live here rather than in the template so that ``tw_merge`` can
# resolve them against a caller's ``classes='w-full'``. A literal ``w-fit`` in the template is
# invisible to the merge and would therefore always win.
_NATIVE_SELECT_CLASSES = 'relative w-fit has-[select:disabled]:opacity-50'


class NativeSelect(ShadcnElement, ValueElement, component='shadcn_native_select.vue',
                   default_classes=_NATIVE_SELECT_CLASSES):
    """A styled ``<select>`` built from the browser's own dropdown.

    :param options: mapping, sequence of labels, or sequence of ``(value, label)``
        pairs -- the same shapes :func:`nicegui_shadcn.shadcn.select` accepts.
    :param value: the initially selected value.
    :param disabled: whether the control can be changed.
    :param on_change: callback invoked with the value-change event when another
        entry is picked; read ``e.value`` for the new value.
    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """

    def __init__(self,
                 options: Mapping[str, str] | Iterable[Any] | None = None,
                 *,
                 value: Any = '',
                 disabled: bool = False,
                 on_change: Callable[..., Any] | None = None,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(value=value, on_value_change=on_change, classes=classes, **kwargs)
        self._props['items'] = normalize_options(options or [])
        self._props['disabled'] = bool(disabled)

    def _value_to_model_value(self, value: Any) -> str:
        return '' if value is None else str(value)

    @property
    def disabled(self) -> bool:
        """Whether the control can be changed."""
        return bool(self._props['disabled'])

    @disabled.setter
    def disabled(self, value: bool) -> None:
        self._props['disabled'] = bool(value)
        self.update()

    def set_options(self, options: Mapping[str, str] | Iterable[Any] | None) -> None:
        """Replace the available entries.

        :param options: the new options, in any of the shapes the constructor's
            ``options`` accepts.
        """
        self._props['items'] = normalize_options(options or [])
        self.update()


def native_select(options: Mapping[str, str] | Iterable[Any] | None = None, **kwargs: Any) -> NativeSelect:
    """Create a :class:`NativeSelect`.

    :param options: the choices to offer.
    """
    return NativeSelect(options, **kwargs)

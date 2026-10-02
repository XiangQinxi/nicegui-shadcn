"""The remaining reka-ui backed form controls.

These all render their options from Python data rather than from nested
elements, because their menus/indicators live inside ports of the DOM that
NiceGUI children cannot be placed into.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from typing import Any

from nicegui.elements.mixins.text_element import TextElement
from nicegui.elements.mixins.value_element import ValueElement

from .base import ShadcnElement, normalize_options

__all__ = [
    'RadioGroup', 'Slider', 'Toggle', 'ToggleGroup',
    'radio_group', 'slider', 'toggle', 'toggle_group',
]

_RADIO_GROUP_CLASSES = 'grid gap-3'

_SLIDER_CLASSES = 'relative flex w-full touch-none items-center select-none'

_TOGGLE_CLASSES = (
    'inline-flex h-9 min-w-9 items-center justify-center gap-2 rounded-md px-2 text-sm font-medium '
    'whitespace-nowrap outline-none transition-[color,box-shadow] '
    'hover:bg-muted hover:text-muted-foreground '
    'focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50 '
    'disabled:pointer-events-none disabled:opacity-50 '
    'data-[state=on]:bg-accent data-[state=on]:text-accent-foreground '
    '[&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0'
)

_TOGGLE_GROUP_CLASSES = 'flex w-fit items-center gap-1 rounded-md'


class RadioGroup(ShadcnElement, ValueElement, component='shadcn_radio_group.vue', default_classes=_RADIO_GROUP_CLASSES):
    """A radio group whose choices are declared as data.

    :param options: the choices, in any of the shapes
        :func:`nicegui_shadcn.elements.base.normalize_options` accepts.
    :param value: the initially selected value.
    :param on_change: callback invoked with the new value when the selection changes.
    """

    def __init__(self,
                 options: Mapping[str, Any] | Iterable[Any] | None = None,
                 *,
                 value: str | None = None,
                 orientation: str = 'vertical',
                 disabled: bool = False,
                 on_change: Callable[..., Any] | None = None,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(value=value, on_value_change=on_change, classes=classes, **kwargs)
        self._props['options'] = normalize_options(options or [])
        self._props['orientation'] = orientation
        if disabled:
            self._props['disabled'] = True

    def _value_to_model_value(self, value: Any) -> str:
        return '' if value is None else str(value)


class Slider(ShadcnElement, ValueElement, component='shadcn_slider.vue', default_classes=_SLIDER_CLASSES):
    """A single-thumb range slider.

    :param value: the initial value.
    :param min: lower bound.
    :param max: upper bound.
    :param step: increment between selectable values.
    :param on_change: callback invoked with the new value while the thumb moves.
    """

    def __init__(self,
                 value: float = 0,
                 *,
                 min: float = 0,  # noqa: A002 - mirrors shadcn/the DOM
                 max: float = 100,  # noqa: A002 - mirrors shadcn/the DOM
                 step: float = 1,
                 orientation: str = 'horizontal',
                 disabled: bool = False,
                 on_change: Callable[..., Any] | None = None,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(value=value, on_value_change=on_change, classes=classes, **kwargs)
        self._props['min'] = min
        self._props['max'] = max
        self._props['step'] = step
        self._props['orientation'] = orientation
        if disabled:
            self._props['disabled'] = True

    def _value_to_model_value(self, value: Any) -> float:
        return 0.0 if value is None else float(value)

    def _value_to_event_value(self, value: Any) -> float:
        return float(value)


class Toggle(ShadcnElement, ValueElement, component='shadcn_toggle.vue', default_classes=_TOGGLE_CLASSES):
    """A two-state button, like a switch the user has to press and release."""

    def __init__(self,
                 text: str = '',
                 *,
                 value: bool = False,
                 disabled: bool = False,
                 on_change: Callable[..., Any] | None = None,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(value=bool(value), on_value_change=on_change, classes=classes, **kwargs)
        if disabled:
            self._props['disabled'] = True
        if text:
            self._props['label'] = text
            with self:
                from .base import Text  # local import keeps the module import graph flat
                self._label = Text(text)

    def _value_to_model_value(self, value: Any) -> bool:
        return bool(value)

    def _value_to_event_value(self, value: Any) -> bool:
        return bool(value)


class ToggleGroup(ShadcnElement, ValueElement, component='shadcn_toggle_group.vue', default_classes=_TOGGLE_GROUP_CLASSES):
    """A segmented control.

    :param options: the segments, in any of the shapes
        :func:`nicegui_shadcn.elements.base.normalize_options` accepts.
    :param multiple: allow several segments to be pressed at once.
    """

    def __init__(self,
                 options: Mapping[str, Any] | Iterable[Any] | None = None,
                 *,
                 value: str | Iterable[str] | None = None,
                 multiple: bool = False,
                 orientation: str = 'horizontal',
                 disabled: bool = False,
                 on_change: Callable[..., Any] | None = None,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(value=value, on_value_change=on_change, classes=classes, **kwargs)
        self._props['options'] = normalize_options(options or [])
        self._props['type'] = 'multiple' if multiple else 'single'
        self._props['orientation'] = orientation
        if disabled:
            self._props['disabled'] = True

    def _value_to_model_value(self, value: Any) -> Any:
        if value is None:
            return ''
        if isinstance(value, str):
            return value
        return [str(item) for item in value]


def radio_group(options: Mapping[str, Any] | Iterable[Any] | None = None, **kwargs: Any) -> RadioGroup:
    """Create a :class:`RadioGroup`."""
    return RadioGroup(options, **kwargs)


def slider(value: float = 0, **kwargs: Any) -> Slider:
    """Create a :class:`Slider`."""
    return Slider(value, **kwargs)


def toggle(text: str = '', **kwargs: Any) -> Toggle:
    """Create a :class:`Toggle`."""
    return Toggle(text, **kwargs)


def toggle_group(options: Mapping[str, Any] | Iterable[Any] | None = None, **kwargs: Any) -> ToggleGroup:
    """Create a :class:`ToggleGroup`."""
    return ToggleGroup(options, **kwargs)

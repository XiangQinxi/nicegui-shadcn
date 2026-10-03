"""Form controls: label, input, textarea, checkbox and switch.

Each control is a real NiceGUI value element, so ``bind_value``, ``on_change``
and the usual NiceGUI value machinery work exactly as they do for ``ui.input``.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from nicegui.element import Element
from nicegui.elements.mixins.text_element import TextElement
from nicegui.elements.mixins.value_element import ValueElement

from .base import ShadcnElement

__all__ = [
    'Checkbox', 'Input', 'Label', 'Switch', 'Textarea',
    'checkbox', 'input', 'label', 'switch', 'textarea',
]

# --------------------------------------------------------------------------- #
# Label
# --------------------------------------------------------------------------- #


class Label(ShadcnElement, TextElement, default_classes='flex select-none items-center gap-2 text-sm font-medium leading-none'):
    """A ``<label>`` for a form control.

    :param text: the text to display.
    :param for_: the element (or DOM id) this label belongs to. NiceGUI assigns
        its element ids lazily, so passing the element itself is the reliable
        way to wire up ``for=``.
    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """

    def __init__(self,
                 text: str = '',
                 *,
                 for_: Element | str | None = None,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(tag='label', text=text, classes=classes, **kwargs)
        if for_ is not None:
            self._props['for'] = for_.html_id if isinstance(for_, Element) else for_


# --------------------------------------------------------------------------- #
# Text entry
# --------------------------------------------------------------------------- #

_INPUT_CLASSES = (
    'flex h-9 w-full min-w-0 rounded-md border border-input bg-transparent px-3 py-1 '
    'text-base shadow-xs outline-none transition-[color,box-shadow] md:text-sm '
    'placeholder:text-muted-foreground '
    'disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50 '
    'dark:bg-input/30 '
    'focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50 '
    'aria-invalid:border-destructive'
)

_TEXTAREA_CLASSES = (
    'flex min-h-16 w-full rounded-md border border-input bg-transparent px-3 py-2 '
    'text-base shadow-xs outline-none transition-[color,box-shadow] md:text-sm '
    'placeholder:text-muted-foreground '
    'disabled:cursor-not-allowed disabled:opacity-50 '
    'dark:bg-input/30 '
    'focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50 '
    'aria-invalid:border-destructive'
)


class Input(ShadcnElement, ValueElement, component='shadcn_input.vue', default_classes=_INPUT_CLASSES):
    """A single-line text field.

    :param value: the initial value.
    :param placeholder: text shown while the field is empty.
    :param type: the native input type (``text``, ``password``, ``email``, ...).
    :param disabled: render the component disabled.
    :param readonly: render the field read-only, so its value cannot be edited.
    :param autocomplete: the native ``autocomplete`` hint for the browser, e.g.
        ``'email'``, ``'current-password'`` or ``'off'``.
    :param on_change: callback invoked when the value changes.
    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """

    LOOPBACK = False

    def __init__(self,
                 value: str = '',
                 *,
                 placeholder: str | None = None,
                 type: str = 'text',  # noqa: A002 - mirrors shadcn/the DOM
                 disabled: bool = False,
                 readonly: bool = False,
                 autocomplete: str | None = None,
                 on_change: Any = None,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(
            value=value,
            on_value_change=on_change,
            classes=classes,
            **kwargs,
        )
        self._props['type'] = type
        if placeholder is not None:
            self._props['placeholder'] = placeholder
        if disabled:
            self._props['disabled'] = True
        if readonly:
            self._props['readonly'] = True
        if autocomplete is not None:
            self._props['autocomplete'] = autocomplete


class Textarea(ShadcnElement, ValueElement, component='shadcn_textarea.vue', default_classes=_TEXTAREA_CLASSES):
    """A multi-line text field.

    :param value: the initial value.
    :param placeholder: text shown while the field is empty.
    :param rows: how many text rows the field is tall.
    :param disabled: render the component disabled.
    :param readonly: render the field read-only, so its value cannot be edited.
    :param on_change: callback invoked when the value changes.
    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """

    LOOPBACK = False

    def __init__(self,
                 value: str = '',
                 *,
                 placeholder: str | None = None,
                 rows: int | None = None,
                 disabled: bool = False,
                 readonly: bool = False,
                 on_change: Any = None,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(
            value=value,
            on_value_change=on_change,
            classes=classes,
            **kwargs,
        )
        if placeholder is not None:
            self._props['placeholder'] = placeholder
        if rows is not None:
            self._props['rows'] = rows
        if disabled:
            self._props['disabled'] = True
        if readonly:
            self._props['readonly'] = True


# --------------------------------------------------------------------------- #
# Boolean controls
# --------------------------------------------------------------------------- #


class Checkbox(ShadcnElement, ValueElement, component='shadcn_checkbox.vue', default_classes='inline-flex'):
    """A checkbox with the shadcn/ui look.

    :param value: the initial checked state.
    :param disabled: render the component disabled.
    :param on_change: callback invoked when the value changes.
    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """

    def __init__(self,
                 value: bool = False,
                 *,
                 disabled: bool = False,
                 on_change: Any = None,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(
            value=bool(value),
            on_value_change=on_change,
            classes=classes,
            **kwargs,
        )
        if disabled:
            self._props['disabled'] = True

    def _value_to_model_value(self, value: Any) -> bool:
        return bool(value)

    def _value_to_event_value(self, value: Any) -> bool:
        return bool(value)


class Switch(ShadcnElement, ValueElement, component='shadcn_switch.vue', default_classes='inline-flex'):
    """An on/off switch with the shadcn/ui look.

    :param value: the initial on/off state.
    :param disabled: render the component disabled.
    :param on_change: callback invoked when the value changes.
    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """

    def __init__(self,
                 value: bool = False,
                 *,
                 disabled: bool = False,
                 on_change: Any = None,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(
            value=bool(value),
            on_value_change=on_change,
            classes=classes,
            **kwargs,
        )
        if disabled:
            self._props['disabled'] = True

    def _value_to_model_value(self, value: Any) -> bool:
        return bool(value)

    def _value_to_event_value(self, value: Any) -> bool:
        return bool(value)


# --------------------------------------------------------------------------- #
# Factories
# --------------------------------------------------------------------------- #


def label(text: str = '', **kwargs: Any) -> Label:
    """Create a :class:`Label`.

    :param text: the text to display.
    """
    return Label(text, **kwargs)


def input(value: str = '', **kwargs: Any) -> Input:  # noqa: A001 - matches the shadcn/ui name
    """Create an :class:`Input`.

    :param value: the initial value.
    """
    return Input(value, **kwargs)


def textarea(value: str = '', **kwargs: Any) -> Textarea:
    """Create a :class:`Textarea`.

    :param value: the initial value.
    """
    return Textarea(value, **kwargs)


def checkbox(value: bool = False, **kwargs: Any) -> Checkbox:
    """Create a :class:`Checkbox`.

    :param value: the initial checked state.
    """
    return Checkbox(value, **kwargs)


def switch(value: bool = False, **kwargs: Any) -> Switch:
    """Create a :class:`Switch`.

    :param value: the initial on/off state.
    """
    return Switch(value, **kwargs)

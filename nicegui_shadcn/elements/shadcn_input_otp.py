"""Input OTP: a one-time-password field with grouped character slots.

The character slots are decorative: a single invisible native ``<input>`` owns
the value, so paste, autofill, the on-screen keyboard and
``autocomplete="one-time-code"`` all behave the way the browser intended.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from typing import Any

from nicegui.elements.mixins.value_element import ValueElement

from .base import ShadcnElement

__all__ = [
    'REGEXP_ONLY_CHARS',
    'REGEXP_ONLY_DIGITS',
    'REGEXP_ONLY_DIGITS_AND_CHARS',
    'InputOTP',
    'input_otp',
]

#: Accept digits only.
REGEXP_ONLY_DIGITS = r'^\d+$'
#: Accept ASCII letters only.
REGEXP_ONLY_CHARS = r'^[a-zA-Z]+$'
#: Accept ASCII letters and digits.
REGEXP_ONLY_DIGITS_AND_CHARS = r'^[a-zA-Z0-9]+$'


class InputOTP(ShadcnElement, ValueElement, component='shadcn_input_otp.vue'):
    """A one-time-password field rendered as a row of character slots.

    :param value: the initial code.
    :param length: how many characters the field accepts.
    :param groups: optional run lengths, e.g. ``[3, 3]`` for ``123-456``. The
        runs must add up to ``length``.
    :param pattern: a per-character regular expression source, e.g.
        :data:`REGEXP_ONLY_DIGITS`. Characters that do not match are dropped as
        they are typed or pasted.
    :param masked: render the entered characters as dots.
    :param disabled: whether the field is read-only.
    :param inputmode: the ``inputmode`` hint for the on-screen keyboard.
    :param aria_label: the accessible name of the underlying text field.
    :param on_change: callback invoked with the value-change event when the code
        changes; read ``e.value`` for the new code.
    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """

    LOOPBACK = False

    def __init__(self,
                 value: str = '',
                 *,
                 length: int = 6,
                 groups: Sequence[int] | None = None,
                 pattern: str | None = None,
                 masked: bool = False,
                 disabled: bool = False,
                 inputmode: str = 'numeric',
                 aria_label: str = 'One-time password',
                 on_change: Callable[..., Any] | None = None,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(value=value, on_value_change=on_change, classes=classes, **kwargs)
        length = int(length)
        if length < 1:
            raise ValueError(f'length must be at least 1, got {length}')
        sizes: list[int] = []
        if groups is not None:
            sizes = [int(size) for size in groups]
            if any(size < 1 for size in sizes):
                raise ValueError(f'group sizes must be positive, got {sizes}')
            if sum(sizes) != length:
                raise ValueError(f'group sizes {sizes} do not add up to length {length}')
        self._props['length'] = length
        self._props['groups'] = sizes
        if pattern:
            self._props['pattern'] = str(pattern)
        self._props['masked'] = bool(masked)
        self._props['disabled'] = bool(disabled)
        self._props['inputmode'] = str(inputmode)
        self._props['ariaLabel'] = str(aria_label)

    def _value_to_model_value(self, value: Any) -> str:
        return '' if value is None else str(value)


def input_otp(value: str = '', **kwargs: Any) -> InputOTP:
    """Create an :class:`InputOTP`.

    :param value: the initial code.
    """
    return InputOTP(value, **kwargs)

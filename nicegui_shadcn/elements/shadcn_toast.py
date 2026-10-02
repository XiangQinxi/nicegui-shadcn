"""Toasts: short-lived notifications that stack in a corner of the viewport.

The API is two elements. A :class:`ToastProvider` owns the stack -- the corner
it grows from and the timing -- and every :class:`Toast` nested inside it is one
notification::

    with shadcn.toast_provider(position='bottom-right'):
        saved = shadcn.toast('Saved', description='Your changes are live.')

    saved.open()   # show it
    saved.close()  # or let it time out on its own

ReKa teleports each toast into the provider's viewport, so the toast elements
can be declared anywhere inside the provider.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any

from nicegui.elements.mixins.value_element import ValueElement

from .base import ShadcnElement, _Openable, option

__all__ = [
    'Toast', 'ToastProvider',
    'toast', 'toast_provider',
]

_TOAST_VARIANTS = {name: name for name in ('default', 'destructive', 'success')}
_TOAST_POSITIONS = {
    name: name for name in (
        'top-left', 'top-center', 'top-right',
        'bottom-left', 'bottom-center', 'bottom-right',
    )
}
_TOAST_SWIPE_DIRECTIONS = {name: name for name in ('up', 'down', 'left', 'right')}


class ToastProvider(ShadcnElement, component='shadcn_toast_provider.vue'):
    """The container that owns a stack of :class:`Toast` elements.

    :param position: the corner the stack grows from: ``'bottom-right'``
        (default), or any other combination of ``top``/``bottom`` and
        ``left``/``center``/``right``.
    :param duration: default milliseconds each toast stays up. Pass ``0`` to
        keep toasts up until they are closed by hand.
    :param swipe_direction: the direction a toast can be swiped away towards.
    """

    def __init__(self,
                 *,
                 position: str = 'bottom-right',
                 duration: int = 5000,
                 swipe_direction: str = 'right',
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(classes=classes, **kwargs)
        self._props['position'] = option('toast position', position, _TOAST_POSITIONS)
        self._props['duration'] = int(duration)
        self._props['swipeDirection'] = option('toast swipe direction', swipe_direction, _TOAST_SWIPE_DIRECTIONS)


class Toast(_Openable, ShadcnElement, ValueElement, component='shadcn_toast.vue'):
    """One notification inside a :class:`ToastProvider`.

    :param title: the bold first line.
    :param value: whether the toast starts out visible.
    :param description: optional supporting line below the title.
    :param variant: ``'default'``, ``'destructive'`` or ``'success'``.
    :param duration: milliseconds before it closes itself; ``0`` disables the
        timer. Defaults to the provider's duration when left as ``None``.
    :param closable: render the small close button.
    :param on_change: callback invoked with the value-change event when the
        toast opens or closes, which is how a timeout or a swipe reaches Python;
        read ``e.value`` for the new state.
    """

    def __init__(self,
                 title: str = '',
                 *,
                 value: bool = False,
                 description: str = '',
                 variant: str = 'default',
                 duration: int | None = None,
                 closable: bool = True,
                 on_change: Callable[..., Any] | None = None,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(value=bool(value), on_value_change=on_change, classes=classes, **kwargs)
        self._props['title'] = title
        self._props['description'] = description
        self._props['variant'] = option('toast variant', variant, _TOAST_VARIANTS)
        if duration is not None:
            self._props['duration'] = int(duration)
        if not closable:
            self._props['closable'] = False

    def _value_to_model_value(self, value: Any) -> bool:
        return bool(value)


def toast_provider(**kwargs: Any) -> ToastProvider:
    """Create a :class:`ToastProvider`."""
    return ToastProvider(**kwargs)


def toast(title: str = '', **kwargs: Any) -> Toast:
    """Create a :class:`Toast`."""
    return Toast(title, **kwargs)

"""Alert dialog: a modal that interrupts the user for a decision.

Shaped exactly like :mod:`nicegui_shadcn.elements.shadcn_overlay`'s dialog, with
two deliberate differences that come from upstream shadcn/ui:

* there is no close button, and clicking the backdrop does not dismiss it -- the
  user has to pick one of the actions. reka-ui enforces this by always rendering
  an alert dialog modally, and by making ``AlertDialogAction``/``AlertDialogCancel``
  wrap the dialog's close action, so both buttons dismiss it automatically.
* the panel carries ``role="alertdialog"``, so screen readers announce it the
  moment it opens instead of waiting for the user to go looking.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any

from nicegui.elements.mixins.text_element import TextElement
from nicegui.elements.mixins.value_element import ValueElement

from .base import ShadcnElement, _Openable
from .shadcn_button import button_classes as _button_classes

__all__ = [
    'AlertDialog', 'AlertDialogAction', 'AlertDialogCancel', 'AlertDialogContent',
    'AlertDialogFooter', 'AlertDialogTrigger',
    'alert_dialog', 'alert_dialog_action', 'alert_dialog_cancel', 'alert_dialog_content',
    'alert_dialog_footer', 'alert_dialog_trigger',
]


class AlertDialog(_Openable, ShadcnElement, ValueElement, component='shadcn_alert_dialog.vue'):
    """A modal dialog that must be answered.

    :param value: whether the dialog starts out open.
    :param on_change: callback invoked with the value-change event when the open state changes; read ``e.value`` for the new state.
        Use it to learn *which* way the user got out -- both actions close the
        dialog, so the state alone cannot tell them apart.
    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """

    def __init__(self,
                 value: bool = False,
                 *,
                 on_change: Callable[..., Any] | None = None,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(value=bool(value), on_value_change=on_change, classes=classes, **kwargs)

    def _value_to_model_value(self, value: Any) -> bool:
        return bool(value)


class AlertDialogTrigger(ShadcnElement, TextElement, component='shadcn_alert_dialog_trigger.vue',
                         default_classes=_button_classes('outline')):
    """The element that opens an :class:`AlertDialog` when clicked.

    :param text: the text to display.
    :param as_child: render the child element instead of a wrapper.
    :param on_click: callback invoked on click.
    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """

    def __init__(self,
                 text: str = '',
                 *,
                 as_child: bool = False,
                 on_click: Callable[..., Any] | None = None,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(text=text, classes=classes, **kwargs)
        if as_child:
            self._props['asChild'] = True
        if on_click is not None:
            self.on('click', on_click)


class AlertDialogContent(ShadcnElement, component='shadcn_alert_dialog_content.vue'):
    """The panel of an :class:`AlertDialog`.

    :param title: heading text. When omitted the panel stays accessible but
        visually untitled, so the heading is rendered for screen readers only.
    :param description: optional supporting text below the title.
    :param aria_label: fallback heading when ``title`` is empty.
    :param classes: classes for the panel itself, which lives in a portal.
    """

    def __init__(self,
                 title: str | None = None,
                 *,
                 description: str | None = None,
                 aria_label: str = 'Alert',
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(classes=classes, **kwargs)
        self._props['title'] = title
        self._props['description'] = description
        self._props['ariaLabel'] = aria_label


class AlertDialogAction(ShadcnElement, TextElement, component='shadcn_alert_dialog_action.vue',
                        default_classes=_button_classes()):
    """The confirming button. Clicking it closes the dialog.

    :param text: the text to display.
    :param on_click: callback invoked when it is clicked. It runs before the
        dialog closes, and the dialog closes whether or not it raises.
    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """

    def __init__(self,
                 text: str = '',
                 *,
                 on_click: Callable[..., Any] | None = None,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(text=text, classes=classes, **kwargs)
        if on_click is not None:
            self.on('click', on_click)


class AlertDialogCancel(ShadcnElement, TextElement, component='shadcn_alert_dialog_cancel.vue',
                        default_classes=_button_classes('outline')):
    """The dismissing button. Clicking it closes the dialog.

    :param text: the text to display.
    :param on_click: callback invoked when it is clicked.
    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """

    def __init__(self,
                 text: str = '',
                 *,
                 on_click: Callable[..., Any] | None = None,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(text=text, classes=classes, **kwargs)
        if on_click is not None:
            self.on('click', on_click)


class AlertDialogFooter(ShadcnElement, default_classes='flex flex-col-reverse gap-2 sm:flex-row sm:justify-end'):
    """The action row at the bottom of an :class:`AlertDialogContent`.

    :param classes: extra utility classes, merged with ``cn()`` semantics.
    :param variant_classes: classes implied by the variant, set by the component itself.
    """


def alert_dialog(value: bool = False, **kwargs: Any) -> AlertDialog:
    """Create an :class:`AlertDialog`.

    :param value: whether the dialog starts out open.
    """
    return AlertDialog(value, **kwargs)


def alert_dialog_trigger(text: str = '', **kwargs: Any) -> AlertDialogTrigger:
    """Create an :class:`AlertDialogTrigger`.

    :param text: the text to display.
    """
    return AlertDialogTrigger(text, **kwargs)


def alert_dialog_content(title: str | None = None, **kwargs: Any) -> AlertDialogContent:
    """Create an :class:`AlertDialogContent`.

    :param title: heading text, rendered for screen readers only when omitted.
    """
    return AlertDialogContent(title, **kwargs)


def alert_dialog_action(text: str = '', **kwargs: Any) -> AlertDialogAction:
    """Create an :class:`AlertDialogAction`.

    :param text: the text to display.
    """
    return AlertDialogAction(text, **kwargs)


def alert_dialog_cancel(text: str = '', **kwargs: Any) -> AlertDialogCancel:
    """Create an :class:`AlertDialogCancel`.

    :param text: the text to display.
    """
    return AlertDialogCancel(text, **kwargs)


def alert_dialog_footer(**kwargs: Any) -> AlertDialogFooter:
    """Create an :class:`AlertDialogFooter`."""
    return AlertDialogFooter(**kwargs)

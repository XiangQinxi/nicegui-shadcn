"""Accordion, built on reka-ui's disclosure primitives.

::

    with shadcn.accordion(value='shipping'):
        with shadcn.accordion_item(value='shipping'):
            shadcn.accordion_trigger('How do you ship?')
            with shadcn.accordion_content():
                shadcn.label('We ship by carrier pigeon, weather permitting.')

``multiple=True`` switches reka-ui to ``type="multiple"``, in which case
``value`` is a list and several sections can be open at once.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any

from nicegui.elements.mixins.text_element import TextElement
from nicegui.elements.mixins.value_element import ValueElement

from .base import ShadcnElement

__all__ = [
    'Accordion', 'AccordionContent', 'AccordionItem', 'AccordionTrigger',
    'accordion', 'accordion_content', 'accordion_item', 'accordion_trigger',
]

_ACCORDION_ITEM_CLASSES = 'border-b last:border-b-0'

# The trigger's own classes live in the template: the component's root has to be
# reka-ui's `AccordionHeader` (an <h3>, needed for the ARIA structure), and the
# caller's classes are forwarded to the inner <button> with `v-bind="$attrs"`.
# The content is kept mounted (`force-mount`) so that the child elements always
# exist on the client and server-side updates can always reach them; `hidden`
# then does the hiding, because reka only sets `data-state` on a mounted panel.
_ACCORDION_CONTENT_CLASSES = (
    'overflow-hidden text-sm data-[state=open]:animate-accordion-down data-[state=closed]:hidden'
)


def _as_model_value(value: Any) -> Any:
    if value is None:
        return ''
    if isinstance(value, str | int | float):
        return str(value)
    return [str(item) for item in value]


class Accordion(ShadcnElement, ValueElement, component='shadcn_accordion.vue', default_classes='flex w-full flex-col'):
    """The root of an accordion.

    :param value: value of the open section (``multiple=True``: a list of values).
    :param multiple: allow more than one section to be open at the same time.
    :param collapsible: allow closing the open section again (single mode only).
    :param orientation: ``'vertical'`` or ``'horizontal'``.
    :param on_change: callback invoked with the new value whenever it changes.
    """

    def __init__(self,
                 value: str | Iterable[str] | None = None,
                 *,
                 multiple: bool = False,
                 collapsible: bool = True,
                 orientation: str = 'vertical',
                 on_change: Callable[..., Any] | None = None,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(value=value, on_value_change=on_change, classes=classes, **kwargs)
        self._props['type'] = 'multiple' if multiple else 'single'
        self._props['collapsible'] = bool(collapsible) and not multiple
        self._props['orientation'] = orientation

    def _value_to_model_value(self, value: Any) -> Any:
        return _as_model_value(value)


class AccordionItem(ShadcnElement, component='shadcn_accordion_item.vue', default_classes=_ACCORDION_ITEM_CLASSES):
    """One collapsible section; put a trigger and a content element inside."""

    def __init__(self,
                 value: str,
                 *,
                 disabled: bool = False,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(classes=classes, **kwargs)
        self._props['value'] = str(value)
        if disabled:
            self._props['disabled'] = True


class AccordionTrigger(ShadcnElement, TextElement, component='shadcn_accordion_trigger.vue'):
    """The clickable header of an :class:`AccordionItem`.

    Classes given here end up on the ``<button>``, not on the surrounding
    ``<h3>``, because the template forwards ``$attrs`` to the button.
    """

    def __init__(self,
                 text: str = '',
                 *,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(text=text, classes=classes, **kwargs)


class AccordionContent(ShadcnElement, component='shadcn_accordion_content.vue', default_classes=_ACCORDION_CONTENT_CLASSES):
    """The body of an :class:`AccordionItem`."""


def accordion(value: str | Iterable[str] | None = None, **kwargs: Any) -> Accordion:
    """Create an :class:`Accordion`."""
    return Accordion(value, **kwargs)


def accordion_item(value: str, **kwargs: Any) -> AccordionItem:
    """Create an :class:`AccordionItem`."""
    return AccordionItem(value, **kwargs)


def accordion_trigger(text: str = '', **kwargs: Any) -> AccordionTrigger:
    """Create an :class:`AccordionTrigger`."""
    return AccordionTrigger(text, **kwargs)


def accordion_content(**kwargs: Any) -> AccordionContent:
    """Create an :class:`AccordionContent`."""
    return AccordionContent(**kwargs)

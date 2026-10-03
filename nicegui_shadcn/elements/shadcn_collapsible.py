"""Collapsible: a single show/hide region with an accessible trigger.

::

    with shadcn.collapsible():
        shadcn.collapsible_trigger('Show details')
        with shadcn.collapsible_content():
            shadcn.label('The details.')

The trigger is reka-ui's ``<button>``, which already carries ``aria-expanded`` and
``aria-controls``; the content stays mounted so that elements inside it keep their
server-side counterparts, and ``data-[state=closed]:hidden`` does the hiding
(reka only sets ``data-state`` on a force-mounted panel, never ``hidden``).
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any

from nicegui.elements.mixins.text_element import TextElement
from nicegui.elements.mixins.value_element import ValueElement

from .base import ShadcnElement, _Openable

__all__ = [
    'Collapsible', 'CollapsibleContent', 'CollapsibleTrigger',
    'collapsible', 'collapsible_content', 'collapsible_trigger',
]

_COLLAPSIBLE_TRIGGER_CLASSES = (
    'inline-flex items-center gap-2 text-sm font-medium transition-all hover:underline '
    '[&[data-state=open]>svg]:rotate-180'
)

_COLLAPSIBLE_CONTENT_CLASSES = (
    'overflow-hidden text-sm data-[state=open]:animate-collapsible-down data-[state=closed]:hidden'
)


class Collapsible(_Openable, ShadcnElement, ValueElement, component='shadcn_collapsible.vue'):
    """The root of a collapsible region.

    :param value: whether the region starts out open.
    :param disabled: grey out the trigger and refuse to toggle.
    :param on_change: callback invoked with the value-change event when the open state changes; read ``e.value`` for the new state.
    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """

    def __init__(self,
                 value: bool = False,
                 *,
                 disabled: bool = False,
                 on_change: Callable[..., Any] | None = None,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(value=bool(value), on_value_change=on_change, classes=classes, **kwargs)
        if disabled:
            self._props['disabled'] = True

    def _value_to_model_value(self, value: Any) -> bool:
        return bool(value)


class CollapsibleTrigger(ShadcnElement, TextElement, component='shadcn_collapsible_trigger.vue',
                         default_classes=_COLLAPSIBLE_TRIGGER_CLASSES):
    """The clickable header of a :class:`Collapsible`.

    :param text: the text to display.
    :param as_child: merge the trigger's behaviour into the single child element
        instead of rendering its own ``<button>`` -- useful for making a whole
        card clickable. The child then has to be a button-like element itself.
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


class CollapsibleContent(ShadcnElement, component='shadcn_collapsible_content.vue',
                         default_classes=_COLLAPSIBLE_CONTENT_CLASSES):
    """The region that expands and collapses.

    :param classes: extra utility classes, merged with ``cn()`` semantics.
    :param variant_classes: classes implied by the variant, set by the component itself.
    """


def collapsible(value: bool = False, **kwargs: Any) -> Collapsible:
    """Create a :class:`Collapsible`.

    :param value: whether the region starts out open.
    """
    return Collapsible(value, **kwargs)


def collapsible_trigger(text: str = '', **kwargs: Any) -> CollapsibleTrigger:
    """Create a :class:`CollapsibleTrigger`.

    :param text: the text to display.
    """
    return CollapsibleTrigger(text, **kwargs)


def collapsible_content(**kwargs: Any) -> CollapsibleContent:
    """Create a :class:`CollapsibleContent`."""
    return CollapsibleContent(**kwargs)

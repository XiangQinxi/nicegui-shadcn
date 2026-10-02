"""The button group: several buttons that read as one control.

The grouping is pure CSS on the container -- the children keep their own
classes, and the group rounds only the two outer corners and pulls the inner
edges together with a negative margin. That means any mix of sizes and variants
works, but every child should be the same height for the seams to line up.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from nicegui.elements.mixins.text_element import TextElement

from .base import ShadcnElement

__all__ = [
    'ButtonGroup', 'ButtonGroupSeparator', 'ButtonGroupText',
    'button_group', 'button_group_separator', 'button_group_text',
]

# The child rules have to out-specify the children's own rounding, which is why
# they are written as arbitrary variants on the container rather than as classes
# on the buttons -- the caller never has to know they exist.
_BUTTON_GROUP_HORIZONTAL_CLASSES = (
    'inline-flex w-fit items-stretch [&>*]:rounded-none '
    '[&>*:first-child]:rounded-l-md [&>*:last-child]:rounded-r-md [&>*+*]:-ml-px'
)
_BUTTON_GROUP_VERTICAL_CLASSES = (
    'inline-flex w-fit flex-col items-stretch [&>*]:rounded-none '
    '[&>*:first-child]:rounded-t-md [&>*:last-child]:rounded-b-md [&>*+*]:-mt-px'
)


class ButtonGroup(ShadcnElement, default_classes=_BUTTON_GROUP_HORIZONTAL_CLASSES):
    """A row (or column) of buttons joined into one control.

    :param vertical: stack the buttons instead of placing them side by side.
    """

    def __init__(self,
                 *,
                 vertical: bool = False,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        variant_classes = _BUTTON_GROUP_VERTICAL_CLASSES if vertical else None
        super().__init__(classes=classes, variant_classes=variant_classes, **kwargs)


class ButtonGroupText(ShadcnElement, TextElement,
                      default_classes='flex items-center gap-2 rounded-md border bg-muted px-4 text-sm font-medium'):
    """Static text (or an icon) that sits inside a :class:`ButtonGroup`."""

    def __init__(self,
                 text: str = '',
                 *,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(text=text, classes=classes, **kwargs)


_BUTTON_GROUP_SEPARATOR_HORIZONTAL_CLASSES = 'relative w-px self-stretch bg-input'
_BUTTON_GROUP_SEPARATOR_VERTICAL_CLASSES = 'relative h-px w-full bg-input'


class ButtonGroupSeparator(ShadcnElement, default_classes=_BUTTON_GROUP_SEPARATOR_HORIZONTAL_CLASSES):
    """A hairline between two buttons of a :class:`ButtonGroup`."""

    def __init__(self,
                 *,
                 vertical: bool = False,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        variant_classes = _BUTTON_GROUP_SEPARATOR_VERTICAL_CLASSES if vertical else None
        super().__init__(classes=classes, variant_classes=variant_classes, **kwargs)


def button_group(**kwargs: Any) -> ButtonGroup:
    """Create a :class:`ButtonGroup`."""
    return ButtonGroup(**kwargs)


def button_group_text(text: str = '', **kwargs: Any) -> ButtonGroupText:
    """Create a :class:`ButtonGroupText`."""
    return ButtonGroupText(text, **kwargs)


def button_group_separator(**kwargs: Any) -> ButtonGroupSeparator:
    """Create a :class:`ButtonGroupSeparator`."""
    return ButtonGroupSeparator(**kwargs)

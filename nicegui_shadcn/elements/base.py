"""Shared machinery for the shadcn/ui elements.

The interesting part is :class:`ShadcnElement`, which gives every component
``cn()`` semantics: the classes a component ships with, the classes its
*placement* implies (its variant/size) and the classes the caller passes are
merged with :func:`.._tw_merge.tw_merge`, so a later utility always wins over
an earlier one for the same CSS property.

That matters because NiceGUI 3.x dropped the ``classes=`` constructor keyword
from ``Element``: ``Element.classes()`` appends, it does not resolve conflicts.
Without the merge, ``shadcn.button('Save', classes='bg-destructive')`` would
emit both ``bg-primary`` and ``bg-destructive`` and the winner would be decided
by stylesheet order rather than by the caller's intent.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any, TypeVar

from nicegui.element import Element
from nicegui.elements.mixins.text_element import TextElement

from .._tw_merge import tw_merge

__all__ = ['ShadcnElement', 'Text', 'as_class_string', 'normalize_options', 'option']

T = TypeVar('T')


def as_class_string(value: str | Iterable[str] | None) -> str:
    """Normalise ``None``, a string or an iterable of strings to one string."""
    if value is None:
        return ''
    if isinstance(value, str):
        return value
    return ' '.join(str(item) for item in value)


def normalize_options(options: Mapping[str, Any] | Iterable[Any]) -> list[dict[str, Any]]:
    """Normalise a list of choices for the components that render a menu.

    Accepts, in the spirit of the rest of the library:

    * a mapping ``{value: label}``,
    * a sequence of strings (value and label are the same),
    * a sequence of ``(value, label)`` pairs,
    * a sequence of mappings with the keys ``value``, ``label``, ``disabled``,
      ``kind`` (``'item'``, ``'label'`` or ``'separator'``) and ``variant``
      (``'default'`` or ``'destructive'``).

    Everything is coerced to the plain JSON-safe shape the Vue templates expect.
    """
    if isinstance(options, Mapping):
        return [{'value': str(key), 'label': str(value)} for key, value in options.items()]

    result: list[dict[str, Any]] = []
    for item in options:
        if isinstance(item, str):
            result.append({'value': item, 'label': item})
        elif isinstance(item, Mapping):
            value = str(item.get('value', item.get('label', '')))
            result.append({
                'value': value,
                'label': str(item.get('label', value)),
                'disabled': bool(item.get('disabled', False)),
                'kind': str(item.get('kind', 'item')),
                'variant': str(item.get('variant', 'default')),
            })
        else:
            value, label = item
            result.append({'value': str(value), 'label': str(label)})
    return result


def option(kind: str, value: str, options: Mapping[str, T]) -> T:
    """Look up ``value`` in ``options``, raising a helpful error if unknown.

    shadcn/ui spells its variants as string literals; failing loudly with the
    list of valid choices beats a silent fallback that renders nothing.
    """
    try:
        return options[value]
    except KeyError:
        valid = ', '.join(repr(key) for key in options)
        raise ValueError(f'Unknown {kind} {value!r}. Valid options are: {valid}') from None


class ShadcnElement(Element):
    """Base class of all shadcn/ui elements.

    Additional keyword arguments compared to :class:`nicegui.element.Element`:

    :param classes: extra utility classes supplied by the caller. They win over
        both the component's own classes and its ``variant_classes``.
    :param variant_classes: classes implied by the selected variant/size. They
        win over the component's own classes but lose to ``classes``.
    """

    def __init__(self,
                 *,
                 classes: str | Iterable[str] | None = None,
                 variant_classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(**kwargs)
        merged = tw_merge(
            ' '.join(self._classes),
            as_class_string(variant_classes),
            as_class_string(classes),
        )
        if merged != ' '.join(self._classes):
            self.classes(replace=merged)

    def with_classes(self, classes: str | Iterable[str]) -> 'ShadcnElement':
        """Merge additional classes into this element and return it.

        Unlike :meth:`nicegui.element.Element.classes` this resolves conflicts
        instead of appending, so the newly supplied utilities win.
        """
        merged = tw_merge(' '.join(self._classes), as_class_string(classes))
        self.classes(replace=merged)
        return self


class Text(TextElement):
    """A bare text element.

    NiceGUI's :class:`nicegui.elements.label.Label` renders a ``<div>``, which
    is invalid inside a ``<button>`` or a ``<p>``. Components that need an
    inline text node use this ``<span>`` instead.
    """

    def __init__(self, text: str = '', *, tag: str = 'span') -> None:
        super().__init__(tag=tag, text=text)

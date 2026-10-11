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
    """Normalise ``None``, a string or an iterable of strings to one string.

    :param value: ``None``, a string or an iterable of strings; ``None`` becomes
        the empty string and an iterable is joined with single spaces.
    """
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
      (``'default'`` or ``'destructive'``),
    * a mapping ``{value: mapping}`` whose inner mapping uses those same keys.

    Everything is coerced to the plain JSON-safe shape the Vue templates expect.
    An entry of an unsupported shape raises a :class:`ValueError` naming it.

    :param options: the choices to offer, in any of the shapes listed above.
    """
    if isinstance(options, Mapping):
        # A mapping value may be the label itself or a full option mapping, which
        # lets a caller write `{'day': 'Day', 'month': {'label': 'Month', 'disabled': True}}`.
        items: Iterable[Any] = (
            {'value': key, 'label': value} if not isinstance(value, Mapping)
            else {**value, 'value': value.get('value', key)}
            for key, value in options.items()
        )
    else:
        items = options

    result: list[dict[str, Any]] = []
    for item in items:
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
            try:
                value, label = item
            except (TypeError, ValueError):
                raise ValueError(
                    f'Unsupported option {item!r}: pass a string, a (value, label) pair or a '
                    'mapping with the value/label/disabled/kind/variant keys',
                ) from None
            result.append({'value': str(value), 'label': str(label)})
    return result


def option(kind: str, value: str, options: Mapping[str, T]) -> T:
    """Look up ``value`` in ``options``, raising a helpful error if unknown.

    shadcn/ui spells its variants as string literals; failing loudly with the
    list of valid choices beats a silent fallback that renders nothing.

    :param kind: the name of the option table, used in the error message, e.g.
        ``'heading level'``.
    :param value: the value to look up.
    :param options: the mapping of valid values to their class strings.
    """
    try:
        return options[value]
    except KeyError:
        valid = ', '.join(repr(key) for key in options)
        raise ValueError(f'Unknown {kind} {value!r}. Valid options are: {valid}') from None


# Shared placement vocabularies: reka-ui spells the same four sides and three
# alignments everywhere, so the floating components use these tables instead of
# each declaring its own copy.
_SIDES = {'top': 'top', 'right': 'right', 'bottom': 'bottom', 'left': 'left'}
_ALIGNMENTS = {'start': 'start', 'center': 'center', 'end': 'end'}
# reka-ui spells the two orientations the same way for its accordion, tabs,
# slider and toggle group.
_ORIENTATIONS = {'vertical': 'vertical', 'horizontal': 'horizontal'}


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

        :param classes: extra utility classes, merged with ``cn()`` semantics.
        """
        merged = tw_merge(' '.join(self._classes), as_class_string(classes))
        self.classes(replace=merged)
        return self


# ``Element.__init_subclass__`` copies ``component`` onto every subclass it creates. That
# materialises ``component = None`` in this class's own ``__dict__``, and because
# ``ShadcnElement`` is listed first in the bases of every component here, the copy shadows the
# Vue component inherited from a *secondary* base such as ``Html``. The element then silently
# degrades to a ``<div>`` with the props leaked as attributes -- no error, no warning.
# Dropping the copy lets the normal MRO lookup find the real component again.
del ShadcnElement.component


class _Disableable:
    """Mixin for the elements whose Vue component takes reka-ui's ``disabled`` prop.

    The keyword arguments of the constructors cover the initial state; this adds
    the same choice at runtime, which NiceGUI elements otherwise cannot express
    (this version of NiceGUI has no enable/disable API).  ``_init_disabled`` only
    sends the prop when it is set, which matches the ``default: false`` of every
    ``disabled`` prop on the Vue side.

    Not part of the public surface: it is mixed into the controls so that they all
    spell the attribute the same way.
    """

    def _init_disabled(self, disabled: bool) -> None:
        if disabled:
            self._props['disabled'] = True  # type: ignore[attr-defined]

    @property
    def disabled(self) -> bool:
        """Whether the control is disabled."""
        return bool(self._props.get('disabled', False))  # type: ignore[attr-defined]

    @disabled.setter
    def disabled(self, value: bool) -> None:
        if value:
            self._props['disabled'] = True  # type: ignore[attr-defined]
        else:
            self._props.pop('disabled', None)  # type: ignore[attr-defined]
        self.update()  # type: ignore[attr-defined]


class _Openable:
    """Mixin giving an overlay element explicit ``open``/``close``/``toggle`` methods.

    Not part of the public surface: it is mixed into the dialog-like elements so
    that they can be driven from a callback as well as from a trigger.
    """

    def open(self) -> None:  # noqa: A003 - matches the DOM/ARIA vocabulary
        """Show the overlay."""
        self.set_value(True)  # type: ignore[attr-defined]

    def close(self) -> None:
        """Hide the overlay."""
        self.set_value(False)  # type: ignore[attr-defined]

    def toggle(self) -> None:
        """Flip the overlay between shown and hidden."""
        self.set_value(not self.value)  # type: ignore[attr-defined]


class Text(TextElement):
    """A bare text element.

    NiceGUI's :class:`nicegui.elements.label.Label` renders a ``<div>``, which
    is invalid inside a ``<button>`` or a ``<p>``. Components that need an
    inline text node use this ``<span>`` instead.

    :param text: the text to display.
    :param tag: the HTML tag to render, ``'span'`` by default.
    """

    def __init__(self, text: str = '', *, tag: str = 'span') -> None:
        super().__init__(tag=tag, text=text)

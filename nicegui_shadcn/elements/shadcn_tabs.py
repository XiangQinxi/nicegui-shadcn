"""Tabs, built on reka-ui's tab primitives.

The composition mirrors shadcn/ui itself: a :class:`Tabs` root, a
:class:`TabsList` carrying one tab per entry, and one :class:`TabsContent` panel
per value::

    with shadcn.tabs(value='account'):
        shadcn.tabs_list([('account', 'Account'), ('password', 'Password')])
        with shadcn.tabs_content(value='account'):
            shadcn.input('Ada Lovelace')
        with shadcn.tabs_content(value='password'):
            shadcn.input('hunter2', type='password')

The tab labels are data rather than elements on purpose. reka-ui's ``TabsList``
provides the roving-focus context that ``TabsTrigger`` injects, and that
injection does not survive being routed through a NiceGUI slot: each tab's
trigger would be created outside the list's instance chain and fail with
``Injection `Symbol(RovingFocusGroupContext)` not found``. Generating the
triggers inside the list component keeps them inside that context, which is what
:class:`~nicegui_shadcn.elements.shadcn_controls.ToggleGroup` does as well.

The panels stay mounted (``force-mount``) so that form state inside an inactive
tab is not thrown away when the user switches tabs.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from typing import Any

from nicegui.elements.mixins.value_element import ValueElement

from .base import ShadcnElement, normalize_options

__all__ = [
    'Tabs', 'TabsContent', 'TabsList',
    'tabs', 'tabs_content', 'tabs_list',
]

_TABS_LIST_CLASSES = 'inline-flex h-9 w-fit items-center justify-center rounded-lg bg-muted p-[3px] text-muted-foreground'

# The individual tab buttons are generated inside ``shadcn_tabs_list.vue``; their
# classes travel there as a prop so that every class string still lives in Python
# (and is therefore covered by tests/audit_classes.py).
_TABS_TRIGGER_CLASSES = (
    'inline-flex h-[calc(100%-1px)] flex-1 items-center justify-center gap-1.5 rounded-md border border-transparent '
    'px-2 py-1 text-sm font-medium whitespace-nowrap text-foreground/60 transition-all '
    'hover:text-foreground focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50 '
    'disabled:pointer-events-none disabled:opacity-50 '
    'data-[state=active]:bg-background data-[state=active]:text-foreground data-[state=active]:shadow-sm '
    'dark:text-muted-foreground dark:data-[state=active]:text-foreground '
    'dark:data-[state=active]:border-input dark:data-[state=active]:bg-input/30'
)

_TABS_CONTENT_CLASSES = 'flex-1 outline-none data-[state=inactive]:hidden'


class Tabs(ShadcnElement, ValueElement, component='shadcn_tabs.vue', default_classes='flex w-full flex-col gap-2'):
    """The root of a tab group.

    :param value: the value of the initially selected tab.
    :param orientation: ``'horizontal'`` or ``'vertical'``.
    :param on_change: callback invoked with the new value whenever the selection changes.
    """

    def __init__(self,
                 value: str | int | None = None,
                 *,
                 orientation: str = 'horizontal',
                 on_change: Callable[..., Any] | None = None,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(value=value, on_value_change=on_change, classes=classes, **kwargs)
        self._props['orientation'] = orientation

    def _value_to_model_value(self, value: Any) -> str:
        # reka-ui treats `undefined` as uncontrolled and `''` as "nothing
        # selected"; the latter is what a Python `None` means here.
        return '' if value is None else str(value)


class TabsList(ShadcnElement, component='shadcn_tabs_list.vue', default_classes=_TABS_LIST_CLASSES):
    """The strip of tab labels.

    :param tabs: the tabs, in any of the shapes
        :func:`nicegui_shadcn.elements.base.normalize_options` accepts. A plain
        ``{'account': 'Account'}`` mapping or ``['account', 'password']`` list is
        usually enough; use mappings with ``value``/``label``/``disabled`` when a
        tab needs a different label from its value or has to be disabled.
    """

    def __init__(self,
                 tabs: Mapping[str, Any] | Iterable[Any] | None = None,
                 *,
                 orientation: str = 'horizontal',
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(classes=classes, **kwargs)
        self._props['tabs'] = normalize_options(tabs or [])
        self._props['orientation'] = orientation
        self._props['triggerClasses'] = _TABS_TRIGGER_CLASSES

    def set_tabs(self, tabs: Mapping[str, Any] | Iterable[Any]) -> None:
        """Replace the list of tabs."""
        self._props['tabs'] = normalize_options(tabs)
        self.update()


class TabsContent(ShadcnElement, component='shadcn_tabs_content.vue', default_classes=_TABS_CONTENT_CLASSES):
    """The panel belonging to one tab value."""

    def __init__(self,
                 value: str,
                 *,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(classes=classes, **kwargs)
        self._props['value'] = str(value)


def tabs(value: str | int | None = None, **kwargs: Any) -> Tabs:
    """Create a :class:`Tabs`."""
    return Tabs(value, **kwargs)


def tabs_list(tabs: Mapping[str, Any] | Iterable[Any] | None = None, **kwargs: Any) -> TabsList:
    """Create a :class:`TabsList`."""
    return TabsList(tabs, **kwargs)


def tabs_content(value: str, **kwargs: Any) -> TabsContent:
    """Create a :class:`TabsContent`."""
    return TabsContent(value, **kwargs)

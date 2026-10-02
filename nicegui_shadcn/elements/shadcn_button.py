"""``shadcn.button`` — shadcn/ui button, rendered as a real ``<button>``.

The Quasar/QBtn button that NiceGUI ships has its own prop-driven look, so this
component is a plain HTML button with shadcn's class vocabulary. It keeps
NiceGUI's ergonomics (``text``, ``on_click``, ``enabled``) while the visuals
come straight from shadcn's variant table.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any

from nicegui import ui

from .. import icons
from .._tw_merge import tw_join
from .base import ShadcnElement, Text, option

__all__ = ['Button', 'button']

_BASE = (
    'inline-flex items-center justify-center gap-2 whitespace-nowrap shrink-0 select-none '
    'rounded-md text-sm font-medium transition-all outline-none '
    'disabled:pointer-events-none disabled:opacity-50 '
    '[&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0 '
    'focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50'
)

_VARIANTS = {
    'default': 'bg-primary text-primary-foreground shadow-xs hover:bg-primary/90',
    'destructive': (
        'bg-destructive text-white shadow-xs hover:bg-destructive/90 '
        'focus-visible:ring-destructive/20 dark:focus-visible:ring-destructive/40'
    ),
    'outline': (
        'border bg-background shadow-xs hover:bg-accent hover:text-accent-foreground '
        'dark:bg-input/30 dark:border-input dark:hover:bg-input/50'
    ),
    'secondary': 'bg-secondary text-secondary-foreground shadow-xs hover:bg-secondary/80',
    'ghost': 'hover:bg-accent hover:text-accent-foreground dark:hover:bg-accent/50',
    'link': 'text-primary underline-offset-4 hover:underline',
}

_SIZES = {
    'default': 'h-9 px-4 py-2',
    'sm': 'h-8 gap-1.5 px-3',
    'lg': 'h-10 px-6',
    'icon': 'size-9',
}


def button_classes(variant: str = 'default', size: str = 'default') -> str:
    """Compose the standard button styling, for elements that render as a button.

    Triggers, menu entries and confirmation buttons are all ``<button>`` elements
    that reka-ui renders for us, so they cannot subclass :class:`Button`; they
    borrow its tables instead. Deliberately not in ``__all__`` — it is internal
    plumbing, not a component.
    """
    return tw_join(_BASE, option('button variant', variant, _VARIANTS), option('button size', size, _SIZES))


class Button(ShadcnElement, default_classes=_BASE):
    """A shadcn/ui button.

    :param text: label of the button.
    :param variant: ``default``, ``destructive``, ``outline``, ``secondary``,
        ``ghost`` or ``link``.
    :param size: ``default``, ``sm``, ``lg`` or ``icon``.
    :param icon: optional lucide icon name, e.g. ``'check'``.
    :param icon_position: ``'left'`` or ``'right'``.
    :param loading: show a spinner and disable the button.
    :param disabled: render the button disabled.
    :param on_click: callback invoked on click.
    :param classes: extra utility classes, merged with ``cn()`` semantics.
    """

    def __init__(self,
                 text: str = '',
                 *,
                 variant: str = 'default',
                 size: str = 'default',
                 icon: str | None = None,
                 icon_position: str = 'left',
                 loading: bool = False,
                 disabled: bool = False,
                 on_click: Callable[..., Any] | None = None,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(
            tag='button',
            classes=classes,
            variant_classes=tw_join(
                'shadcn-button',
                option('button variant', variant, _VARIANTS),
                option('button size', size, _SIZES),
            ),
            **kwargs,
        )
        self._props['type'] = 'button'
        self._label: Text | None = None
        self._text_value = ''
        # ``size='icon'`` is a square button, so a visible label would spill out
        # of it. The label is kept for screen readers instead (shadcn/ui relies on
        # the caller passing only an icon here, which is easy to get wrong).
        self._icon_only = size == 'icon'

        if loading:
            with self:
                ui.html(icons.svg('loader-circle', classes='animate-spin'), sanitize=False, tag='span')
        if icon and icon_position == 'left':
            with self:
                ui.html(icons.svg(icon), sanitize=False, tag='span')
        if text:
            with self:
                self._label = Text(text)
        if icon and icon_position == 'right':
            with self:
                ui.html(icons.svg(icon), sanitize=False, tag='span')

        self._text_value = text
        self._style_label()
        if self._icon_only and not text and icon:
            self._props['aria-label'] = icon
        self.set_enabled(not disabled and not loading)
        if on_click is not None:
            self.on('click', on_click)

    @property
    def text(self) -> str:
        """The label of the button."""
        return self._text_value

    @text.setter
    def text(self, value: str) -> None:
        self.set_text(value)

    def _style_label(self) -> None:
        """Keep an icon button's label out of sight, but not out of the a11y tree."""
        if self._label is None:
            return
        if self._icon_only:
            self._label.classes('sr-only')
            self._props['aria-label'] = self._text_value
        else:
            self._props.pop('aria-label', None)

    def set_text(self, text: str) -> None:
        """Set the label of the button."""
        self._text_value = text
        if self._label is None:
            if not text:
                return
            with self:
                self._label = Text(text)
        else:
            self._label.set_text(text)
        self._style_label()

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the button."""
        if enabled:
            self._props.pop('disabled', None)
        else:
            self._props['disabled'] = True
        self.update()


def button(text: str = '', **kwargs: Any) -> Button:
    """Create a :class:`Button`. Shorthand for ``Button(text, **kwargs)``."""
    return Button(text, **kwargs)

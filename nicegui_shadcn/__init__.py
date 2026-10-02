"""shadcn/ui for NiceGUI.

A component library that ports the `shadcn/ui <https://ui.shadcn.com>`_ look and
vocabulary to NiceGUI, using NiceGUI's documented
`"Using other Vue UI frameworks"
<https://nicegui.io/documentation/section_styling_appearance#using_other_vue_ui_frameworks>`_
extension mechanism.

Usage
-----
Importing the package is enough -- it registers the compiled stylesheet, the
``reka-ui`` ESM bundle and the import-map entry that connects them::

    from nicegui import ui
    from nicegui_shadcn import shadcn

    with shadcn.card():
        with shadcn.card_header():
            shadcn.card_title('Create project')
            shadcn.card_description('Deploy your new project in one click.')
        with shadcn.card_content():
            shadcn.input(placeholder='Name')
            shadcn.button('Deploy')

Every component is a subclass of :class:`nicegui.element.Element`, so the whole
NiceGUI toolbox (``bind_value``, ``on``, ``tooltip``, ``classes``, slots,
``move``, ...) keeps working. The additional ``classes=`` keyword behaves like
shadcn's ``cn()``: it is merged with the component's own utilities through
:mod:`nicegui_shadcn._tw_merge`, so the caller's classes win instead of being
appended and resolved by stylesheet order.

Dark mode
---------
The Tailwind ``dark:`` variant is bound to ``body.body--dark``, the class that
NiceGUI's own :func:`nicegui.ui.dark_mode` toggles. Use it as usual.

Theming
-------
The design tokens are plain CSS custom properties, so they can be replaced at
runtime instead of being frozen into the compiled stylesheet::

    from nicegui_shadcn import theming

    theming.use_base_color('zinc')
    theming.set_radius(0.75)
    theming.set_colors(primary='#2563eb')

See :mod:`nicegui_shadcn.theming` for the full API.
"""

from __future__ import annotations

from . import icons, shadcn, theme, theming
from .elements import *  # noqa: F401,F403
from .elements import __all__ as _elements_all

__version__ = '0.1.4'

__all__ = ['__version__', 'icons', 'shadcn', 'theme', 'theming', *_elements_all]

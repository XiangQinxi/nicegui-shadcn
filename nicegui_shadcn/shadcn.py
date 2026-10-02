"""The component namespace.

Exists so that both spellings work and read well::

    import nicegui_shadcn as shadcn
    from nicegui_shadcn import shadcn

``shadcn.button(...)``, ``shadcn.card()``, ``shadcn.table_cell(...)`` and the
rest are re-exported from :mod:`nicegui_shadcn.elements`.
"""

from . import icons, theme
from .elements import *  # noqa: F401,F403
from .elements import __all__ as _elements_all

__all__ = ['icons', 'theme', *_elements_all]

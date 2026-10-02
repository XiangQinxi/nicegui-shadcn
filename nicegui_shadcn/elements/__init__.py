"""NiceGUI elements implementing the shadcn/ui component vocabulary."""

from . import (
    base,
    shadcn_accordion,
    shadcn_button,
    shadcn_controls,
    shadcn_display,
    shadcn_form,
    shadcn_layout,
    shadcn_overlay,
    shadcn_select,
    shadcn_tabs,
)
from . import icon as _icon

# The ``__all__`` lists have to be collected *before* the star imports below:
# ``from .icon import *`` rebinds the module-level name ``icon`` to the icon
# factory function, which would then shadow the module.
__all__ = [
    *base.__all__,
    *_icon.__all__,
    *shadcn_accordion.__all__,
    *shadcn_button.__all__,
    *shadcn_controls.__all__,
    *shadcn_display.__all__,
    *shadcn_form.__all__,
    *shadcn_layout.__all__,
    *shadcn_overlay.__all__,
    *shadcn_select.__all__,
    *shadcn_tabs.__all__,
]

from .base import *  # noqa: E402,F401,F403
from .icon import *  # noqa: E402,F401,F403
from .shadcn_accordion import *  # noqa: E402,F401,F403
from .shadcn_button import *  # noqa: E402,F401,F403
from .shadcn_controls import *  # noqa: E402,F401,F403
from .shadcn_display import *  # noqa: E402,F401,F403
from .shadcn_form import *  # noqa: E402,F401,F403
from .shadcn_layout import *  # noqa: E402,F401,F403
from .shadcn_overlay import *  # noqa: E402,F401,F403
from .shadcn_select import *  # noqa: E402,F401,F403
from .shadcn_tabs import *  # noqa: E402,F401,F403

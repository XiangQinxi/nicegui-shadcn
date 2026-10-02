"""NiceGUI elements implementing the shadcn/ui component vocabulary."""

from . import (
    base,
    shadcn_accordion,
    shadcn_alert_dialog,
    shadcn_breadcrumb,
    shadcn_button,
    shadcn_button_group,
    shadcn_calendar,
    shadcn_collapsible,
    shadcn_combobox,
    shadcn_command,
    shadcn_content,
    shadcn_controls,
    shadcn_date_picker,
    shadcn_direction,
    shadcn_display,
    shadcn_drawer,
    shadcn_form,
    shadcn_hover_card,
    shadcn_input_otp,
    shadcn_item,
    shadcn_layout,
    shadcn_menubar,
    shadcn_menus,
    shadcn_native_select,
    shadcn_navigation_menu,
    shadcn_overlay,
    shadcn_pagination,
    shadcn_scroll_area,
    shadcn_select,
    shadcn_sheet,
    shadcn_tabs,
    shadcn_toast,
    shadcn_typography,
)
from . import icon as _icon

# The ``__all__`` lists have to be collected *before* the star imports below:
# ``from .icon import *`` rebinds the module-level name ``icon`` to the icon
# factory function, which would then shadow the module.
__all__ = [
    *base.__all__,
    *_icon.__all__,
    *shadcn_accordion.__all__,
    *shadcn_alert_dialog.__all__,
    *shadcn_breadcrumb.__all__,
    *shadcn_button.__all__,
    *shadcn_button_group.__all__,
    *shadcn_calendar.__all__,
    *shadcn_collapsible.__all__,
    *shadcn_combobox.__all__,
    *shadcn_command.__all__,
    *shadcn_content.__all__,
    *shadcn_controls.__all__,
    *shadcn_date_picker.__all__,
    *shadcn_direction.__all__,
    *shadcn_display.__all__,
    *shadcn_drawer.__all__,
    *shadcn_form.__all__,
    *shadcn_hover_card.__all__,
    *shadcn_input_otp.__all__,
    *shadcn_item.__all__,
    *shadcn_layout.__all__,
    *shadcn_menubar.__all__,
    *shadcn_menus.__all__,
    *shadcn_native_select.__all__,
    *shadcn_navigation_menu.__all__,
    *shadcn_overlay.__all__,
    *shadcn_pagination.__all__,
    *shadcn_scroll_area.__all__,
    *shadcn_select.__all__,
    *shadcn_sheet.__all__,
    *shadcn_tabs.__all__,
    *shadcn_toast.__all__,
    *shadcn_typography.__all__,
]

from .base import *  # noqa: E402,F401,F403
from .icon import *  # noqa: E402,F401,F403
from .shadcn_accordion import *  # noqa: E402,F401,F403
from .shadcn_alert_dialog import *  # noqa: E402,F401,F403
from .shadcn_breadcrumb import *  # noqa: E402,F401,F403
from .shadcn_button import *  # noqa: E402,F401,F403
from .shadcn_button_group import *  # noqa: E402,F401,F403
from .shadcn_calendar import *  # noqa: E402,F401,F403
from .shadcn_collapsible import *  # noqa: E402,F401,F403
from .shadcn_combobox import *  # noqa: E402,F401,F403
from .shadcn_command import *  # noqa: E402,F401,F403
from .shadcn_content import *  # noqa: E402,F401,F403
from .shadcn_controls import *  # noqa: E402,F401,F403
from .shadcn_date_picker import *  # noqa: E402,F401,F403
from .shadcn_direction import *  # noqa: E402,F401,F403
from .shadcn_display import *  # noqa: E402,F401,F403
from .shadcn_drawer import *  # noqa: E402,F401,F403
from .shadcn_form import *  # noqa: E402,F401,F403
from .shadcn_hover_card import *  # noqa: E402,F401,F403
from .shadcn_input_otp import *  # noqa: E402,F401,F403
from .shadcn_item import *  # noqa: E402,F401,F403
from .shadcn_layout import *  # noqa: E402,F401,F403
from .shadcn_menubar import *  # noqa: E402,F401,F403
from .shadcn_menus import *  # noqa: E402,F401,F403
from .shadcn_native_select import *  # noqa: E402,F401,F403
from .shadcn_navigation_menu import *  # noqa: E402,F401,F403
from .shadcn_overlay import *  # noqa: E402,F401,F403
from .shadcn_pagination import *  # noqa: E402,F401,F403
from .shadcn_scroll_area import *  # noqa: E402,F401,F403
from .shadcn_select import *  # noqa: E402,F401,F403
from .shadcn_sheet import *  # noqa: E402,F401,F403
from .shadcn_tabs import *  # noqa: E402,F401,F403
from .shadcn_toast import *  # noqa: E402,F401,F403
from .shadcn_typography import *  # noqa: E402,F401,F403

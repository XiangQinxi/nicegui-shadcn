"""Showcase of the nicegui-shadcn component library.

Run it with::

    python examples/demo.py

then open http://localhost:8080.
"""

from dataclasses import dataclass
import sys
from pathlib import Path

if __package__ in {None, ''}:  # allow ``python examples/demo.py`` from the repo root
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from nicegui import ui

from nicegui_shadcn import shadcn

ui.add_head_html('<style>body { background: var(--muted); }</style>', shared=True)


@dataclass
class Form:
    name: str = 'my-project'
    description: str = ''
    terms: bool = True
    notifications: bool = False


@ui.page('/')
def main() -> None:
    dark = ui.dark_mode()
    form = Form()

    with ui.column().classes('mx-auto w-full max-w-3xl items-stretch gap-8 p-10'):
        with ui.row().classes('w-full items-center justify-between'):
            with ui.column().classes('gap-1'):
                shadcn.card_title('nicegui-shadcn')
                shadcn.card_description('shadcn/ui components for NiceGUI, no build step required.')
            shadcn.button('Dark mode', variant='outline', icon='moon',
                          on_click=lambda: dark.toggle())

        # --- buttons ------------------------------------------------------- #
        with shadcn.card():
            with shadcn.card_header():
                shadcn.card_title('Buttons')
            with shadcn.card_content().classes('grid gap-4'):
                with ui.row().classes('flex-wrap items-center gap-3'):
                    shadcn.button('Default')
                    shadcn.button('Secondary', variant='secondary')
                    shadcn.button('Destructive', variant='destructive')
                    shadcn.button('Outline', variant='outline')
                    shadcn.button('Ghost', variant='ghost')
                    shadcn.button('Link', variant='link')
                with ui.row().classes('flex-wrap items-center gap-3'):
                    shadcn.button('Small', size='sm')
                    shadcn.button('Large', size='lg')
                    shadcn.button('With icon', icon='plus')
                    shadcn.button('Icon only', size='icon', icon='settings')
                    shadcn.button('Disabled', disabled=True)

        # --- form ---------------------------------------------------------- #
        with shadcn.card():
            with shadcn.card_header():
                shadcn.card_title('Form')
                shadcn.card_description('Native NiceGUI value elements — bind_value() works.')
            with shadcn.card_content().classes('grid gap-4'):
                with ui.column().classes('w-full gap-2'):
                    shadcn.label('Project name')
                    shadcn.input(placeholder='my-project').bind_value(form, 'name')
                with ui.column().classes('w-full gap-2'):
                    shadcn.label('Description')
                    shadcn.textarea(placeholder='Tell us more...').bind_value(form, 'description')
                with ui.row().classes('items-center gap-6'):
                    with ui.row().classes('items-center gap-2'):
                        shadcn.checkbox().bind_value(form, 'terms')
                        shadcn.label('Accept terms')
                    with ui.row().classes('items-center gap-2'):
                        shadcn.switch().bind_value(form, 'notifications')
                        shadcn.label('Notifications')
                shadcn.button('Submit', icon='check',
                              on_click=lambda: ui.notify(f'Hello {form.name}!', type='positive'))

        # --- tabs & accordion ---------------------------------------------- #
        with shadcn.card():
            with shadcn.card_header():
                shadcn.card_title('Tabs & Accordion')
                shadcn.card_description('reka-ui disclosure primitives, driven from Python.')
            with shadcn.card_content().classes('grid gap-6'):
                with shadcn.tabs(value='account'):
                    shadcn.tabs_list([
                        ('account', 'Account'),
                        ('password', 'Password'),
                        {'value': 'disabled', 'label': 'Disabled', 'disabled': True},
                    ])
                    with shadcn.tabs_content(value='account'):
                        shadcn.input(value=form.name).bind_value(form, 'name')
                    with shadcn.tabs_content(value='password'):
                        shadcn.input(placeholder='Current password', type='password')
                with shadcn.accordion(value='shipping'):
                    with shadcn.accordion_item(value='shipping'):
                        shadcn.accordion_trigger('How do you ship?')
                        with shadcn.accordion_content():
                            shadcn.label('We ship by carrier pigeon, weather permitting.')
                    with shadcn.accordion_item(value='returns'):
                        shadcn.accordion_trigger('What is your return policy?')
                        with shadcn.accordion_content():
                            shadcn.label('Unopened boxes within 30 days.')

        # --- controls ------------------------------------------------------- #
        with shadcn.card():
            with shadcn.card_header():
                shadcn.card_title('Controls')
                shadcn.card_description('Select, radio group, slider and toggles.')
            with shadcn.card_content().classes('grid gap-4'):
                shadcn.select(
                    [('system', 'System'), ('light', 'Light'), ('dark', 'Dark')],
                    value='system',
                    on_change=lambda e: ui.notify(f'Theme: {e.value}'),
                )
                shadcn.radio_group(
                    [('card', 'Card'), ('paypal', 'PayPal'), ('apple', 'Apple Pay')],
                    value='card',
                )
                shadcn.slider(40, min=0, max=100, step=5)
                with ui.row().classes('items-center gap-2'):
                    shadcn.toggle_group(['left', 'center', 'right'], value='center')
                    shadcn.toggle('Bold', value=True)
                    shadcn.toggle('Italic')

        # --- overlays ------------------------------------------------------- #
        with shadcn.card():
            with shadcn.card_header():
                shadcn.card_title('Overlays')
                shadcn.card_description('Dialog, popover, dropdown menu and tooltip.')
            with shadcn.card_content().classes('flex flex-wrap items-center gap-3'):
                with shadcn.dialog() as profile_dialog:
                    shadcn.dialog_trigger('Edit profile')
                    with shadcn.dialog_content(title='Edit profile',
                                               description='Changes are saved locally.'):
                        with ui.column().classes('w-full gap-2'):
                            shadcn.label('Display name')
                            shadcn.input(value=form.name).bind_value(form, 'name')
                        with shadcn.dialog_footer():
                            shadcn.button('Cancel', variant='outline',
                                          on_click=profile_dialog.close)
                            shadcn.button('Save', icon='check',
                                          on_click=lambda: (ui.notify(f'Saved {form.name}'),
                                                            profile_dialog.close()))
                with shadcn.popover() as popover:
                    shadcn.popover_trigger('Open popover')
                    with shadcn.popover_content():
                        with ui.column().classes('gap-1'):
                            shadcn.card_title('Dimensions')
                            shadcn.card_description('Set the layout dimensions.')
                with shadcn.dropdown_menu(
                    [{'kind': 'label', 'label': 'My account'},
                     {'value': 'profile', 'label': 'Profile'},
                     {'value': 'settings', 'label': 'Settings'},
                     {'kind': 'separator'},
                     {'value': 'logout', 'label': 'Log out', 'variant': 'destructive'}],
                    on_select=lambda e: ui.notify(f'Menu: {e.args}'),
                ):
                    shadcn.button('Open menu', variant='outline', icon='ellipsis')
                with shadcn.tooltip('Add to library'):
                    shadcn.button('Hover me', variant='outline', icon='plus')

        # --- display ------------------------------------------------------- #
        with shadcn.card():
            with shadcn.card_header():
                shadcn.card_title('Display')
                shadcn.card_description('Badges, alerts, progress and avatars.')
            with shadcn.card_content().classes('grid gap-4'):
                with ui.row().classes('items-center gap-2'):
                    shadcn.badge('Default')
                    shadcn.badge('Secondary', variant='secondary')
                    shadcn.badge('Destructive', variant='destructive')
                    shadcn.badge('Outline', variant='outline')
                shadcn.alert(
                    title='Heads up!',
                    description='You can add components to your app using the CLI.',
                )
                shadcn.alert(
                    variant='destructive',
                    title='Error',
                    description='Your session has expired. Please log in again.',
                )
                shadcn.progress(62)
                with ui.row().classes('items-center gap-3'):
                    shadcn.avatar(fallback='CN')
                    shadcn.avatar(fallback='AB', size='lg')
                    shadcn.skeleton().classes('size-10 rounded-full')
                shadcn.separator()
                with ui.row().classes('items-center gap-2 text-sm text-muted-foreground'):
                    shadcn.icon('info')
                    shadcn.label('Rendered with NiceGUI + Tailwind CSS v4 + reka-ui.')

        # --- table --------------------------------------------------------- #
        with shadcn.card():
            with shadcn.card_header():
                shadcn.card_title('Table')
            with shadcn.card_content():
                with shadcn.table_container():
                    with shadcn.table():
                        with shadcn.table_header():
                            with shadcn.table_row():
                                shadcn.table_head('Invoice')
                                shadcn.table_head('Status')
                                shadcn.table_head('Amount').classes('text-right')
                        with shadcn.table_body():
                            for invoice, status, variant, amount in [
                                ('INV-001', 'Paid', 'secondary', '$250.00'),
                                ('INV-002', 'Pending', 'outline', '$150.00'),
                                ('INV-003', 'Overdue', 'destructive', '$350.00'),
                            ]:
                                with shadcn.table_row():
                                    shadcn.table_cell(invoice).classes('font-medium')
                                    with shadcn.table_cell():
                                        shadcn.badge(status, variant=variant)
                                    shadcn.table_cell(amount).classes('text-right')


if __name__ in {'__main__', '__mp_main__'}:
    import os

    ui.run(title='nicegui-shadcn', reload=False, show=False,
           port=int(os.environ.get('SHADCN_DEMO_PORT', '8080')))

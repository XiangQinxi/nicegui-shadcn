"""Showcase of the nicegui-shadcn component library.

Run it with::

    python examples/demo.py

then open http://localhost:8080.
"""

from dataclasses import dataclass
from datetime import date
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
    events: list[str] = []
    probe_log = None

    def probe(event: str) -> None:
        """Record a client event so ``tests/visual_check.mjs`` can read it back."""
        events.append(event)
        if probe_log is not None:
            probe_log.set_text(' | '.join(events[-8:]))

    with ui.column().classes('mx-auto w-full max-w-3xl items-stretch gap-8 p-10'):
        with ui.row().classes('w-full items-center justify-between'):
            with ui.column().classes('gap-1'):
                shadcn.card_title('nicegui-shadcn')
                shadcn.card_description('shadcn/ui components for NiceGUI, no build step required.')
            shadcn.button('Dark mode', variant='outline', icon='moon',
                          on_click=lambda: dark.toggle())

        # Every interactive component below appends to this line, which is how the
        # headless check proves an event really travelled back to the server.
        with ui.row().classes('items-center gap-2'):
            shadcn.icon('info').classes('text-muted-foreground')
            shadcn.small('Events').classes('text-muted-foreground')
            probe_log = shadcn.muted('(none yet)').props('id=probe-log')

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
                with shadcn.popover():
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

        # --- button group, kbd & markers ------------------------------------ #
        with shadcn.card():
            with shadcn.card_header():
                shadcn.card_title('Button Group, Kbd & Markers')
                shadcn.card_description('Segmented controls, shortcut hints and status dots.')
            with shadcn.card_content().classes('grid gap-4'):
                with ui.row().classes('flex-wrap items-center gap-3'):
                    with shadcn.button_group():
                        shadcn.button('Day', variant='outline',
                                      on_click=lambda: probe('group:day'))
                        shadcn.button('Week', variant='outline',
                                      on_click=lambda: probe('group:week'))
                        shadcn.button('Month', variant='outline',
                                      on_click=lambda: probe('group:month'))
                    with shadcn.button_group():
                        shadcn.button_group_text('Zoom')
                        shadcn.button_group_separator()
                        shadcn.button('Fit', variant='outline', size='sm',
                                      on_click=lambda: probe('group:fit'))
                with ui.row().classes('flex-wrap items-center gap-3'):
                    shadcn.kbd('Ctrl')
                    shadcn.kbd('K')
                    shadcn.spinner()
                    shadcn.spinner(size=24, label='Saving')
                with ui.row().classes('flex-wrap items-center gap-4'):
                    shadcn.marker('Default')
                    shadcn.marker('Success', variant='success')
                    shadcn.marker('Warning', variant='warning')
                    shadcn.marker('Error', variant='error')
                    shadcn.marker('Live', variant='info', pulse=True)

        # --- typography ----------------------------------------------------- #
        with shadcn.card():
            with shadcn.card_header():
                shadcn.card_title('Typography')
                shadcn.card_description('Headings, prose, lists and inline code.')
            with shadcn.card_content().classes('grid gap-1'):
                shadcn.h1('Heading one')
                shadcn.h2('Heading two')
                shadcn.h3('Heading three')
                shadcn.h4('Heading four')
                shadcn.lead('A lead paragraph introduces the section below it.')
                shadcn.paragraph('Drop any component into a NiceGUI layout and it picks '
                                 'up the theme, the radius ladder and the dark mode for free.')
                shadcn.large('Large and semibold, for emphasis.')
                shadcn.small('Small print, also semibold.')
                shadcn.muted('Muted supporting copy.')
                shadcn.blockquote('Every CSS class string lives in Python.')
                with shadcn.bullet_list():
                    for entry in ['Copy a component from the registry.',
                                  'Import it from nicegui_shadcn.',
                                  'Compose it like any other NiceGUI element.']:
                        with ui.element('li'):
                            shadcn.label(entry)
                with ui.row().classes('items-center gap-2'):
                    shadcn.muted('Import with')
                    shadcn.inline_code('from nicegui_shadcn import shadcn')

        # --- content & empty states ----------------------------------------- #
        with shadcn.card():
            with shadcn.card_header():
                shadcn.card_title('Content, Scroll Area & Direction')
                shadcn.card_description('Aspect ratio, an empty state, a scroll region and RTL.')
            with shadcn.card_content().classes('grid gap-6'):
                with shadcn.aspect_ratio(16 / 9).classes('w-full max-w-sm'):
                    ui.element('div').classes('size-full rounded-lg bg-muted')
                with shadcn.empty():
                    with shadcn.empty_header():
                        with shadcn.empty_media(variant='icon'):
                            shadcn.icon('mail')
                        shadcn.empty_title('No projects yet')
                        shadcn.empty_description('Create your first project to get started.')
                    with shadcn.empty_content():
                        shadcn.button('Create project', icon='plus',
                                      on_click=lambda: probe('empty:create'))
                with shadcn.scroll_area().classes('h-40 w-full rounded-md border'):
                    with ui.column().classes('w-full gap-2 p-4'):
                        for release in range(1, 13):
                            shadcn.small(f'Release {release}.0.0')
                with shadcn.direction('rtl').props('id=direction-block'):
                    shadcn.muted('يُعرض هذا النص من اليمين إلى اليسار.')

        # --- item ----------------------------------------------------------- #
        with shadcn.card():
            with shadcn.card_header():
                shadcn.card_title('Item')
                shadcn.card_description('A media object with actions, header and footer slots.')
            with shadcn.card_content():
                with shadcn.item_group():
                    with shadcn.item(variant='outline'):
                        with shadcn.item_media(variant='icon'):
                            shadcn.icon('copy')
                        with shadcn.item_content():
                            shadcn.item_title('Design system')
                            shadcn.item_description('Last edited two hours ago')
                        with shadcn.item_actions():
                            shadcn.button('Open', variant='outline', size='sm',
                                          on_click=lambda: probe('item:open'))
                    shadcn.item_separator()
                    with shadcn.item(variant='muted', size='sm'):
                        with shadcn.item_media(variant='icon'):
                            shadcn.icon('circle-check')
                        with shadcn.item_content():
                            shadcn.item_title('Password vault')
                            shadcn.item_description('Synced with your team')
                        with shadcn.item_footer():
                            shadcn.badge('Private', variant='secondary')
                            shadcn.small('Updated just now')

        # --- breadcrumb, native select & pagination -------------------------- #
        with shadcn.card():
            with shadcn.card_header():
                shadcn.card_title('Breadcrumb, Native Select & Pagination')
                shadcn.card_description('A trail of links, a real <select> and a pager.')
            with shadcn.card_content().classes('grid gap-6'):
                with shadcn.breadcrumb():
                    with shadcn.breadcrumb_list():
                        with shadcn.breadcrumb_item():
                            shadcn.breadcrumb_link('Home')
                        shadcn.breadcrumb_separator()
                        with shadcn.breadcrumb_item():
                            shadcn.breadcrumb_link('Components')
                        shadcn.breadcrumb_separator()
                        with shadcn.breadcrumb_item():
                            shadcn.breadcrumb_ellipsis()
                        shadcn.breadcrumb_separator()
                        with shadcn.breadcrumb_item():
                            shadcn.breadcrumb_page('Breadcrumb')
                shadcn.native_select(
                    [('starter', 'Starter'), ('growth', 'Growth'), ('scale', 'Scale')],
                    value='growth',
                    on_change=lambda e: probe(f'native:{e.value}'),
                )
                shadcn.pagination(page=3, total=12,
                                  on_change=lambda e: probe(f'page:{e.value}'))

        # --- collapsible & hover card ---------------------------------------- #
        with shadcn.card():
            with shadcn.card_header():
                shadcn.card_title('Collapsible & Hover Card')
                shadcn.card_description('An inline disclosure and a hover preview.')
            with shadcn.card_content().classes('grid gap-6'):
                with shadcn.collapsible(on_change=lambda e: probe(f'collapsible:{e.value}')):
                    shadcn.collapsible_trigger('Can I use this in production?')
                    with shadcn.collapsible_content():
                        shadcn.muted('Yes — the compiled assets are committed, so there is no build step.')
                with shadcn.hover_card():
                    with shadcn.hover_card_trigger():
                        shadcn.button('@nicegui', variant='link')
                    with shadcn.hover_card_content():
                        with ui.column().classes('gap-1'):
                            shadcn.large('NiceGUI')
                            shadcn.muted('Build web interfaces with Python.')

        # --- sheet & drawer --------------------------------------------------- #
        with shadcn.card():
            with shadcn.card_header():
                shadcn.card_title('Sheet & Drawer')
                shadcn.card_description('A side panel and a swipeable bottom drawer.')
            with shadcn.card_content().classes('flex flex-wrap items-center gap-3'):
                with shadcn.sheet(on_change=lambda e: probe(f'sheet:{e.value}')):
                    shadcn.sheet_trigger('Open sheet')
                    with shadcn.sheet_content(title='Edit settings',
                                              description='Changes apply immediately.',
                                              side='right'):
                        shadcn.input(placeholder='Workspace name').classes('w-full')
                        with shadcn.sheet_footer():
                            shadcn.button('Save', icon='check',
                                          on_click=lambda: probe('sheet:save'))
                with shadcn.drawer(on_change=lambda e: probe(f'drawer:{e.value}')):
                    shadcn.drawer_trigger('Open drawer')
                    with shadcn.drawer_content(title='Quick actions',
                                               description='Pick an action to run.'):
                        shadcn.muted('The drawer slides in from the bottom edge.')
                        with shadcn.drawer_footer():
                            shadcn.button('Run', icon='arrow-right',
                                          on_click=lambda: probe('drawer:run'))

        # --- alert dialog, context menu & toast ------------------------------- #
        with shadcn.card():
            with shadcn.card_header():
                shadcn.card_title('Alert Dialog, Context Menu & Toast')
                shadcn.card_description('A modal decision, a right-click menu and a notification.')
            with shadcn.card_content().classes('grid gap-6'):
                with shadcn.alert_dialog():
                    shadcn.alert_dialog_trigger('Delete project')
                    with shadcn.alert_dialog_content(title='Delete project?',
                                                     description='This action cannot be undone.'):
                        with shadcn.alert_dialog_footer():
                            shadcn.alert_dialog_cancel('Cancel')
                            shadcn.alert_dialog_action('Delete',
                                                       on_click=lambda: probe('alert:delete'))
                with shadcn.context_menu():
                    shadcn.context_menu_trigger('Right-click this panel')
                    shadcn.context_menu_content(
                        [{'value': 'copy', 'label': 'Copy'},
                         {'value': 'cut', 'label': 'Cut'},
                         {'kind': 'separator'},
                         {'value': 'delete', 'label': 'Delete', 'variant': 'destructive'}],
                        on_select=lambda e: probe(f'context:{e.args}'),
                    )
                with shadcn.toast_provider(position='bottom-right'):
                    with ui.row().classes('items-center gap-3'):
                        saved_toast = shadcn.toast('Deployment queued',
                                                   description='We will email you when it is live.',
                                                   duration=60000)

                        def show_toast() -> None:
                            probe('toast:open')
                            saved_toast.open()

                        shadcn.button('Show toast', variant='outline', on_click=show_toast)

        # --- pickers ---------------------------------------------------------- #
        with shadcn.card():
            with shadcn.card_header():
                shadcn.card_title('Calendar, Date Picker & Input OTP')
                shadcn.card_description('Two date inputs and a segmented one-time code.')
            with shadcn.card_content().classes('grid gap-6'):
                shadcn.calendar(date(2026, 3, 15),
                                on_change=lambda e: probe(f'calendar:{e.value}'))
                shadcn.date_picker(date(2026, 3, 15),
                                   on_date_change=lambda e: probe(f'date:{e.value}'))
                shadcn.input_otp('123456', length=6, groups=[3, 3],
                                 pattern=shadcn.REGEXP_ONLY_DIGITS,
                                 on_change=lambda e: probe(f'otp:{e.value}'))

        # --- command & combobox ------------------------------------------------ #
        with shadcn.card():
            with shadcn.card_header():
                shadcn.card_title('Command & Combobox')
                shadcn.card_description('A searchable command palette and a filterable picker.')
            with shadcn.card_content().classes('grid gap-6'):
                shadcn.command(
                    [{'value': 'calendar', 'label': 'Calendar', 'group': 'Suggestions'},
                     {'value': 'search', 'label': 'Search', 'group': 'Suggestions', 'shortcut': '⌘K'},
                     {'kind': 'separator'},
                     {'value': 'profile', 'label': 'Profile', 'group': 'Settings'},
                     {'value': 'billing', 'label': 'Billing', 'group': 'Settings', 'disabled': True}],
                    on_select=lambda e: probe(f'command:{e.args}'),
                )
                shadcn.combobox(
                    [('next', 'Next.js'), ('svelte', 'SvelteKit'), ('nuxt', 'Nuxt.js')],
                    value='next',
                    on_change=lambda e: probe(f'combobox:{e.value}'),
                )

        # --- menubar & navigation menu ------------------------------------------ #
        with shadcn.card():
            with shadcn.card_header():
                shadcn.card_title('Menubar & Navigation Menu')
                shadcn.card_description('An application menu bar and a hover navigation bar.')
            with shadcn.card_content().classes('grid gap-6'):
                shadcn.menubar(
                    {'File': [{'value': 'new', 'label': 'New'},
                              {'value': 'open', 'label': 'Open'},
                              {'kind': 'separator'},
                              {'value': 'quit', 'label': 'Quit'}],
                     'Edit': [{'value': 'undo', 'label': 'Undo'},
                              {'value': 'redo', 'label': 'Redo', 'disabled': True}]},
                    on_select=lambda e: probe(f'menubar:{e.args}'),
                )
                shadcn.navigation_menu(
                    [{'label': 'Getting started',
                      'items': [{'label': 'Introduction', 'href': '/docs',
                                 'description': 'How the library works.'},
                                {'label': 'Installation', 'href': '/docs/install',
                                 'description': 'Add the package to your project.'}]},
                     {'label': 'Components', 'href': '/components'}],
                    on_select=lambda e: probe(f'nav:{e.args}'),
                )


if __name__ in {'__main__', '__mp_main__'}:
    import os

    ui.run(title='nicegui-shadcn', reload=False, show=False,
           port=int(os.environ.get('SHADCN_DEMO_PORT', '8080')))

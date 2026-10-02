# nicegui-shadcn

**English** · [简体中文](README_zh.md)

[shadcn/ui](https://ui.shadcn.com) components for [NiceGUI](https://nicegui.io), built on
NiceGUI's documented
[“Using other Vue UI frameworks”](https://nicegui.io/documentation/section_styling_appearance#using_other_vue_ui_frameworks)
extension mechanism. No build step is required to *use* it: the stylesheet and the
`reka-ui` bundle ship pre-compiled inside the package.

```python
from nicegui import ui
from nicegui_shadcn import shadcn

with shadcn.card():
    with shadcn.card_header():
        shadcn.card_title('Create project')
        shadcn.card_description('Deploy your new project in one click.')
    with shadcn.card_content():
        shadcn.input(placeholder='Name')
        shadcn.button('Deploy', on_click=lambda: ui.notify('Deployed'))

ui.run()
```

![the demo app](docs/demo-light.png)

<sub>Light and dark are both driven by `body.body--dark`, i.e. by `ui.dark_mode()`.</sub>

![the demo app in dark mode](docs/demo-dark.png)

`python examples/demo.py` renders every component; it is what the screenshots above and
`tests/visual_check.mjs` use. `python examples/login.py` is a smaller, real-world page: a
sign-in card with a show/hide password toggle.

## Contents

- [Install](#install)
- [How it works](#how-it-works)
- [Usage](#usage)
  - [The `classes=` keyword](#the-classes-keyword)
  - [Layout](#layout)
  - [Forms](#forms)
  - [Display](#display)
  - [Disclosure](#disclosure)
  - [Overlays](#overlays)
  - [Menus, commands and feedback](#menus-commands-and-feedback)
  - [Icons](#icons)
- [Dark mode](#dark-mode)
- [Theme](#theme)
- [Keyword arguments from NiceGUI](#keyword-arguments-from-nicegui)
- [Component reference](#component-reference)
- [Documentation](#documentation)
- [Development](#development)
- [Extending the stylesheet](#extending-the-stylesheet)
- [Packaging and publishing](#packaging-and-publishing)
- [Design notes and limitations](#design-notes-and-limitations)

## Install

```bash
pip install nicegui-shadcn        # from PyPI (pulls in nicegui>=3.0)
pip install -e .                  # or, from a checkout of this repository
```

Importing `nicegui_shadcn` registers everything that has to be on the page before the
first component renders:

- the stylesheet is served at `/_nicegui_shadcn/shadcn.css` and linked from the page head;
- the `reka-ui` ESM bundle is served from the same prefix and installed on the import map
  as the bare specifier `reka-ui`;
- NiceGUI's own Vue 3 build stays the single Vue instance (the bundle keeps `vue`
  external), so `provide`/`inject` and `Teleport` keep working across every component.

Nothing else is registered globally — no Tailwind runtime, no CDN imports.

## How it works

| Piece | What it does |
| --- | --- |
| `nicegui_shadcn/theme.py` | Serves `static/` and adds the `<link>`. Runs on import. |
| `frontend/tailwind.css` | Tailwind v4 source: shadcn design tokens, `@theme inline` exposure, `dark` variant bound to `body.body--dark`. Build input, not shipped in the wheel. |
| `nicegui_shadcn/static/shadcn.css` | The compiled stylesheet (~201 kB). |
| `nicegui_shadcn/static/vendor/reka-ui.js` | The `reka-ui` primitives the library wraps, tree-shaken to ~381 kB. |
| `frontend/vendor/reka-entry.js` | The esbuild entry that produces the bundle above. Build input. |
| `nicegui_shadcn/_tw_merge.py` | A dependency-free port of `tailwind-merge`, i.e. the `cn()` helper. |
| `nicegui_shadcn/elements/*.py` | One class per component: `ShadcnElement` plus NiceGUI's `ValueElement`/`TextElement` mixins. |
| `nicegui_shadcn/elements/*.vue` | Templates for the components that need real behaviour. Parsed by NiceGUI's own `VBuild`, executed as ES modules. |

The Python classes decide the classes, the `.vue` files decide the markup. Every class
string lives in Python so that `classes=` can be merged correctly, and
`tests/audit_classes.py` can verify that each one really exists in the compiled CSS.

## Usage

### The `classes=` keyword

Exactly like shadcn's `cn()`: your classes are merged with the component's own through
`tailwind-merge`, and **yours win**.

```python
shadcn.button('Save')                            # bg-primary text-primary-foreground …
shadcn.button('Save', classes='bg-destructive')  # the red wins, not both
shadcn.button('Save', classes=['w-full', 'mt-4'])
```

NiceGUI's own `.classes(...)` is unchanged and still appends:

```python
btn = shadcn.button('Save')
btn.classes('mt-4')          # appended, no conflict resolution
btn.classes(replace='mt-8')  # NiceGUI's replace still works
```

Appending is a silent trap when the new class collides with one the component already
carries: both utilities end up in the `class` attribute and the stylesheet picks the winner,
which is not necessarily your intent. A `Card` ships `py-6` and the build emits `.p-0`
*before* `.py-6`, so `shadcn.card().classes('p-0')` really does keep 1.5rem of vertical
padding.

`.with_classes(...)` is the merging counterpart, available after construction:

```python
shadcn.card().with_classes('p-0')           # py-6 evicted, p-0 wins
shadcn.card().with_classes('rounded-full')  # rounded-xl evicted
```

It runs through the same `tailwind-merge`, and returns the element so it chains:

```python
card = shadcn.card().with_classes('p-0 mt-4')
```

The stylesheet is pre-compiled, so `classes=` only affects classes that were generated
at build time. The set you can rely on is:

- every class the components themselves use;
- the shadcn semantic colours, plain and with the common variants — `bg-primary`,
  `text-muted-foreground`, `dark:border-input`, `hover:bg-accent`, `data-[state=open]:bg-accent`, …;
- a curated layout / spacing / typography vocabulary — `w-full`, `mt-4`, `px-8`, `gap-3`,
  `text-center`, `rounded-full`, `shadow-lg`, `grid-cols-3`, …

Anything outside that — an arbitrary Tailwind utility, or a raw palette colour such as
`bg-blue-600` — has to be generated by a rebuild:
[Extending the stylesheet](#extending-the-stylesheet).

### Layout

```python
with shadcn.card():
    with shadcn.card_header():
        shadcn.card_title('Title')
        shadcn.card_description('Description')
    with shadcn.card_content():
        ...
    with shadcn.card_footer():
        shadcn.button('Cancel', variant='outline')
        shadcn.button('Save')

shadcn.separator()
shadcn.separator(orientation='vertical')
shadcn.skeleton(width='8rem', height='1rem')
```

Tables are the usual shadcn family:

```python
with shadcn.table_container():
    with shadcn.table():
        with shadcn.table_header():
            with shadcn.table_row():
                shadcn.table_head('Invoice')
                shadcn.table_head('Status')
        with shadcn.table_body():
            with shadcn.table_row():
                shadcn.table_cell('INV-001')
                shadcn.table_cell('Paid')
```

### Forms

Every form control is a NiceGUI `ValueElement`, so `bind_value`, `on_value_change` and
`ui.bind` all work.

```python
name = shadcn.input(placeholder='Project name')
shadcn.textarea(placeholder='Description', rows=4)
terms = shadcn.checkbox(value=True)
shadcn.label('Accept terms', for_=terms)
notify = shadcn.switch()
shadcn.label('Notifications', for_=notify)
shadcn.label('Project name', for_=name)

shadcn.select({'system': 'System', 'light': 'Light', 'dark': 'Dark'}, value='system')
shadcn.radio_group([('card', 'Card'), ('paypal', 'PayPal')], value='card')
shadcn.slider(40, min=0, max=100, step=5)
shadcn.toggle('Bold', value=True)
shadcn.toggle_group(['left', 'center', 'right'], value='center', multiple=False)
```

The pickers, the one-time-password field and the combobox are form controls as well:

```python
shadcn.native_select({'system': 'System', 'light': 'Light'}, value='system')
shadcn.combobox({'next': 'Next.js', 'svelte': 'SvelteKit'}, value='next')
shadcn.input_otp(length=6, groups=[3, 3])              # masked, pattern and inputmode too

shadcn.calendar(value='2026-03-15', week_starts_on=1)  # ISO date in, ISO date out
shadcn.date_picker(value='2026-03-15', min_value='2026-03-01')
```

`bind_value` between a shadcn control and a normal NiceGUI element is the point of the
whole exercise:

```python
@dataclass
class Form:
    name: str = ''

form = Form()
shadcn.input().bind_value(form, 'name')
ui.label().bind_text_from(form, 'name')
```

### Display

```python
shadcn.badge('Default')
shadcn.badge('Secondary', variant='secondary')
shadcn.badge('Overdue', variant='destructive')

shadcn.avatar(src='/photo.png', fallback='CN')
shadcn.alert(title='Heads up!', description='You can add components using the CLI.')
shadcn.alert(title='Error', description='Your session has expired.', variant='destructive')

progress = shadcn.progress(60)
progress.set_value(80)
```

The rest of the display family — item rows, empty states, breadcrumbs and typography:

```python
with shadcn.item():
    with shadcn.item_media(variant='icon'):
        shadcn.icon('check', size=16)
    with shadcn.item_content():
        shadcn.item_title('Deployment ready')
        shadcn.item_description('Your project is live.')
    with shadcn.item_actions():
        shadcn.badge('New')

with shadcn.empty():
    with shadcn.empty_header():
        with shadcn.empty_media(variant='icon'):
            shadcn.icon('info')
        shadcn.empty_title('No results')
        shadcn.empty_description('Try a different search.')

shadcn.spinner(size=20)
shadcn.kbd('Ctrl')
shadcn.marker('New', variant='success')
shadcn.aspect_ratio(16 / 9)
shadcn.pagination(page=2, total=5)

shadcn.h1('Installation')
shadcn.paragraph('Then restart the server.')

with shadcn.breadcrumb():
    with shadcn.breadcrumb_list():
        with shadcn.breadcrumb_item():
            shadcn.breadcrumb_link('Home')
        shadcn.breadcrumb_separator()
        with shadcn.breadcrumb_item():
            shadcn.breadcrumb_page('Components')
```

### Disclosure

Tabs take their labels as data, because reka-ui's roving-focus context does not survive
being routed through a NiceGUI slot; the tab *panels* are ordinary NiceGUI children.

```python
with shadcn.tabs(value='account'):
    shadcn.tabs_list([('account', 'Account'),
                      ('password', 'Password'),
                      {'value': 'disabled', 'label': 'Disabled', 'disabled': True}])
    with shadcn.tabs_content(value='account'):
        shadcn.input(value='Ada Lovelace')
    with shadcn.tabs_content(value='password'):
        shadcn.input(placeholder='Current password', type='password')

with shadcn.accordion(value='shipping'):
    with shadcn.accordion_item(value='shipping'):
        shadcn.accordion_trigger('How do you ship?')
        with shadcn.accordion_content():
            ui.label('By carrier pigeon.')
    with shadcn.accordion_item(value='returns'):
        shadcn.accordion_trigger('What is your return policy?')
        with shadcn.accordion_content():
            ui.label('30 days.')
```

### Overlays

```python
with shadcn.dialog() as dialog:
    shadcn.dialog_trigger('Edit profile')          # renders as an outline button
    with shadcn.dialog_content(title='Edit profile',
                               description='Changes are saved locally.'):
        shadcn.input(value='Ada Lovelace')
        with shadcn.dialog_footer():
            shadcn.button('Cancel', variant='outline', on_click=dialog.close)
            shadcn.button('Save', on_click=lambda: (ui.notify('Saved'), dialog.close()))

dialog.open()      # also close() and toggle()

with shadcn.popover():
    shadcn.popover_trigger('Open popover')
    with shadcn.popover_content():
        ui.label('Anything NiceGUI can render.')

shadcn.dropdown_menu([
    {'kind': 'label', 'label': 'My account'},
    {'value': 'profile', 'label': 'Profile'},
    {'kind': 'separator'},
    {'value': 'logout', 'label': 'Log out', 'variant': 'destructive'},
], on_select=lambda e: ui.notify(str(e.args)))

with shadcn.tooltip('Add to library', side='top'):
    shadcn.button('Hover me', variant='outline')
```

`popover_trigger()` and `dialog_trigger()` always render as outline buttons; they take no
`variant` or `size` (`shadcn_overlay.py:76`, `shadcn_overlay.py:169`).

`DialogContent(side=...)` also accepts `'right'`, `'left'`, `'top'` and `'bottom'` for
sheet-style panels.

### Menus, commands and feedback

The remaining overlay family — menu bars, context menus, hover cards, the navigation menu,
the command palette and toasts:

```python
with shadcn.alert_dialog() as confirm:
    shadcn.alert_dialog_trigger('Delete project')
    with shadcn.alert_dialog_content(title='Are you absolutely sure?',
                                     description='This action cannot be undone.'):
        with shadcn.alert_dialog_footer():
            shadcn.alert_dialog_cancel('Cancel')
            shadcn.alert_dialog_action('Continue').on('click', confirm.close)

with shadcn.sheet():
    shadcn.sheet_trigger('Open sheet')
    with shadcn.sheet_content(title='Edit profile', side='right'):
        shadcn.input(value='Ada Lovelace')

with shadcn.hover_card():
    shadcn.hover_card_trigger().classes('underline')
    with shadcn.hover_card_content():
        shadcn.muted('@ada - joined March 2020')

shadcn.menubar({'File': [{'value': 'new', 'label': 'New'},
                         {'kind': 'separator'},
                         {'value': 'quit', 'label': 'Quit'}],
                'Edit': [{'value': 'undo', 'label': 'Undo'}]},
               on_select=lambda e: ui.notify(str(e.args)))

shadcn.navigation_menu([
    {'label': 'Home', 'href': '/'},
    {'label': 'Products', 'items': [{'label': 'Analytics', 'href': '/analytics'}]},
])

with shadcn.context_menu():
    shadcn.context_menu_trigger('Right-click me')
    shadcn.context_menu_content([{'value': 'copy', 'label': 'Copy'}],
                                on_select=lambda e: ui.notify(str(e.args)))

shadcn.command([{'value': 'calendar', 'label': 'Calendar', 'group': 'Suggestions'},
                {'kind': 'separator'},
                {'value': 'logout', 'label': 'Log out', 'group': 'Settings'}],
               on_select=lambda e: ui.notify(str(e.args)))

with shadcn.toast_provider():
    saved = shadcn.toast('Saved', description='Your changes are live.')

saved.open()      # or let the provider's duration close it
```

### Icons

The library inlines the handful of [Lucide](https://lucide.dev) glyphs it needs, so no
icon bundle is shipped. `icons.ICON_NAMES` lists them, and `icons.svg()` gives you the
markup for your own use:

```python
from nicegui_shadcn import icons

shadcn.button('Delete', icon='trash-2', variant='destructive')
ui.html(icons.svg('github', size=24), sanitize=False)
shadcn.button('Icon only', icon='settings', size='icon')   # label becomes sr-only
```

## Dark mode

The Tailwind `dark:` variant is bound to `body.body--dark` — the class NiceGUI's own
`ui.dark_mode()` toggles — and the shadcn tokens are redefined under `.dark`. So the usual
NiceGUI switch is all you need:

```python
ui.dark_mode().bind_value(...)   # or ui.dark_mode(True)
```

## Theme

Every component reads the same set of CSS variables, so re-theming means replacing those
variables. The shipped stylesheet carries shadcn's `neutral` palette statically; the
`theming` module replaces the whole palette at runtime — no rebuild, no restart:

```python
from nicegui_shadcn import theming

theming.use_base_color('zinc')          # neutral/stone/zinc/mauve/olive/mist/taupe
theming.set_colors(primary='#2563eb')   # tweak individual light-mode tokens
theming.set_dark_colors(primary='#60a5fa')
theming.set_radius(0.75)                # every corner derives from --radius
theming.set_variables(spacing='0.22rem')  # any other CSS variable
theming.add_color('warning', light='#f59e0b', dark='#fbbf24')
theming.reset()                         # back to the compiled default
```

Two things surprise people here. The compiled default *is* `neutral`, and the seven base
colours differ only in chroma (at most 0.019) while all of them share `--radius: 0.625rem` —
so `use_base_color()` is a subtle change that never moves a corner. And Tailwind's
`@theme inline` inlines `--font-sans`, `--shadow-*` and the whole `--radius-sm` … `--radius-4xl`
ladder into the utilities at build time, so overriding those does nothing; `set_variables()`
warns whenever a name is not read through `var()` by the shipped stylesheet.

`add_color()` defines the token and generates the matching `bg-`/`text-`/`border-`/`ring-`/
`fill-`/`stroke-`/`outline-`/`divide-` utilities plus their `dark:` variants, so a colour
shadcn does not ship behaves like one that it does. Calls made before the server starts are
coalesced into a single head injection; calls made afterwards are broadcast to every open
page, so a theme picker updates live.

See [Theme](docs/tutorial/theming.md) in the documentation for the token table, the radius
ladder and the caveats.

## Keyword arguments from NiceGUI

Every component is a real `nicegui.element.Element`, so the standard toolbox works
unchanged: `.bind_value()`, `.on()`, `.tooltip()`, `.classes()`, `.with_classes()`, `.style()`,
`.props()`,
`.move()`, `.set_enabled()`, `.visible`, `.add_slot()`, and `ui.context`.

## Component reference

| Group | Factory | Highlights |
| --- | --- | --- |
| Buttons | `button` | `variant` ∈ default/destructive/outline/secondary/ghost/link, `size` ∈ default/sm/lg/icon, `icon`, `icon_position`, `loading`, `disabled` |
| | `button_group`, `button_group_text`, `button_group_separator` | `vertical: bool` |
| Forms | `input`, `textarea` | `placeholder`, `type`, `disabled`, `readonly`, `autocomplete`, `rows`, `on_change` |
| | `checkbox`, `switch` | `value: bool`, `disabled`, `on_change` |
| | `label` | `for_` takes an element or an id |
| | `select` | `options`, `value`, `placeholder`, `disabled` |
| | `native_select` | the plain HTML `<select>`; `options`, `value`, `disabled` |
| | `combobox` | `options`, `value`, `placeholder`, `search_placeholder`, `filter`, `on_select` |
| | `radio_group` | `options`, `value`, `orientation`, `disabled` |
| | `slider` | `min`, `max`, `step`, `orientation`, `disabled` |
| | `toggle`, `toggle_group` | `value`, `multiple`, `orientation`, `disabled` |
| | `input_otp` | `length`, `groups`, `masked`, `pattern`, `inputmode`, `disabled` |
| | `calendar` | `value` (ISO string or `date`), `min_value`, `max_value`, `week_starts_on`, `number_of_months`, `fixed_weeks`, `disabled`, `readonly` |
| | `date_picker` | a `popover` + `calendar` composition: `value`, `min_value`, `max_value`, `format_date`, `on_date_change` |
| Display | `badge` | `variant` ∈ default/secondary/destructive/outline |
| | `avatar` | `src`, `fallback`, `size` ∈ default/sm/lg/xl |
| | `alert`, `alert_title`, `alert_description` | `title`, `description`, `variant` ∈ default/destructive, `icon` |
| | `progress` | `value` (clamped 0–100), `set_value()` |
| | `spinner` | `size`, `label` (the accessible name) |
| | `kbd`, `marker` | `marker` takes `variant` ∈ default/success/warning/error/info |
| | `aspect_ratio` | `ratio` |
| | `empty`, `empty_header`, `empty_media`, `empty_title`, `empty_description`, `empty_content` | `empty_media(variant=...)` ∈ default/icon |
| | `item`, `item_group`, `item_header`, `item_media`, `item_title`, `item_description`, `item_content`, `item_actions`, `item_footer`, `item_separator` | `item(variant=...)` ∈ default/outline/muted, `size` ∈ default/sm |
| | `table`, `table_container`, `table_header`, `table_body`, `table_footer`, `table_row`, `table_head`, `table_cell`, `table_caption` | |
| Typography | `h1`–`h4`, `heading`, `paragraph`, `lead`, `large`, `small`, `muted`, `blockquote`, `bullet_list`, `inline_code` | `heading(level=...)` |
| Layout | `card`, `card_header`, `card_title`, `card_description`, `card_content`, `card_footer` | |
| | `separator` | `orientation`, `decorative` |
| | `skeleton` | `width`, `height` |
| | `scroll_area` | `type_` ∈ hover/scroll/auto/always |
| | `direction` | `direction` ∈ ltr/rtl, for right-to-left scripts |
| | `breadcrumb`, `breadcrumb_list`, `breadcrumb_item`, `breadcrumb_link`, `breadcrumb_page`, `breadcrumb_separator`, `breadcrumb_ellipsis` | `breadcrumb_separator(icon=...)` |
| | `pagination` | `page`, `total`, `siblings`, `on_change` |
| Disclosure | `tabs`, `tabs_list`, `tabs_content` | `value`, `orientation` |
| | `accordion`, `accordion_item`, `accordion_trigger`, `accordion_content` | `value`, `multiple` |
| | `collapsible`, `collapsible_trigger`, `collapsible_content` | `value`, plus `open()`/`close()`/`toggle()` |
| Overlays | `dialog`, `dialog_trigger`, `dialog_content`, `dialog_footer` | `open()`/`close()`/`toggle()`, `side`, `closable` |
| | `sheet`, `sheet_trigger`, `sheet_content`, `sheet_footer` | a dialog anchored to an edge; `side` ∈ right/left/top/bottom |
| | `drawer`, `drawer_trigger`, `drawer_content`, `drawer_footer` | a swipeable sheet; `side` ∈ bottom/… |
| | `alert_dialog`, `alert_dialog_trigger`, `alert_dialog_content`, `alert_dialog_action`, `alert_dialog_cancel`, `alert_dialog_footer` | a dialog the user has to answer |
| | `popover`, `popover_trigger`, `popover_content` | `side`, `align` |
| | `hover_card`, `hover_card_trigger`, `hover_card_content` | `side`, `align` |
| | `dropdown_menu` | `items`, `align`, `on_select` |
| | `context_menu`, `context_menu_trigger`, `context_menu_content` | `items`, `on_select` |
| | `menubar` | `menus` (label → items), `align`, `on_select` |
| | `navigation_menu` | `items` (links and panels), `on_select` |
| | `command` | `items`, `placeholder`, `empty_text`, `filter`, `on_select`, `on_search` |
| | `tooltip` | `text`, `side`, `delay` |
| Feedback | `toast_provider` | `position` ∈ six corners, `duration`, `swipe_direction` |
| | `toast` | `title`, `description`, `variant` ∈ default/destructive/success, `duration`, `closable` |
| Theming | `theming` | see [Theme](#theme) |
| Icons | `icon` | `icon('check', size=16)` |

`options` and `items` accept all of these spellings, everywhere:

```python
shadcn.select(['system', 'light', 'dark'])                     # value == label
shadcn.select({'system': 'System', 'light': 'Light'})          # value -> label
shadcn.select([('system', 'System'), ('light', 'Light')])      # (value, label) pairs
shadcn.select([{'value': 'system', 'label': 'System', 'disabled': False}])
```

## Documentation

A documentation site lives in [`docs/`](docs) — Chinese-first, built with
[Sphinx](https://www.sphinx-doc.org) and
[pydata-sphinx-theme](https://pydata-sphinx-theme.readthedocs.io):

- **首页 (Home)** — `docs/index.md`, with light and dark screenshots of the demo.
- **教程 (Tutorial)** — the basics, covering the same ground as this README: installation,
  how it works, usage, layout, forms, display, disclosure, overlays, icons, dark mode,
  theming, the component reference, and the design notes.
- **开始 (Getting started)** — the advanced material: writing a new component, styling and
  theming, building and testing, and packaging.

```bash
pip install -r docs/requirements.txt
python -m sphinx -b html docs docs/_build/html
python -m http.server 8300 --directory docs/_build/html
```

Then open <http://127.0.0.1:8300/> in a browser.
`docs/Makefile` and `docs/make.bat` wrap the same command (`make -C docs html`, or
`docs\make.bat html`). The pages are MyST Markdown and `docs/conf.py` reads the version
straight out of `pyproject.toml`, so the docs and the package cannot drift apart.

## Development

```bash
npm install
npx @tailwindcss/cli -i ./frontend/tailwind.css -o ./nicegui_shadcn/static/shadcn.css
npx esbuild frontend/vendor/reka-entry.js --bundle --format=esm --target=es2020 \
    --external:vue --minify --legal-comments=none --outfile=nicegui_shadcn/static/vendor/reka-ui.js
```

Rebuild the CSS after touching any `.py` or `.vue` file: Tailwind only emits the utilities
it can see, and it scans both file types (`@source` globs in `frontend/tailwind.css`).
Automatic content detection is switched off with `source(none)`, so the compiled output is
a function of those globs alone and does not change with whatever else is in the checkout.

Tests:

```bash
python tests/test_tw_merge.py        # tailwind-merge semantics (62 cases)
python tests/test_render.py          # every component renders without a client
python tests/audit_classes.py        # every class used in Python exists in the CSS
python tests/check_examples.py       # every Markdown sample binds to a real signature
python tests/check_readme.py         # README.md and README_zh.md stay in sync
python examples/demo.py              # then, in another shell:
node tests/visual_check.mjs http://127.0.0.1:8080/
```

`visual_check.mjs` drives the demo in headless Edge and asserts the things that a Python
test cannot see: computed colours resolve to the shadcn tokens, the `.vue` components
actually mounted, the reka-ui primitives render (tabs, accordion, slider, radio, toggles),
the overlays portal/focus/dismiss correctly, light and dark agree, and nothing overflows.

If you are changing the library itself — rather than using it — read
[`AGENT.md`](AGENT.md): it documents the NiceGUI extension contract, the constraints of
NiceGUI's home-grown `.vue` parser, the Tailwind cascade-layer rules, and the mistakes that
have already been made here once.

## Extending the stylesheet

`classes=` and `element.classes(...)` can only apply classes that exist in the compiled
stylesheet. To use your own, point a copy of the Tailwind source at your application and
rebuild:

```bash
npm install -D tailwindcss @tailwindcss/cli
# frontend/ ships in the sdist; if you installed the wheel, take it from the repository
printf '@source "../myapp/**/*.py";\n' >> frontend/tailwind.css
npx @tailwindcss/cli -i ./frontend/tailwind.css -o ./myapp/static/shadcn.css
```

`@source` takes globs, and `@source inline("bg-blue-600")` forces a class that only ever
appears at runtime inside a string. Then link the result from your page:

```python
from nicegui import ui
from nicegui_shadcn import shadcn  # still needed: registers the components

ui.add_head_html('<link rel="stylesheet" href="/static/shadcn.css">', shared=True)
```

Everything the library needs is namespaced by the cascade layers it declares, so an
extended rebuild and the bundled stylesheet are interchangeable.

## Packaging and publishing

This is a [Poetry](https://python-poetry.org) project, so publishing is two commands:

```bash
poetry check            # metadata is valid
poetry publish --build  # builds the wheel + sdist and uploads them to PyPI
```

`poetry publish` needs credentials once, either in Poetry's config or in the environment
variable it also reads (handy for CI, where nothing is written to disk):

```bash
poetry config pypi-token.pypi pypi-AgEIcHlwaS5vcmc...
export POETRY_PYPI_TOKEN_PYPI=pypi-AgEIcHlwaS5vcmc...
```

Send a release candidate to TestPyPI first. Poetry has no built-in `testpypi` repository,
so define it once:

```bash
poetry config repositories.testpypi https://test.pypi.org/legacy/
poetry config pypi-token.testpypi pypi-AgEIcHlwaS5vcmc...
poetry publish --repository testpypi --build
```

`poetry publish --dry-run` resolves the target repository and both artifacts without
uploading anything, which is a cheap way to check the metadata and the `dist/` contents.

Either way, `poetry publish` with no arguments and an already-built `dist/` is enough —
it uploads what is there instead of rebuilding, so `poetry build && poetry publish` and
`poetry publish --build` are the same release.

What goes where:

| Artifact | Contents |
| --- | --- |
| wheel | `nicegui_shadcn/` only — the Python modules, the 54 `.vue` templates and `static/` with the two prebuilt assets. |
| sdist | the same, plus `frontend/` (Tailwind source and esbuild entry), `package.json` + `package-lock.json` (which pin the two build tools), `examples/`, `tests/` and `AGENT.md`, so the assets can be rebuilt from source. |

The build inputs deliberately live outside the package in `frontend/`, so the wheel stays
runtime-only and importing `nicegui_shadcn` never reads a build-time file.

## Design notes and limitations

- **`.vue` files use the Options API.** NiceGUI's `VBuild` is an HTML parser, not a Vue
  SFC compiler: `<script setup>` is not compiled, and a nested `<template>` truncates the
  template. Templates here are built with `v-for` on a real element and
  `<component :is>` instead.
- **No Tailwind preflight.** Quasar already normalises, and a second reset would fight it.
  The one preflight rule the library needs (`[hidden] { display: none }`, used by
  mounted-but-closed panels) is added by hand.
- **shadcn's own CSS variables, not Quasar's.** Both define `--primary`; the shadcn
  utilities win because they are emitted into `layer(utilities) important`, which beats
  `quasar_importants`. Quasar widgets keep their own colours.
- **Tabs are data-driven.** reka-ui's `TabsList` provides the roving-focus context that
  `TabsTrigger` injects, and that injection does not survive a NiceGUI slot, so the
  triggers are generated inside the list component. The trade-off is that a tab cannot
  contain arbitrary NiceGUI children; it takes a label.
- **Mounted-but-closed panels.** `TabsContent` and `AccordionContent` stay in the DOM so
  that server-side updates always find their elements; `data-[state=inactive]:hidden` and
  `data-[state=closed]:hidden` do the hiding. The consequence is that the accordion has no
  *closing* animation.
- **Icons are inlined**, not bundled from `lucide-vue-next`; the package ships 39 glyphs.
- **The stylesheet is pre-compiled, so `classes=` is bounded.** Semantic colours and a
  curated layout vocabulary are force-generated with `@source inline(...)`; everything else
  needs a rebuild ([Extending the stylesheet](#extending-the-stylesheet)). The alternative —
  generating all of Tailwind, or shipping a runtime JIT — would either multiply the download
  or reintroduce a reset that fights Quasar.
- **The README screenshots use relative paths**, which work on a repository host but not on
  PyPI; switch them to absolute raw URLs once the project has a home.

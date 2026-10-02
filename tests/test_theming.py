"""Checks for ``nicegui_shadcn.theming``: the bundled palettes, the generated
stylesheet, the argument validation and the head injection.

The strongest claim this module makes is that the theme ships *shadcn's own*
palette, so most of the work here is comparing our numbers against the asset in
``nicegui_shadcn/static/base-colors.json`` -- which is itself a copy of the
registry payload (see ``tests/update_base_colors.py``).

Run with ``python tests/test_theming.py``.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from nicegui import Client  # noqa: E402

import nicegui_shadcn  # noqa: E402
from nicegui_shadcn import shadcn, theming  # noqa: E402

ROOT_CSS = ROOT / 'frontend' / 'tailwind.css'
COMPILED_CSS = ROOT / 'nicegui_shadcn' / 'static' / 'shadcn.css'
PORT = int(os.environ.get('SHADCN_TEST_PORT', '8138'))
URL = f'http://127.0.0.1:{PORT}/'

PALETTES = json.loads((ROOT / 'nicegui_shadcn' / 'static' / 'base-colors.json')
                      .read_text(encoding='utf-8'))['colors']
CHARTS = tuple(f'chart-{index}' for index in range(1, 6))
RADIUS_SCALE = {
    'radius-xs': 'calc(var(--radius) * 0.4)',
    'radius-sm': 'calc(var(--radius) * 0.6)',
    'radius-md': 'calc(var(--radius) * 0.8)',
    'radius-lg': 'var(--radius)',
    'radius-xl': 'calc(var(--radius) * 1.4)',
    'radius-2xl': 'calc(var(--radius) * 1.8)',
    'radius-3xl': 'calc(var(--radius) * 2.2)',
    'radius-4xl': 'calc(var(--radius) * 2.6)',
}
FAMILIES = (
    ('bg', 'background-color'),
    ('text', 'color'),
    ('border', 'border-color'),
    ('ring', '--tw-ring-color'),
    ('fill', 'fill'),
    ('stroke', 'stroke'),
    ('outline', 'outline-color'),
)

APP = """
from nicegui import ui
from nicegui_shadcn import shadcn, theming

theming.use_base_color('zinc')
theming.set_radius(0.75)
theming.set_colors(primary='#2563eb')
theming.set_dark_colors(primary='#60a5fa')
theming.add_color('warning', light='#f59e0b', dark='#fbbf24',
                  foreground_light='#1c1917')


@ui.page('/')
def page():
    shadcn.button('Themed')


ui.run(port=__PORT__, show=False, reload=False)
""".replace('__PORT__', str(PORT))

passed = 0
failures: list[str] = []


def check(name: str, condition: object) -> None:
    global passed
    if condition:
        passed += 1
    else:
        failures.append(name)


def declarations(text: str, pattern: str) -> dict[str, str]:
    """Return the ``--custom-properties`` of the first block matching ``pattern``.

    The pattern must not contain the opening brace: ``match.end()`` would then sit
    past it and the search for the closing brace would land in the *next* block.
    """
    match = re.search(pattern + r'\s*\{([^}]*)\}', text, re.M)
    assert match, f'no block matched {pattern!r}'
    return {found.group(1): found.group(2).strip()
            for found in re.finditer(r'--([\w-]+)\s*:\s*([^;]+);', match.group(1))}


def rule_body(css: str, selector: str) -> str:
    match = re.search(rf'{re.escape(selector)}\s*\{{([^}}]*)\}}', css)
    assert match, f'no rule for {selector}'
    return ' '.join(match.group(1).split())


def raises(exception: type[BaseException], call) -> str:
    """Run ``call`` and return the message of the expected exception, or ``''``."""
    try:
        call()
    except exception as error:  # noqa: BLE001
        return str(error)
    except BaseException as error:  # noqa: BLE001
        return f'<{type(error).__name__}: {error}>'
    return ''


def warnings_of(call) -> list[str]:
    """Run ``call`` and return the messages of the UserWarnings it raised."""
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        call()
    return [str(warning.message) for warning in caught
            if issubclass(warning.category, UserWarning)]


# --- the bundled registry asset ---------------------------------------------

check('asset lists all base colours', set(PALETTES) == set(theming.BASE_COLORS))
check('asset and constant agree on the order',
      tuple(PALETTES) == theming.BASE_COLORS)
check('every palette carries the shadcn radius',
      {entry['radius'] for entry in PALETTES.values()} == {'0.625rem'})
check('every palette has 31 light and 31 dark tokens',
      {(len(entry['light']), len(entry['dark'])) for entry in PALETTES.values()} == {(31, 31)})
check('all palettes use the same token set',
      len({tuple(entry['light']) for entry in PALETTES.values()}) == 1
      and len({tuple(entry['dark']) for entry in PALETTES.values()}) == 1)
check('the registry token set is COLOR_TOKENS without destructive-foreground',
      set(PALETTES['neutral']['light']) == set(theming.COLOR_TOKENS) - {'destructive-foreground'})

# --- the module is reachable -------------------------------------------------

check('the package exports the theming module',
      'theming' in nicegui_shadcn.__all__ and nicegui_shadcn.theming is theming)
check('the shadcn namespace exposes it too',
      'theming' in shadcn.__all__ and shadcn.theming is theming)

# --- the shipped default is shadcn's neutral --------------------------------

TAILWIND = ROOT_CSS.read_text(encoding='utf-8')
DEFAULT_LIGHT = declarations(TAILWIND, r'^:root')
DEFAULT_DARK = declarations(TAILWIND, r'^body\.body--dark,\s*\.dark')
NEUTRAL = PALETTES['neutral']
semantic = {name: value for name, value in NEUTRAL['light'].items() if name not in CHARTS}
semantic_dark = {name: value for name, value in NEUTRAL['dark'].items() if name not in CHARTS}

check('shipped :root matches the neutral palette token for token',
      {name: DEFAULT_LIGHT.get(name) for name in semantic} == semantic)
check('shipped dark block matches the neutral palette token for token',
      {name: DEFAULT_DARK.get(name) for name in semantic_dark} == semantic_dark)
check('shipped charts are the vivid default-theme values, not the registry ramp',
      all(DEFAULT_LIGHT[name] != NEUTRAL['light'][name] for name in CHARTS)
      and all(DEFAULT_DARK[name] != NEUTRAL['dark'][name] for name in CHARTS))
check('shipped blocks keep the extra destructive-foreground token',
      'destructive-foreground' in DEFAULT_LIGHT and 'destructive-foreground' in DEFAULT_DARK)

# --- the radius scale -------------------------------------------------------

check('the @theme radius scale is the published proportional one',
      {name: declarations(TAILWIND, r'^@theme inline').get(name) for name in RADIUS_SCALE}
      == RADIUS_SCALE)
COMPILED = COMPILED_CSS.read_text(encoding='utf-8')
check('compiled .rounded-sm follows the radius token',
      rule_body(COMPILED, '.rounded-sm') == 'border-radius: calc(var(--radius) * 0.6) !important;')
check('compiled .rounded-lg follows the radius token',
      rule_body(COMPILED, '.rounded-lg') == 'border-radius: var(--radius) !important;')
check('compiled .rounded-2xl follows the radius token',
      rule_body(COMPILED, '.rounded-2xl') == 'border-radius: calc(var(--radius) * 1.8) !important;')
check('theming.py is excluded from the class scan',
      '@source not "../nicegui_shadcn/theming.py"' in TAILWIND
      and '.accent-foreground {' not in COMPILED)

# --- the generated stylesheet -----------------------------------------------

theming.reset()
check('nothing is injected while no theme is set', theming.css() == '')

theming.use_base_color('zinc')
generated = theming.css()
zinc_light = PALETTES['zinc']['light']
zinc_dark = PALETTES['zinc']['dark']
root_block = declarations(generated, r'^:root')
dark_block = declarations(generated, r'^body\.body--dark,\s*\.dark')
check('use_base_color writes the light palette into :root',
      {name: root_block.get(name) for name in zinc_light} == zinc_light)
check('use_base_color writes the dark palette into the dark block',
      {name: dark_block.get(name) for name in zinc_dark} == zinc_dark)
check('use_base_color carries the radius token',
      root_block.get('radius') == '0.625rem')
check('the light block is the registry palette plus the radius token',
      set(root_block) == set(zinc_light) | {'radius'})
check('the dark block is the registry palette',
      set(dark_block) == set(zinc_dark))
check('the generated stylesheet defines no utilities of its own',
      '@layer utilities' not in generated)

for name in theming.BASE_COLORS:
    theming.reset()
    theming.use_base_color(name)
    block = declarations(theming.css(), r'^:root')
    check(f'base colour {name!r} round-trips',
          {token: block.get(token) for token in PALETTES[name]['light']} == PALETTES[name]['light'])

theming.reset()
theming.use_base_color('neutral')
theming.set_colors(primary='#2563eb', card_foreground='#111827')
theming.set_dark_colors(ring='#60a5fa')
generated = theming.css()
root_block = declarations(generated, r'^:root')
dark_block = declarations(generated, r'^body\.body--dark,\s*\.dark')
check('set_colors accepts underscore spelling and hits only the light block',
      root_block.get('primary') == '#2563eb' and root_block.get('card-foreground') == '#111827'
      and dark_block.get('primary') == PALETTES['neutral']['dark']['primary'])
check('set_dark_colors hits only the dark block',
      dark_block.get('ring') == '#60a5fa' and root_block.get('ring') == PALETTES['neutral']['light']['ring'])
check('set_colors keeps the other tokens from the base palette',
      root_block.get('background') == PALETTES['neutral']['light']['background'])
check('current() reports what was set',
      theming.current()['light']['primary'] == '#2563eb'
      and theming.current()['dark']['ring'] == '#60a5fa'
      and theming.current()['radius'] == '0.625rem'
      and theming.current()['colors'] == {})
check('the comment names the module',
      theming.css().startswith('/* nicegui-shadcn theme - generated by nicegui_shadcn.theming */'))

theming.reset()
theming.set_radius(0.75)
check('set_radius takes a number of rem', declarations(theming.css(), r'^:root')['radius'] == '0.75rem')
theming.use_base_color('stone')
check('an explicit radius survives a later base colour',
      declarations(theming.css(), r'^:root')['radius'] == '0.75rem')
theming.reset()
theming.use_base_color('stone')
check('a base colour still supplies its own radius when none was set',
      declarations(theming.css(), r'^:root')['radius'] == '0.625rem')
theming.reset()
theming.set_radius(0.75)
theming.set_radius('12px')
check('set_radius takes a CSS length', declarations(theming.css(), r'^:root')['radius'] == '12px')
check('set_radius keeps a theme that has no colours yet', theming.css().count(':root') == 1)

# --- colours added at runtime ------------------------------------------------

theming.reset()
theming.add_color('warning', light='#f59e0b', dark='#fbbf24', foreground_light='#1c1917')
generated = theming.css()
root_block = declarations(generated, r'^:root')
dark_block = declarations(generated, r'^body\.body--dark,\s*\.dark')
check('add_color defines the token in both modes',
      root_block.get('warning') == '#f59e0b' and dark_block.get('warning') == '#fbbf24')
check('add_color defines the foreground in both modes',
      root_block.get('warning-foreground') == '#1c1917'
      and dark_block.get('warning-foreground') == '#1c1917')
check('add_color wraps its utilities in the utilities layer',
      '@layer utilities {\n' in generated and generated.rstrip().endswith('}'))
for prefix, prop in FAMILIES:
    check(f'add_color generates .{prefix}-warning',
          f'  .{prefix}-warning {{ {prop}: var(--warning) !important; }}' in generated)
check('add_color generates the divide utility',
      '  :where(.divide-warning > :not(:last-child)) '
      '{ border-color: var(--warning) !important; }' in generated)
check('add_color generates the dark: variants',
      '  .dark\\:bg-warning:where(body.body--dark, body.body--dark *) '
      '{ background-color: var(--warning) !important; }' in generated)
check('the generated utilities sit after the token blocks',
      generated.index(':root {') < generated.index('@layer utilities {'))
check('the utilities layer does not leak the base palette',
      generated.count('@layer utilities {') == 1)
check('current() reports the added colour',
      theming.current()['colors'] == {'warning': {'light': '#f59e0b', 'dark': '#fbbf24',
                                                  'foreground_light': '#1c1917',
                                                  'foreground_dark': '#1c1917'}})

theming.reset()
theming.add_color('success', light='#16a34a', dark='#22c55e', foreground_dark='#052e16')
added = theming.current()['colors']['success']
check('a foreground given for one mode is copied to the other',
      added['foreground_light'] == '#052e16' and added['foreground_dark'] == '#052e16')
check('the copied foreground is written in both modes and gets its utilities',
      theming.css().count('--success-foreground:') == 2
      and '  .bg-success-foreground { background-color: var(--success-foreground) !important; }'
      in theming.css())

theming.add_color('info', light='#0ea5e9', dark='#38bdf8')
check('add_color keeps a previously added colour',
      set(theming.current()['colors']) == {'success', 'info'}
      and '.bg-success {' in theming.css() and '.bg-info {' in theming.css())
check('a colour without a foreground gets no -foreground token',
      '--info-foreground' not in theming.css()
      and '.bg-info-foreground' not in theming.css())

theming.reset()
check('reset() drops everything', theming.css() == '' and theming.current() ==
      {'radius': None, 'light': {}, 'dark': {}, 'variables': {}, 'dark_variables': {},
       'colors': {}})

# --- arbitrary CSS variables -------------------------------------------------

theming.reset()
theming.set_variables(spacing='0.22rem', tracking_tight='-0.03em')
generated = theming.css()
check('set_variables writes the light block on its own',
      theming.css().count(':root') == 1 and 'body.body--dark' not in generated)
check('set_variables converts underscores to hyphens',
      declarations(generated, r'^:root').get('tracking-tight') == '-0.03em')
check('set_variables reaches a scale the stylesheet reads at runtime',
      declarations(generated, r'^:root').get('spacing') == '0.22rem')
check('a variable the stylesheet consumes does not warn',
      warnings_of(lambda: theming.set_variables(spacing='0.25rem')) == [])

theming.set_variables(**{'--chart-1': 'oklch(0.6 0.2 20)'})
check('set_variables tolerates the leading dashes',
      declarations(theming.css(), r'^:root').get('chart-1') == 'oklch(0.6 0.2 20)')

message = warnings_of(lambda: theming.set_variables(font_sans='Inter, sans-serif'))
check('a variable the build inlined warns instead of failing silently',
      len(message) == 1 and '--font-sans cannot change any utility' in message[0]
      and '@theme inline' in message[0])
check('the unreadable variable is still declared for your own CSS',
      declarations(theming.css(), r'^:root').get('font-sans') == 'Inter, sans-serif')
check('the same warning is not repeated',
      warnings_of(lambda: theming.set_variables(font_sans='Other, serif')) == [])
check('a variable of your own is not second-guessed',
      warnings_of(lambda: theming.set_variables(brand='#0ea5e9')) == [])

_name = next(iter(sorted(theming._declared_variables() - theming._consumed_variables())), '')
check('a token the stylesheet declares but never reads also warns',
      _name != '' and len(warnings_of(lambda: theming.set_variables(**{_name: 'red'}))) == 1)

theming.set_dark_variables(card='#111827')
generated = theming.css()
check('set_dark_variables hits only the dark block',
      declarations(generated, r'^body\.body--dark,\s*\.dark').get('card') == '#111827'
      and declarations(generated, r'^:root').get('card') is None)

theming.set_colors(primary='#2563eb')
theming.set_variables(primary='#dc2626')
check('a variable wins over a colour token of the same name',
      declarations(theming.css(), r'^:root').get('primary') == '#dc2626')
check('current() reports the variables',
      theming.current()['variables']['primary'] == '#dc2626'
      and theming.current()['dark_variables'] == {'card': '#111827'})
check('the comments still come first',
      theming.css().startswith('/* nicegui-shadcn theme - generated by nicegui_shadcn.theming */'))
check('variables keep the insertion order',
      [name for name in declarations(theming.css(), r'^:root')
       if name in ('spacing', 'tracking-tight', 'chart-1')]
      == ['spacing', 'tracking-tight', 'chart-1'])

theming.reset()
check('reset() drops the variables too', theming.css() == '' and theming.current() ==
      {'radius': None, 'light': {}, 'dark': {}, 'variables': {}, 'dark_variables': {},
       'colors': {}})

# --- argument validation -----------------------------------------------------

message = raises(ValueError, lambda: theming.use_base_color('bogus'))
check('an unknown base colour is rejected with the valid ones',
      "Unknown base colour 'bogus'" in message and "'neutral'" in message)
message = raises(ValueError, lambda: theming.set_colors(primry='#fff'))
check('a typo in a token name suggests the real one',
      'unknown colour token' in message and "'primary'" in message)
message = raises(ValueError, lambda: theming.set_colors(primary='red; }'))
check('a value that could escape the style element is rejected',
      'must not contain' in message)
message = raises(TypeError, lambda: theming.set_colors(primary=1))
check('a non-string colour is rejected', 'must be a CSS colour string' in message)
message = raises(TypeError, lambda: theming.set_radius(True))
check('set_radius refuses a bool', 'number of rem' in message)
message = raises(ValueError, lambda: theming.set_radius('0.75'))
check('set_radius refuses a length without a unit', 'not a CSS length' in message)
message = raises(ValueError, lambda: theming.set_radius(-1))
check('set_radius refuses a negative radius', 'cannot be negative' in message)
message = raises(ValueError, lambda: theming.set_radius(''))
check('set_radius refuses an empty string', 'must not be empty' in message)
theming.reset()
theming.set_radius('calc(0.5rem + 2px)')
check('set_radius accepts a calc() length',
      declarations(theming.css(), r'^:root')['radius'] == 'calc(0.5rem + 2px)')
message = raises(ValueError, lambda: theming.set_variables(**{'Bogus Name': '#fff'}))
check('set_variables wants a kebab-case name', 'invalid CSS variable name' in message)
message = raises(ValueError, lambda: theming.set_variables(font='serif; }'))
check('set_variables rejects a value that could escape the style element',
      'must not contain' in message)
message = raises(TypeError, lambda: theming.set_variables(spacing=4))
check('set_variables refuses a number, which would be silently dropped',
      'must be a CSS value string' in message)
message = raises(ValueError, lambda: theming.set_dark_variables(**{'not ok': '1'}))
check('set_dark_variables validates names too', 'invalid CSS variable name' in message)
message = raises(ValueError, lambda: theming.add_color('Warning', light='#fff', dark='#000'))
check('add_color wants a kebab-case name', 'kebab-case' in message)
message = raises(ValueError, lambda: theming.add_color('primary', light='#fff', dark='#000'))
check('add_color refuses a built-in token', 'set_colors(primary=...)' in message)
message = raises(ValueError, lambda: theming.add_color('custom', light='#fff', dark=''))
check('add_color refuses an empty value', 'must not be empty' in message)
message = raises(TypeError, lambda: theming.add_color('custom', light='#fff', dark='#000',
                                                     foreground_light=1))
check('add_color validates the foreground too', 'must be a CSS colour string' in message)

# --- the head injection ------------------------------------------------------

# The real lifecycle is covered end to end by check_served_page() below; here we
# drive the startup flush directly, because app.start() would boot NiceGUI.
theming.reset()
before = len(Client.shared_head_html)
theming.use_base_color('zinc')
theming.set_radius(0.75)
theming.set_colors(primary='#2563eb')
check('theming before startup is coalesced, not injected per call',
      len(Client.shared_head_html) == before)
theming._flush()
after = len(Client.shared_head_html)
check('the startup flush injects the accumulated theme', after > before)
theming._flush()
check('flushing an unchanged theme is a no-op', len(Client.shared_head_html) == after)
check('the injection carries the replacement snippet',
      'nicegui-shadcn-theme' in Client.shared_head_html)
check('the snippet runs after the stylesheet link',
      Client.shared_head_html.index('/_nicegui_shadcn/shadcn.css')
      < Client.shared_head_html.index('nicegui-shadcn-theme'))
check('the injected block is a script, not a bare <style>',
      '<script>' in Client.shared_head_html
      and '<style id="nicegui-shadcn-theme">' not in Client.shared_head_html)
theming.set_colors(primary='#60a5fa')
check('a change after startup is injected immediately',
      len(Client.shared_head_html) > after)


def wait_for_server(timeout: float = 45.0) -> str:
    deadline = time.time() + timeout
    last_error: Exception | None = None
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(URL, timeout=2) as response:  # noqa: S310
                return response.read().decode('utf-8')
        except (urllib.error.URLError, ConnectionError, TimeoutError) as error:
            last_error = error
            time.sleep(0.4)
    raise RuntimeError(f'the themed app did not come up: {last_error}')


def check_served_page() -> None:
    process = subprocess.Popen(  # noqa: S603
        [sys.executable, '-c', APP],
        cwd=str(ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        html = wait_for_server()
    finally:
        process.kill()
        process.wait(timeout=10)
    check('the themed page carries the injection', 'style#' in html and 'nicegui-shadcn-theme' in html)
    payloads = re.findall(r'style\.textContent = ("(?:[^"\\]|\\.)*");', html)
    check('the setup is injected once, not once per setter', len(payloads) == 1)
    payload = payloads[-1] if payloads else None
    check('the payload is a JSON string', payload is not None)
    if payload:
        text = json.loads(payload)
        check('the payload is the generated stylesheet',
              '--primary: #2563eb;' in text and '--primary: #60a5fa;' in text)
        check('the payload carries the radius', '--radius: 0.75rem;' in text)
        check('the payload carries the runtime colour utilities',
              '.bg-warning { background-color: var(--warning) !important; }' in text)
        check('the payload cannot escape the script element', '<' not in text)
    check('the injection comes after the stylesheet link',
          html.index('/_nicegui_shadcn/shadcn.css') < html.index('nicegui-shadcn-theme'))


check_served_page()

if failures:
    print(f'{len(failures)} of {passed + len(failures)} checks failed:')
    for failure in failures:
        print(f'  FAIL {failure}')
    sys.exit(1)

print(f'OK - {passed} theming checks passed')

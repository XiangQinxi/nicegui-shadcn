"""End-to-end check: boot the demo app and inspect the served HTML.

This is the strongest automated signal available without a browser: it proves
that the stylesheet link, the import map, the ``reka-ui`` override and the
generated ``.vue`` component registration all reach the page.

Run with ``python tests/test_render.py`` or ``pytest tests/test_render.py``.
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ELEMENTS = ROOT / 'nicegui_shadcn' / 'elements'
# A port of its own, so the test can run while the demo is being looked at.
PORT = int(os.environ.get('SHADCN_TEST_PORT', '8137'))
URL = f'http://127.0.0.1:{PORT}/'


def wait_for_server(timeout: float = 45.0) -> str:
    """Poll the demo app until it answers, then return its HTML."""
    deadline = time.time() + timeout
    last_error: Exception | None = None
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(URL, timeout=2) as response:  # noqa: S310
                return response.read().decode('utf-8')
        except (urllib.error.URLError, ConnectionError, TimeoutError) as error:
            last_error = error
            time.sleep(0.4)
    raise RuntimeError(f'the demo app did not come up: {last_error}')


def _component_checks() -> list[tuple[str, str]]:
    """One check per ``.vue`` file, derived from the directory.

    A component that is never registered would render nothing in the browser and
    produce no Python error, so the registration has to be asserted explicitly --
    and deriving the list from the files means a new component is covered without
    touching this test.
    """
    return [
        (f'{path.stem} registered', f'tpl-{path.stem}')
        for path in sorted(ELEMENTS.glob('*.vue'))
    ]


CHECKS: list[tuple[str, str]] = [
    ('stylesheet link', '/_nicegui_shadcn/shadcn.css'),
    ('reka-ui import map entry', '/vendor/reka-ui.js'),
    ('reka-ui specifier mapped', '"reka-ui"'),
    ('page title rendered', 'nicegui-shadcn'),
    ('shadcn button classes', 'bg-primary'),
    ('shadcn card classes', 'rounded-xl'),
    *_component_checks(),
]


def main() -> int:
    import os

    env = {**os.environ, 'SHADCN_DEMO_PORT': str(PORT)}
    process = subprocess.Popen(  # noqa: S603
        [sys.executable, str(ROOT / 'examples' / 'demo.py')],
        cwd=str(ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env,
    )
    try:
        html = wait_for_server()
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()

    failures: list[str] = []
    for label, needle in CHECKS:
        ok = needle in html
        print(f'{"PASS" if ok else "FAIL"}  {label}: {needle!r}')
        if not ok:
            failures.append(label)

    if failures:
        out = (ROOT / '_render-dump.html')
        out.write_text(html, encoding='utf-8')
        print(f'\n{len(failures)} check(s) failed. HTML dumped to {out}')
        return 1
    print(f'\nall {len(CHECKS)} checks passed ({len(html)} bytes of HTML)')
    return 0


if __name__ == '__main__':
    sys.exit(main())

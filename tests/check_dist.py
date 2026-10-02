"""Check the built wheel and sdist: metadata, runtime assets, and exclusions.

Everything the wheel ships is something a user imports or the browser loads, so a
missing `.vue` file or a stale `static/` asset is only visible after `pip install`.
The sdist is the opposite problem: Poetry also honours `.gitignore`, so a file that
is merely untracked can vanish from the source distribution without a word.

The check is skipped while `dist/` holds no artifact for the current version, so it
stays harmless in the normal test loop. Run `poetry build` first to make it bite.

    python tests/check_dist.py
"""
from __future__ import annotations

import re
import sys
import tarfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / 'dist'

failures: list[str] = []


def check(label: str, ok: bool, detail: str = '') -> None:
    print(f'{"PASS" if ok else "FAIL"}  {label}{"  -> " + detail if detail else ""}')
    if not ok:
        failures.append(label)


def version() -> str:
    text = (ROOT / 'pyproject.toml').read_text(encoding='utf-8')
    match = re.search(r'^version = "([^"]+)"', text, re.M)
    assert match, 'no version in pyproject.toml'
    return match.group(1)


def main() -> int:
    current = version()
    wheels = sorted(DIST.glob(f'nicegui_shadcn-{current}-*.whl'))
    sdists = sorted(DIST.glob(f'nicegui_shadcn-{current}.tar.gz'))
    if not wheels or not sdists:
        print(f'SKIP - no {current} artifacts in dist/ (run `poetry build`)')
        return 0

    with zipfile.ZipFile(wheels[0]) as z:
        names = z.namelist()
        meta = z.read(f'nicegui_shadcn-{current}.dist-info/METADATA').decode('utf-8')
        vue = [n for n in names if n.endswith('.vue')]
        expected_vue = sorted(p.name for p in (ROOT / 'nicegui_shadcn' / 'elements').glob('*.vue'))
        assets = [
            'nicegui_shadcn/static/shadcn.css',
            'nicegui_shadcn/static/vendor/reka-ui.js',
            'nicegui_shadcn/static/base-colors.json',
            'nicegui_shadcn/theming.py',
        ]

        check(f'wheel METADATA version is {current}', f'Version: {current}' in meta)
        check(f'wheel ships all {len(expected_vue)} .vue templates',
              sorted(Path(n).name for n in vue) == expected_vue, f'found {len(vue)}')
        for asset in assets:
            check(f'wheel ships {asset}', asset in names,
                  f'{z.getinfo(asset).file_size} bytes' if asset in names else 'MISSING')
        check('wheel excludes frontend/ build inputs',
              not any(n.startswith('frontend/') for n in names))
        check('wheel excludes node_modules', not any('node_modules' in n for n in names))
        check('wheel excludes .idea', not any('.idea' in n for n in names))
        check('wheel excludes __pycache__', not any('__pycache__' in n for n in names))

    with tarfile.open(sdists[0]) as t:
        snames = t.getnames()
        prefix = f'nicegui_shadcn-{current}/'

        def has(rel: str) -> bool:
            return prefix + rel in snames

        for rel in ('frontend/tailwind.css', 'tests/test_tw_merge.py', 'examples/demo.py',
                    'package.json', 'AGENT.md', 'docs/conf.py', 'docs/tutorial/theming.md',
                    'nicegui_shadcn/theming.py', 'nicegui_shadcn/static/shadcn.css',
                    'nicegui_shadcn/static/base-colors.json',
                    'nicegui_shadcn/static/vendor/reka-ui.js'):
            check(f'sdist ships {rel}', has(rel))
        check('sdist excludes docs/_build', not any('/docs/_build/' in n for n in snames))
        check('sdist excludes node_modules', not any('node_modules' in n for n in snames))
        check('sdist excludes .idea', not any('.idea' in n for n in snames))
        check('sdist excludes demos/', not any('/demos/' in n for n in snames))
        check('sdist excludes dist/', not any('/dist/' in n for n in snames))

    print()
    if failures:
        print(f'{len(failures)} check(s) failed:')
        for failure in failures:
            print(f'  - {failure}')
        return 1
    print(f'OK - all dist checks passed ({current})')
    return 0


if __name__ == '__main__':
    sys.exit(main())

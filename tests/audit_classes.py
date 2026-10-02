"""Audit that every Tailwind class the library references is really generated.

Tailwind v4 silently drops a candidate it cannot resolve — a typo, or a utility
whose design token was never exposed through ``@theme inline``. That is how
``bg-input/30`` would vanish if ``--color-input`` were missing. Since the
stylesheet is compiled ahead of time, such a mistake would otherwise only show
up as an unstyled component in the browser.

The scan is deliberately narrow instead of heuristic: it reads the Python class
declarations with :mod:`ast` (the ``default_classes=``/``classes=`` keywords and
the module-level class-table constants such as ``_BASE`` or ``_VARIANTS``) and
the ``class="..."`` attributes of the ``.vue`` templates. Prose, SVG path data
and prop values are never class lists, so they never enter the check.

    python tests/audit_classes.py
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKAGE = ROOT / 'nicegui_shadcn'
CSS = PACKAGE / 'static' / 'shadcn.css'

CLASS_KEYWORDS = {'default_classes', 'classes', 'variant_classes'}
# Only constants that are *named* like class tables are read, so icon markup and
# the conflict tables in ``_tw_merge`` never masquerade as class lists.
CLASS_CONSTANT_RE = re.compile(r'^_?[A-Z][A-Z0-9_]*_(BASE|CLASSES|VARIANTS|SIZES)$')
# The lookbehind rejects the bound forms ``:class`` and ``v-bind:class``, whose
# value is a JavaScript expression and therefore not a class list.
CLASS_ATTR_RE = re.compile(r'(?<![\w:-])class="([^"]*)"')


def escape_class(cls: str) -> str:
    """Reproduce Tailwind's CSS escaping for a class name.

    Every character outside ``[A-Za-z0-9_-]`` is backslash-escaped; ``-`` and
    ``_`` are left alone (``_`` is also Tailwind's stand-in for a space).
    """
    return ''.join(ch if (ch.isalnum() or ch in '-_') else '\\' + ch for ch in cls)


def has_selector(css: str, token: str) -> bool:
    """True when ``css`` contains a rule for exactly this class.

    A plain substring test is not enough: ``.a`` would match ``.animate-pulse``.
    The class must be followed by something that cannot continue it, which
    excludes both identifier characters and the backslash of another escape.
    """
    pattern = re.escape('.' + escape_class(token)) + r'(?![A-Za-z0-9_\\-])'
    return re.search(pattern, css) is not None


def _strings(node: ast.AST) -> list[str]:
    """Class strings carried by a class-table assignment."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return [node.value]
    if isinstance(node, ast.Dict):                    # e.g. _VARIANTS = {...}
        return [v.value for v in node.values
                if isinstance(v, ast.Constant) and isinstance(v.value, str)]
    if isinstance(node, (ast.Tuple, ast.List)):       # e.g. _CLASSES = ('a', 'b')
        out: list[str] = []
        for element in node.elts:
            out += _strings(element)
        return out
    return []


def classes_in_python(path: Path) -> list[tuple[str, str]]:
    tree = ast.parse(path.read_text(encoding='utf-8'))
    strings: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.keyword) and node.arg in CLASS_KEYWORDS:
            strings += _strings(node.value)
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                and node.func.attr in CLASS_KEYWORDS:
            strings += [a.value for a in node.args
                        if isinstance(a, ast.Constant) and isinstance(a.value, str)]
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            names = [t.id for t in targets if isinstance(t, ast.Name)]
            if any(CLASS_CONSTANT_RE.match(n) for n in names):
                strings += _strings(node.value)

    return [(t, path.name) for s in strings for t in s.split()]


def classes_in_vue(path: Path) -> list[tuple[str, str]]:
    text = path.read_text(encoding='utf-8')
    return [(t, path.name) for body in CLASS_ATTR_RE.findall(text) for t in body.split()]


def main() -> int:
    if not CSS.exists():
        print(f'!! {CSS} is missing — run the Tailwind build first')
        return 2
    css = CSS.read_text(encoding='utf-8')

    seen: dict[str, str] = {}
    for path in sorted(PACKAGE.glob('elements/*.py')) + sorted(PACKAGE.glob('*.py')):
        for token, origin in classes_in_python(path):
            seen.setdefault(token, origin)
    for path in sorted(PACKAGE.glob('elements/*.vue')):
        for token, origin in classes_in_vue(path):
            seen.setdefault(token, origin)

    missing = sorted((t, o) for t, o in seen.items() if not has_selector(css, t))
    print(f'checked {len(seen)} class tokens')
    for token, origin in missing:
        print(f'MISSING  {token}  (first seen in {origin})')
    if missing:
        print(f'\n{len(missing)} class(es) have no rule in static/shadcn.css')
        return 1
    print('\nall referenced classes are present in static/shadcn.css')
    return 0


if __name__ == '__main__':
    sys.exit(main())

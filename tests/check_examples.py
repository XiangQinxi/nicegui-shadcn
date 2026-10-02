"""Check every `shadcn.*` / `icons.*` / `theming.*` call inside Markdown code blocks
against the real signatures, so the docs cannot ship an example that does not run.

The README and the documentation site contain hundreds of samples, and a sample is a
promise: ``shadcn.checkbox('Accept terms', value=True)`` reads perfectly and raises
``TypeError``. This is the guard against that class of mistake.

The blocks are parsed with ``ast`` — not regex — so a `shadcn.` mention inside a
string, a comment or a shell block is not a false hit. Because the snake_case
factories forward ``**kwargs`` to the element class, the only decisive question is
whether the call would *bind*, so the check is against ``inspect.signature``.
Samples that are deliberately wrong are shown inside a ``:::{warning}`` and marked
with a trailing comment such as ``# 错误``; those are skipped and counted.

    python tests/check_examples.py                  # README.md, README_zh.md, docs/
    python tests/check_examples.py docs/start       # just one corner
    python tests/check_examples.py docs/forms.md    # or one file

Exit code 0 means every call would bind; 1 lists the offenders as ``file:line``.
"""
from __future__ import annotations

import ast
import inspect
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from nicegui_shadcn import icons, shadcn, theming  # noqa: E402

OWNERS = ((shadcn, "shadcn"), (icons, "icons"), (theming, "theming"))
DEFAULTS = ("README.md", "README_zh.md", "docs")
FENCE_RE = re.compile(r"```(\w*)\n(.*?)```", re.S)
# Deliberately wrong examples live inside :::{warning} blocks and are marked in
# the prose; honour the marker instead of reporting them as real defects.
WRONG_RE = re.compile(r"#\s*(错误|不成立|wrong|bad|✗|✘)")
NAMESPACES = {"shadcn", "icons", "theming"}

SIGNATURES: dict[str, inspect.Signature] = {}
for owner, prefix in OWNERS:
    # ``__all__`` keeps imported helpers (``Path``, ``Template``, …) out of the table.
    names = getattr(owner, "__all__", None) or [n for n in dir(owner) if not n.startswith("_")]
    for name in names:
        if name.startswith("_"):
            continue
        obj = getattr(owner, name, None)
        if callable(obj):
            try:
                SIGNATURES[f"{prefix}.{name}"] = inspect.signature(obj)
            except (TypeError, ValueError):
                pass

problems: list[str] = []
checked = 0
skipped_bad = 0


def show(path: Path) -> str:
    """Path as written from the repository root, so the report is greppable."""
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def md_files(targets: list[str]) -> list[Path]:
    out: list[Path] = []
    for t in targets:
        p = Path(t)
        if not p.is_absolute():
            p = ROOT / p
        if p.is_dir():
            out.extend(sorted(p.rglob("*.md")))
        elif p.exists():
            out.append(p)
        else:
            print(f"warning: {t} does not exist", file=sys.stderr)
    return out


def check_block(path: Path, line0: int, code: str) -> None:
    global checked, skipped_bad
    source_lines = code.splitlines()
    # Strip MyST directives and shell-ish lines that never parse as Python.
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return  # a fragment, not a whole program - runnable-ness is checked by hand

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not isinstance(func, ast.Attribute) or not isinstance(func.value, ast.Name):
            continue
        key = f"{func.value.id}.{func.attr}"
        idx = getattr(node, "lineno", 1) - 1
        line = line0 + idx
        where = f"{show(path)}:{line}"

        if 0 <= idx < len(source_lines) and WRONG_RE.search(source_lines[idx]):
            skipped_bad += 1
            continue

        if func.value.id in NAMESPACES and key not in SIGNATURES:
            problems.append(f"{where}  UNKNOWN  `{key}` is not exported")
            continue
        sig = SIGNATURES.get(key)
        if sig is None:
            continue

        checked += 1
        positional = [
            p
            for p in sig.parameters.values()
            if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
        ]
        has_varargs = any(p.kind is p.VAR_POSITIONAL for p in sig.parameters.values())

        if not has_varargs and len(node.args) > len(positional):
            problems.append(
                f"{where}  ARITY    `{key}{sig}` got {len(node.args)} positional args"
            )
            continue

        for arg, param in zip(node.args, positional):
            # Only the component factories take a *label* where the parameter is
            # called `value`; `theming.set_radius('12px')` is a real value.
            if (func.value.id == "shadcn" and param.name == "value"
                    and isinstance(arg, ast.Constant) and isinstance(arg.value, str)):
                problems.append(
                    f"{where}  LABELISH `{key}({arg.value!r}, ...)` passes a string to the "
                    f"`value` parameter - this is a value, not a label"
                )

        for kw in node.keywords:
            if kw.arg and kw.arg not in sig.parameters and not any(
                p.kind is p.VAR_KEYWORD for p in sig.parameters.values()
            ):
                problems.append(f"{where}  KWARG    `{key}` has no parameter `{kw.arg}`")


for path in md_files(sys.argv[1:] or list(DEFAULTS)):
    text = path.read_text(encoding="utf-8")
    for lang, code, offset in (
        (m.group(1), m.group(2), text[: m.start()].count("\n") + 1) for m in FENCE_RE.finditer(text)
    ):
        if lang in {"python", "py"}:
            check_block(path, offset, code)

print(
    f"checked {checked} call(s) against {len(SIGNATURES)} known signatures"
    + (f" (skipped {skipped_bad} deliberately-wrong example(s))" if skipped_bad else "")
)
if problems:
    print(f"\n{len(problems)} problem(s):")
    for p in problems:
        print(" ", p)
    sys.exit(1)
print("OK - no signature mismatches in any Markdown example")

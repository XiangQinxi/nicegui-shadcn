"""Check that the public API is documented in the format Sphinx autodoc reads.

The API reference under ``docs/api/`` is nothing but ``automodule`` directives, so
its quality is exactly the quality of the docstrings in ``nicegui_shadcn/``. This
script is the guard: it walks the same public surface autodoc walks and reports
anything that would render as a bare signature.

What it enforces:

* every module, public class, public factory and public method has a docstring;
* every parameter of every public class ``__init__`` and every factory is
  documented with a reStructuredText field, ``:param name: ...``;
* no ``:param:`` names a parameter that does not exist - autodoc drops those
  silently, which is how a renamed argument turns into missing documentation;
* the docstrings stay in one format: reST field lists, not a stray Google
  (``Args:``) or NumPy (``Parameters`` underline) section;
* every public module is named by an ``automodule`` directive under ``docs/api/``,
  so adding a module cannot silently leave it out of the reference.

    python tests/check_docstrings.py            # the whole public surface
    python tests/check_docstrings.py docs       # also re-read the API pages from here

Exit code 0 means the API reference can be generated from the docstrings alone.
"""
from __future__ import annotations

import importlib
import inspect
import re
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import nicegui_shadcn  # noqa: E402
from nicegui_shadcn import icons, shadcn, theme, theming  # noqa: E402

#: Bound parameters autodoc never renders, so they are not required to be documented.
IMPLICIT = {"self", "cls"}

PARAM_RE = re.compile(r"^:param\s+(?:\S+\s+)?(\*{0,2}[A-Za-z_][\w]*)\s*:", re.M)
#: autodoc reads nothing from these, so a docstring using them is half-invisible.
GOOGLE_RE = re.compile(r"^\s*(Args|Arguments|Returns|Raises|Yields|Attributes|Examples)\s*:\s*$", re.M)
NUMPY_RE = re.compile(r"^\s*(Parameters|Returns|Raises|Yields|Attributes)\s*\n\s*-{3,}\s*$", re.M)
AUTOMODULE_RE = re.compile(r"^\s*\.\.\s+automodule::\s*(nicegui_shadcn[\w.]*)", re.M)

problems: list[str] = []
counts = {"modules": 0, "classes": 0, "functions": 0, "methods": 0, "parameters": 0}


def show(obj: object) -> str:
    """``module.qualname``, or the module name for a module."""
    if isinstance(obj, ModuleType):
        return obj.__name__
    return f"{obj.__module__}.{obj.__qualname__}"  # type: ignore[attr-defined]


def parameters_of(callable_) -> tuple[list[str], set[str]]:
    """Return the required parameter names, plus the accepted ``*args`` / ``**kwargs``.

    ``self``/``cls`` are dropped. A catch-all is optional to document: writing
    ``:param kwargs:`` is useful, but demanding one on all fifty-odd classes that
    forward to ``ShadcnElement`` would be noise.
    """
    try:
        signature = inspect.signature(callable_)
    except (TypeError, ValueError):
        return [], set()
    named: list[str] = []
    variadic: set[str] = set()
    for name, parameter in signature.parameters.items():
        if name in IMPLICIT:
            continue
        if parameter.kind in (parameter.VAR_POSITIONAL, parameter.VAR_KEYWORD):
            variadic.add(name)
        else:
            named.append(name)
    return named, variadic


def documented(doc: str | None) -> set[str]:
    return {match.group(1).lstrip("*") for match in PARAM_RE.finditer(doc or "")}


def check_docstring(owner: object, label: str, doc: str | None) -> str:
    """Return the docstring, complaining about missing text and foreign formats."""
    if not doc or not doc.strip():
        problems.append(f"{label}  MISSING  no docstring")
        return ""
    if GOOGLE_RE.search(doc):
        section = GOOGLE_RE.search(doc).group(1)  # type: ignore[union-attr]
        problems.append(
            f"{label}  FORMAT   Google-style `{section}:` section; "
            "the house style is `:param name: ...` field lists"
        )
    if NUMPY_RE.search(doc):
        section = NUMPY_RE.search(doc).group(1)  # type: ignore[union-attr]
        problems.append(
            f"{label}  FORMAT   NumPy-style `{section}` section; "
            "the house style is `:param name: ...` field lists"
        )
    return doc


def check_parameters(owner: object, callable_, label: str, doc: str) -> None:
    """Compare the signature against the ``:param:`` fields in both directions."""
    expected, variadic = parameters_of(callable_)
    found = documented(doc)
    counts["parameters"] += len(expected)

    missing = [name for name in expected if name not in found]
    if missing:
        problems.append(f"{label}  UNDOCUMENTED  parameter(s): {', '.join(missing)}")

    # A typo or a stale name after a rename: autodoc drops the field and the
    # parameter silently loses its description.
    unknown = sorted(found - set(expected) - variadic)
    if unknown:
        problems.append(
            f"{label}  STALE  `:param {'`, `:param '.join(unknown)}` matches no parameter"
        )


def check_callable(obj: object, label: str, kind: str) -> None:
    doc = check_docstring(obj, label, inspect.getdoc(obj))
    counts[kind] += 1
    if doc:
        check_parameters(obj, obj, label, doc)


def check_class(cls: type, label: str) -> None:
    doc = check_docstring(cls, label, inspect.getdoc(cls))
    counts["classes"] += 1
    if not doc:
        return
    # Parameters live in the class docstring because autoclass_content = 'class'.
    check_parameters(cls, cls.__init__, label, doc)
    for name, member in vars(cls).items():
        if name.startswith("_") or not inspect.isfunction(member):
            continue
        # Only what this class defines itself. Inherited members belong to the
        # class that defines them - and inherited NiceGUI members are documented
        # upstream, often with signatures of their own - so neither is checked twice.
        if getattr(member, "__module__", "") != cls.__module__:
            continue
        method_label = f"{label}.{name}"
        method_doc = check_docstring(member, method_label, inspect.getdoc(member))
        counts["methods"] += 1
        if method_doc:
            check_parameters(member, member, method_label, method_doc)


def public_members(module: ModuleType) -> list[tuple[str, object]]:
    names = getattr(module, "__all__", None) or [n for n in vars(module) if not n.startswith("_")]
    members = []
    for name in names:
        obj = getattr(module, name, None)
        if obj is None or inspect.ismodule(obj):
            continue
        if not (inspect.isclass(obj) or inspect.isfunction(obj)):
            continue
        # Re-exports show up here; document each object where it is defined.
        if getattr(obj, "__module__", "").startswith("nicegui_shadcn"):
            members.append((name, obj))
    return members


# -- the public surface, exactly as docs/api/ renders it ----------------------

seen: set[int] = set()
for name in nicegui_shadcn.__all__:
    obj = getattr(nicegui_shadcn, name, None)
    if obj is None:
        continue
    if isinstance(obj, ModuleType):
        continue
    if id(obj) in seen:
        continue
    seen.add(id(obj))
    if inspect.isclass(obj):
        check_class(obj, show(obj))
    elif inspect.isfunction(obj):
        check_callable(obj, show(obj), "functions")

for module in (shadcn, icons, theme, theming):
    for name, obj in public_members(module):
        if id(obj) in seen:
            continue
        seen.add(id(obj))
        if inspect.isclass(obj):
            check_class(obj, show(obj))
        else:
            check_callable(obj, show(obj), "functions")

# Every module that defines part of that surface has a docstring of its own.
defined_in = {
    getattr(obj, "__module__", "")
    for obj in list(vars(shadcn).values())
    if getattr(obj, "__module__", "").startswith("nicegui_shadcn")
}
# ``nicegui_shadcn.elements.icon`` exports a single factory and the package
# attribute of the same name shadows the module, so it never shows up as an
# object above; the module names in ``__all__`` cover that case.
surface_modules = {name for name in defined_in if name and not name.endswith("__init__")}
for name in nicegui_shadcn.__all__:
    obj = getattr(nicegui_shadcn, name, None)
    if not isinstance(obj, ModuleType):
        continue
    # A module earns a page when it defines something itself. ``shadcn`` is a pure
    # re-export facade, so ``automodule`` would render it empty; its contents are
    # documented on the pages of the modules that define them.
    if any(getattr(member, "__module__", None) == obj.__name__ for member in vars(obj).values()):
        surface_modules.add(obj.__name__)

for module_name in sorted(surface_modules):
    try:
        module = importlib.import_module(module_name)
    except ImportError as error:  # pragma: no cover - import-time breakage
        problems.append(f"{module_name}  IMPORT   {error}")
        continue
    counts["modules"] += 1
    check_docstring(module, module_name, inspect.getdoc(module))

# -- the API pages must actually render all of it -----------------------------

docs_root = ROOT / (sys.argv[1] if len(sys.argv) > 1 else "docs")
api_pages = sorted((docs_root / "api").glob("*.md"))
if not api_pages:
    problems.append(f"{docs_root / 'api'}  MISSING  no API reference pages found")
else:
    text = "\n".join(page.read_text(encoding="utf-8") for page in api_pages)
    rendered = set(AUTOMODULE_RE.findall(text))
    for module_name in sorted(surface_modules):
        if module_name in rendered:
            continue
        problems.append(f"{module_name}  NOT-RENDERED  no `automodule` directive in docs/api/")
    for module_name in sorted(rendered - surface_modules):
        problems.append(f"{module_name}  GHOST  named by docs/api/ but not part of the public surface")

print(
    "checked {modules} module(s), {classes} class(es), {functions} function(s), "
    "{methods} method(s), {parameters} parameter(s)".format(**counts)
)
if problems:
    print(f"\n{len(problems)} problem(s):")
    for problem in problems:
        print(" ", problem)
    sys.exit(1)
print("OK - every public parameter is documented in the format autodoc reads")

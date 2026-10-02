# AGENT.md

Notes for anyone — human or agent — changing this repository.

`nicegui-shadcn` is a [NiceGUI](https://nicegui.io) extension that provides shadcn/ui
components. It is unusual in one respect: it has **no build step for the user**, which means
the Tailwind stylesheet and the Vue component bundle are compiled here and committed. Most
of the rules below exist to keep that illusion intact.

Read `README.md` for what the library does. This file is about how to change it without
breaking it.

---

## 1. Layout: build inputs vs runtime assets

The split is deliberate and load-bearing. `frontend/` is **not** part of the importable
package, so importing `nicegui_shadcn` never reads a `.css` or a `.js` source file.

| Path | Role | Ships in |
| --- | --- | --- |
| `nicegui_shadcn/*.py` | Runtime: `theme.py`, `shadcn.py`, `icons.py`, `_tw_merge.py` | wheel + sdist |
| `nicegui_shadcn/elements/*.py` | Runtime: one module per component group | wheel + sdist |
| `nicegui_shadcn/elements/*.vue` | Runtime: templates, parsed by NiceGUI's own `VBuild` | wheel + sdist |
| `nicegui_shadcn/static/shadcn.css` | Runtime: compiled stylesheet (~191 kB) | wheel + sdist |
| `nicegui_shadcn/static/vendor/reka-ui.js` | Runtime: tree-shaken reka-ui bundle (~283 kB) | wheel + sdist |
| `frontend/tailwind.css` | **Build input**: Tailwind v4 source, design tokens, `@source` globs | sdist |
| `frontend/vendor/reka-entry.js` | **Build input**: esbuild entry for the reka-ui bundle | sdist |
| `examples/demo.py` | **Build input + dev aid**: the demo the browser test drives | sdist |
| `tests/` | Dev | sdist |
| `package.json`, `package-lock.json` | Dev: pins the Tailwind CLI and esbuild | sdist |
| `node_modules/` | Installed, never shipped | — |
| `AGENT.md` | This file | sdist |

If you add a runtime file, check `[tool.poetry].include` in `pyproject.toml`.

---

## 2. The edit → build → verify loop

```bash
npm install          # once
npm run build        # = build:css + build:vendor, ~250 ms total
```

**Rebuild the CSS after touching any `.py` or `.vue` under `nicegui_shadcn/`.** Tailwind
only emits utilities it can see, so a new class in a Python constant or a `.vue` template
does not exist until you rebuild. Forgetting this is the single most common way to ship a
component that renders unstyled.

Then verify, in this order — each layer catches what the one before it cannot:

```bash
python tests/test_tw_merge.py     # 37 cases: cn() conflict resolution, no NiceGUI needed
python tests/test_render.py       # 30 checks: every component renders server-side, no browser
python tests/audit_classes.py     # 223 tokens: every class used in Python exists in the CSS
python examples/demo.py           # start the demo (port 8123), then:
node tests/visual_check.mjs http://127.0.0.1:8123/   # 34 checks in headless Edge
```

- `tests/test_render.py` derives one `<stem> registered` check per `*.vue` file, so a new
  component is covered as soon as the file exists.
- `tests/audit_classes.py` is the only guard against Tailwind's **silent** failure mode: an
  unresolvable candidate is dropped without a warning, and you only see the damage as an
  unstyled element in a browser. Add a component, rebuild, and run it.
- `tests/visual_check.mjs` asserts computed styles, so it is the only layer that can tell
  whether a design *token* — not merely a class name — reached the element. It writes
  `_shot-light.png` / `_shot-dark.png`; set `SHADCN_SHOT_DIR` to redirect them.

`examples/demo.py` runs with `reload=False`, so **restart it after every code change**
otherwise the browser test checks the previous build.

The bundled browser tools are not always available in this environment; the Playwright +
headless Edge path in `tests/visual_check.mjs` is the supported way to look at a page.
It already knows the Edge/Chrome paths to try.

---

## 3. NiceGUI extension contract

Everything here was read out of NiceGUI 3.x and is easy to get wrong. Paths are under
`C:\Python\Py313\Lib\site-packages\nicegui` in this environment.

### Registering a component

`Element.__init_subclass__(cls, *, component, dependencies, esm, default_classes,
default_style, default_props)` (`element.py:92-131`). `component` and `dependencies` are
globs resolved **relative to the file that defines the subclass**, which is why every
component module carries its own `.vue` next to it.

### What `VBuild` will and will not accept

`vbuild.py` is a ~100-line `HTMLParser`, **not** a Vue SFC compiler. Its limits shape every
`.vue` file in this repo:

- Exactly **one top-level tag** inside `<template>`, or it raises
  `ValueError('File has more than one top level tag')`.
- **`<script setup>` does not work.** Only an Options API `export default {...}` is read.
- **Nested `<template>` truncates the component.** `handle_endtag` closes the captured
  template at the *first* `</template>` it sees, without checking nesting level, so
  `<template v-for>` / `<template #slot>` silently cuts the rest of the markup off.
  Write `v-for` on a real element, or use `<component :is>`.
- Void tags (`input`, `img`, `br`, `hr`, …) are not level-counted, so an `<input>` root is
  legal.
- The `<script>` block is served verbatim as an ES module and **must have a default
  export**; `import` statements work.
- Scoped `<style>` selectors are rewritten to `*[data-<name>]`.

### Naming rules

- The file **stem** is used as a raw JavaScript identifier (`import { default as NAME } from
  …`), so **no hyphens** — hence `shadcn_tabs_list.vue`, never `shadcn-tabs-list.vue`.
- Stems must be **globally unique** across both `.vue` and `.js` components
  (`Component._names` is a shared `ClassVar` with an `assert`).
- All components are prefixed `shadcn_` for that reason.

### The `data-<name>` marker

`VBuild` puts `data-<stem>` on the **first tag of the template**. If the root is a fragment
(a reka `*Root`, or a `*Portal`), the attribute is dropped and your mount assertions fail.
Two consequences:

- Put an explicit marker on the meaningful element:
  `data-shadcn_select`, `data-shadcn_dialog_content`, `data-shadcn_popover_content`,
  `data-shadcn_dropdown_menu`.
- A fragment root needs `inheritAttrs: false` in `export default`, otherwise Vue warns about
  extraneous non-prop attributes. Use `v-bind="$attrs"` on the element that should receive
  the caller's classes.

### Props and events

- `element._props` entries become **real Vue props** on the resolved component
  (`static/nicegui.js:230-325`), camelized by Vue: Python `model-value` → `modelValue`.
- Python event names go through `event_type_to_camel_case`, and the client only
  capitalises the first letter, so `self.on('update:model-value', …)` becomes
  `onUpdate:modelValue` — exactly what `emit('update:modelValue', v)` looks up.
- A component that emits a **single** value arrives server-side as that value, not a list
  (`client.py:347-349` unwraps `len(args) == 1`).
- `ValueElement` uses `VALUE_PROP = 'model-value'`; set `LOOPBACK = False` when the
  component writes the value back itself (see `shadcn_form.py`).
- **Declare every prop you pass.** An undeclared prop falls through to the DOM; NiceGUI's
  own `loopback` prop once leaked onto the select trigger as `<button loopback="true">`
  until `shadcn_select.vue` declared it.

### Text and children

`renderRecursively` unshifts `element.text` **before** the children of the default slot.
So an element's own `_text` always renders first — a Button cannot use `_text` for its
label if it wants an icon on the left. Build the label as a child element instead.

Use `elements/base.py:Text` (a `<span>`) rather than `ui.label` (a `<div>`) for anything
inside a `<button>`; a `<div>` in a button is invalid HTML.

### Page-level registration

`theme.py` does three things at import time, all of which must happen before the first
component renders:

1. `app.add_static_files('/_nicegui_shadcn', …)`;
2. `register_importmap_override('reka-ui', …)` so `.vue` scripts can
   `import { … } from 'reka-ui'`;
3. `ui.add_head_html('<link rel="stylesheet" …>', shared=True)`.

Use a `<link>`, **not** `ui.add_css`. `add_css` inlines the stylesheet into an
`addStyle(...)` JavaScript call, so it only lands after the socket handshake — a visible
flash of unstyled content on every reload. `shared=True` is what makes the call legal
outside a client context (import time).

Keep `vue` **external** in the reka-ui bundle (`esbuild --external:vue`). NiceGUI already
puts its own Vue 3.5 on the import map; a second copy breaks `provide`/`inject` and
`Teleport` across components.

---

## 4. Tailwind and the cascade

NiceGUI declares the layer order once, in `templates/index.html:13`:

```
@layer theme, base, quasar, nicegui, components, utilities, overrides, quasar_importants;
```

Everything we emit joins those layers.

- **Import `utilities` with `layer(utilities) important`.** `quasar.important.css` lands in
  the *last* layer and contains `.bg-primary { background: var(--q-primary) !important }`.
  Layer precedence is reversed for important declarations, so making ours important too is
  the only way `shadcn.button()` comes out shadcn-black instead of Quasar-blue.
- **Do not import Tailwind's preflight.** Quasar already normalises; a second reset fights
  it. The one preflight rule we need — `[hidden] { display: none !important }`, used by
  mounted-but-closed panels — is added by hand in `@layer base`.
- Bind the dark variant to the class NiceGUI already toggles:
  `@custom-variant dark (&:where(body.body--dark, body.body--dark *));`
- Expose design tokens through `@theme inline { --color-primary: var(--primary); … }` so
  `bg-primary` / `text-muted-foreground` resolve to the shadcn variables.
- The build uses `source(none)` plus explicit `@source` globs, so the compiled CSS is a
  pure function of the checkout's `.py`/`.vue` files and does not drift with where it was
  built.
- Runtime `classes=` strings are covered by `@source inline(...)` blocks. That vocabulary is
  a **deliberate subset**: semantic colours plus common layout/spacing/typography. Raw
  palette colours (`bg-blue-600`) are not generated. Extending it means adding to the
  matrix and rebuilding; the README documents the user-facing workflow.

### Where class strings live

**All CSS classes live in Python**, in module-level constants or `default_classes`. The
`.vue` templates contain no `class="…"` of their own except `:class` bindings fed from a
prop. That is what makes `classes=` mergeable and auditable.

`tests/audit_classes.py` encodes the conventions it depends on:

- constants must be named `_?[A-Z][A-Z0-9_]*_(BASE|CLASSES|VARIANTS|SIZES)`;
- it parses Python with `ast`, not regex, and reads `default_classes=`, `classes=` and
  `.classes(...)` keyword arguments;
- `CLASS_ATTR_RE` uses a lookbehind so `:class` / `v-bind:class` (JavaScript expressions) are
  ignored.

If you rename a constant or move a class into a template, the audit will either go quiet or
go red — check it.

---

## 5. reka-ui

The bundle is built from `frontend/vendor/reka-entry.js`, which re-exports **only** the
primitives we wrap so esbuild can tree-shake the rest. Rebuild it after changing that file:

```bash
npm run build:vendor
```

Two things worth knowing:

- **`provide`/`inject` does not survive a NiceGUI slot for `TabsList` → `TabsTrigger`.**
  reka's `TabsTrigger` uses `RovingFocusItem` unconditionally and throws
  `` Injection `Symbol(RovingFocusGroupContext)` not found ``. Every *other* cross-boundary
  inject works (dialog, popover, dropdown, tooltip, select, accordion). The fix was to make
  the tab bar data-driven: `shadcn_tabs_list.vue` takes a `tabs` array prop and generates
  the triggers itself, which keeps reka's real roving-focus/arrow-key behaviour inside one
  component tree. Anything else that needs a context provided by a sibling should follow
  the same pattern.
- **Force-mounted content is not hidden by reka.** It only sets `data-state`, never
  `hidden`. The children of `TabsContent`/`AccordionContent` stay mounted on purpose (so a
  server-side update always finds its element), and hiding is done with
  `data-[state=inactive]:hidden` / `data-[state=closed]:hidden`. The cost is that the
  accordion has no *closing* animation.
- `PinInputSeparator` does not exist in reka-ui 2.10.5. Check the export list before adding
  an import; a bad import fails the esbuild step with
  `No matching export in "node_modules/reka-ui/dist/index.js"`.

---

## 6. Python API conventions

- **`cn()` semantics are mandatory for components that take `classes=`.** NiceGUI's
  `.classes()` *appends*, so `shadcn.button('Save', classes='bg-destructive')` would emit
  both `bg-primary` and `bg-destructive` and let CSS source order decide. `ShadcnElement`
  merges through `_tw_merge.tw_merge` so the caller wins.
- In `_tw_merge`, always slice with `b[len(prefix):]`. Two bugs came from hand-counted
  indices (`b[6:]` for `border-`, `b[7:]` for `rounded-`), and both made unrelated utilities
  share a conflict group.
- Validate enum-ish arguments with `option(kind, value, options)` so the error names the
  valid choices.
- Expose a lowercase factory (`shadcn.button(...)`) and keep the class in the same module.
  `elements/__init__.py` builds `__all__` from each module's `__all__` **before** the star
  imports, because `from .icon import *` rebinds the name `icon` from the module to the
  factory.
- Icons are inlined in `icons.py` (39 glyphs), not bundled from `lucide-vue-next`; a new
  glyph is one entry in `_ICONS`.

---

## 7. Packaging

Poetry, PEP 621 metadata, `poetry-core` backend.

- `requires-python` **must** carry an upper bound (`>=3.10,<4.0`). A bare `>=3.10` makes
  `poetry lock` fail with *"a possible solution would be to set the `python` property to
  `>=3.10,<4`"*.
- `license = "MIT"` + `license-files = ["LICENSE"]` (PEP 639). Do not add a
  `License ::` classifier; it conflicts.
- Poetry honours `.gitignore` when building the sdist. Anything you add there also
  disappears from the source distribution — that is how `node_modules/` and `dist/` stay
  out.
- **Poetry 2.4.1 defines no `testpypi` repository.** `poetry publish -r testpypi` fails with
  `Repository testpypi is not defined` until you run
  `poetry config repositories.testpypi https://test.pypi.org/legacy/`.
- `poetry publish` uploads whatever is in `dist/`; it does not rebuild unless you pass
  `--build`. Use `poetry publish --dry-run` to check repository resolution and the artifact
  list without credentials.
- After changing the runtime assets, rebuild the wheel and **verify it in a fresh venv**.
  Run the check with a working directory outside the repository, or `C:\dsh` shadows
  site-packages on `sys.path` and you will happily test the checkout instead of the wheel.

---

## 8. Pitfalls already paid for

A short list of mistakes that cost real time here. Most were invisible until a browser
looked at the result.

1. **Tailwind drops unknown classes silently.** A typo produces no warning and no rule.
   `tests/audit_classes.py` exists for exactly this.
2. **`getComputedStyle` reports a blockified `display`.** A button that is a flex item
   reports `flex` even though its class list says `inline-flex`, and removing the class
   gives `block`. Assert `flex` *or* `inline-flex`; the class list is the source of truth.
3. **A page-level overflow check misses per-element overflow.** A `size="icon"` button with
   a text label overflowed by 22 px while `document.scrollWidth` was clean; the check had to
   compare each element's `scrollWidth` against its `clientWidth`. The Button now degrades
   to `sr-only` + `aria-label`.
4. **Assign text to the element that should show it.** `Avatar.__init__` once did
   `self._text = fallback`, which put "CN" in the outer container next to the circle instead
   of inside it. For a child element, assign to the child.
5. **Compare tokens, not colours.** Assertions convert through a probe element
   (`background-color: var(--primary)`) and compare computed strings; Chromium echoes
   `oklch()` back unchanged, so the test proves *which token* was used rather than that some
   dark colour appeared.
6. **`Button` has no `.vue`.** It renders a native `<button>` (`tag='button'`). Asserting
   `tpl-shadcn_button` is wrong; the repository has exactly 24 `.vue` files, which is why
   `test_render.py` has 30 checks (6 static + 24).
7. **NiceGUI 3.x removed `classes=` / `style=` / `props=` from `Element.__init__`.** Set them
   through `_props` / `.classes()` / `.style()` after construction, as `base.py` does.
8. **`add_slot('default', template)` cannot inject markup.** `_collect_slot_dict()` excludes
   the default slot, so a default-slot template is never sent to the client. Build real
   child elements.

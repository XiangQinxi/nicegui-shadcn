"""A small, dependency-free port of the parts of *tailwind-merge* that
nicegui-shadcn needs.

shadcn's public API is built around ``cn()``: a component has a set of default
classes and the caller may pass more classes that are supposed to *win*.  In
CSS the order of the class attribute is irrelevant -- which rule wins is decided
by the order of the rules inside the stylesheet -- so "let the caller win" has
to be implemented by *removing* the conflicting default class before the class
list ever reaches the DOM.

That removal is exactly what this module does::

    >>> tw_merge('h-9 rounded-md bg-primary px-4', 'bg-destructive rounded-full')
    'h-9 bg-destructive px-4 rounded-full'

The implementation is deliberately conservative.  It splits every class into a
variant prefix and a base utility, maps the base utility onto a *conflict
group*, and gives that group an ancestor *path* inside its family::

    p       -> ('p',)            px       -> ('p', 'x')
    pt      -> ('p', 'y', 't')   size     -> ('size',)
    w       -> ('size', 'w')     inset    -> ('inset',)
    left    -> ('inset', 'x', 'left')
    rounded -> ('rounded',)      rounded-tl -> ('rounded', 't', 'l')

A later class then evicts every earlier class *of the same variant* whose path
starts with its own path.  The relation is directional, exactly as in
tailwind-merge: a shorthand removes the per-axis classes it covers
(``px-4 py-2`` + ``p-4`` -> ``p-4``), while a narrower class never removes an
earlier shorthand (``p-4`` + ``px-2`` -> ``p-4 px-2``).  Siblings such as
``w-4 h-2`` or ``left-2 inset-y-4`` are both kept.

Anything it does not recognise is treated as its own single-segment group, so
unknown classes are never dropped -- they are only de-duplicated.  That
de-duplication is the one place this port is deliberately stricter than
tailwind-merge, which would emit an unrecognised class verbatim twice.
"""

from __future__ import annotations

__all__ = ['tw_merge', 'tw_join']

# --------------------------------------------------------------------------- #
# static utilities: class name -> conflict group
# --------------------------------------------------------------------------- #

_STATIC = {
    # position
    'static': 'position', 'fixed': 'position', 'absolute': 'position',
    'relative': 'position', 'sticky': 'position',
    # display
    'block': 'display', 'inline-block': 'display', 'inline': 'display',
    'flex': 'display', 'inline-flex': 'display', 'table': 'display',
    'inline-table': 'display', 'table-caption': 'display',
    'table-cell': 'display', 'table-column': 'display',
    'table-column-group': 'display', 'table-footer-group': 'display',
    'table-header-group': 'display', 'table-row-group': 'display',
    'table-row': 'display', 'flow-root': 'display', 'grid': 'display',
    'inline-grid': 'display', 'contents': 'display', 'list-item': 'display',
    'hidden': 'display',
    # flex / grid child
    'flex-row': 'flex-direction', 'flex-row-reverse': 'flex-direction',
    'flex-col': 'flex-direction', 'flex-col-reverse': 'flex-direction',
    'flex-wrap': 'flex-wrap', 'flex-wrap-reverse': 'flex-wrap',
    'flex-nowrap': 'flex-wrap',
    'grow': 'grow', 'grow-0': 'grow', 'shrink': 'shrink', 'shrink-0': 'shrink',
    # text alignment
    'text-left': 'text-align', 'text-center': 'text-align',
    'text-right': 'text-align', 'text-justify': 'text-align',
    'text-start': 'text-align', 'text-end': 'text-align',
    # text overflow / wrapping
    'truncate': 'text-overflow', 'text-ellipsis': 'text-overflow',
    'text-clip': 'text-overflow',
    'text-wrap': 'text-wrap', 'text-nowrap': 'text-wrap',
    'text-balance': 'text-wrap', 'text-pretty': 'text-wrap',
    # misc
    'uppercase': 'text-transform', 'lowercase': 'text-transform',
    'capitalize': 'text-transform', 'normal-case': 'text-transform',
    'italic': 'font-style', 'not-italic': 'font-style',
    'underline': 'text-decoration', 'overline': 'text-decoration',
    'line-through': 'text-decoration', 'no-underline': 'text-decoration',
    'antialiased': 'font-smoothing', 'subpixel-antialiased': 'font-smoothing',
    'sr-only': 'sr', 'not-sr-only': 'sr',
    # bare utilities that only set a width/style (their "-value" forms are
    # handled by the prefix table further down)
    'border': 'border-w', 'ring': 'ring-w', 'shadow': 'shadow',
    'outline': 'outline-style',
    'border-collapse': 'border-collapse', 'border-separate': 'border-collapse',
    'outline-none': 'outline-style', 'outline-hidden': 'outline-style',
    'ring-inset': 'ring-inset',
    'transform': 'transform', 'transform-none': 'transform',
    'transition': 'transition', 'transition-none': 'transition',
    'transition-all': 'transition', 'transition-colors': 'transition',
    'transition-opacity': 'transition', 'transition-shadow': 'transition',
    'transition-transform': 'transition',
    'shadow-none': 'shadow', 'shadow-inner': 'shadow',
}

# --------------------------------------------------------------------------- #
# utilities that take a value: "prefix-value" -> conflict group
# --------------------------------------------------------------------------- #

_PREFIX = {
    'p': 'p', 'px': 'px', 'py': 'py', 'pt': 'pt', 'pr': 'pr', 'pb': 'pb',
    'pl': 'pl', 'ps': 'ps', 'pe': 'pe',
    'm': 'm', 'mx': 'mx', 'my': 'my', 'mt': 'mt', 'mr': 'mr', 'mb': 'mb',
    'ml': 'ml', 'ms': 'ms', 'me': 'me',
    'w': 'w', 'h': 'h', 'size': 'size',
    'min-w': 'min-w', 'max-w': 'max-w', 'min-h': 'min-h', 'max-h': 'max-h',
    'gap': 'gap', 'gap-x': 'gap-x', 'gap-y': 'gap-y',
    'items': 'items', 'justify': 'justify', 'justify-items': 'justify-items',
    'justify-self': 'justify-self', 'content': 'align-content',
    'self': 'self', 'place-items': 'place-items',
    'place-content': 'place-content', 'place-self': 'place-self',
    'z': 'z', 'opacity': 'opacity',
    'overflow': 'overflow', 'overflow-x': 'overflow-x', 'overflow-y': 'overflow-y',
    'inset': 'inset', 'inset-x': 'inset-x', 'inset-y': 'inset-y',
    'top': 'top', 'right': 'right', 'bottom': 'bottom', 'left': 'left',
    'start': 'start', 'end': 'end',
    'translate-x': 'translate-x', 'translate-y': 'translate-y',
    'scale': 'scale', 'scale-x': 'scale-x', 'scale-y': 'scale-y',
    'rotate': 'rotate', 'origin': 'origin',
    'grid-cols': 'grid-cols', 'grid-rows': 'grid-rows',
    'col': 'col', 'col-span': 'col-span', 'col-start': 'col-start',
    'col-end': 'col-end', 'row': 'row', 'row-span': 'row-span',
    'row-start': 'row-start', 'row-end': 'row-end',
    'leading': 'leading', 'tracking': 'tracking',
    'cursor': 'cursor', 'select': 'select', 'pointer-events': 'pointer-events',
    'resize': 'resize', 'list': 'list-style-type',
    'duration': 'duration', 'delay': 'delay', 'ease': 'ease',
    'animate': 'animate', 'aspect': 'aspect',
    'object': 'object-fit', 'object-position': 'object-position',
    'fill': 'fill', 'stroke': 'stroke', 'stroke-width': 'stroke-width',
    'divide-x': 'divide-x', 'divide-y': 'divide-y',
    'space-x': 'space-x', 'space-y': 'space-y',
    'basis': 'basis', 'grow': 'grow', 'shrink': 'shrink',
    'flex': 'flex', 'order': 'order',
    'whitespace': 'whitespace', 'break': 'break',
    'line-clamp': 'line-clamp', 'indent': 'indent',
    'align': 'vertical-align', 'table': 'table-layout',
    'bg': 'bg-color', 'text': 'text-color', 'font': 'font-family',
    'border': 'border-color', 'rounded': 'rounded',
    'shadow': 'shadow', 'ring': 'ring-color', 'outline': 'outline-color',
    'decoration': 'text-decoration-color', 'accent': 'accent-color',
    'caret': 'caret-color', 'blur': 'blur', 'brightness': 'brightness',
    'contrast': 'contrast', 'saturate': 'saturate', 'hue-rotate': 'hue-rotate',
    'grayscale': 'grayscale', 'invert': 'invert', 'sepia': 'sepia',
    'backdrop-blur': 'backdrop-blur', 'will-change': 'will-change',
}

_TEXT_SIZES = {'xs', 'sm', 'base', 'lg', 'xl', '2xl', '3xl', '4xl', '5xl',
               '6xl', '7xl', '8xl', '9xl'}
_BG_MODES = {'fixed', 'local', 'scroll', 'clip', 'origin', 'repeat',
             'no-repeat', 'repeat-x', 'repeat-y', 'cover', 'contain', 'auto',
             'center', 'top', 'bottom', 'left', 'right', 'left-top',
             'left-bottom', 'right-top', 'right-bottom', 'top-left',
             'top-right', 'bottom-left', 'bottom-right', 'none',
             'gradient-to-t', 'gradient-to-tr', 'gradient-to-r',
             'gradient-to-br', 'gradient-to-b', 'gradient-to-bl',
             'gradient-to-l', 'gradient-to-tl', 'clip-text', 'clip-border',
             'clip-padding', 'clip-content'}
_RADIUS_SIZES = {'none', 'xs', 'sm', 'md', 'lg', 'xl', '2xl', '3xl', '4xl',
                 'full'}
_BORDER_SIDES = {'x', 'y', 't', 'r', 'b', 'l', 's', 'e'}
_RING_WIDTHS = {'0', '1', '2', '4', '8', 'inset'}
_SHADOW_SIZES = {'sm', 'md', 'lg', 'xl', '2xl', 'inner', 'none'}
_FONT_WEIGHTS = {'thin', 'extralight', 'light', 'normal', 'medium', 'semibold',
                 'bold', 'extrabold', 'black'}
_FONT_FAMILIES = {'sans', 'serif', 'mono'}

# The longest prefix wins, so that ``text-`` is not matched before ``text-balance``.
_PREFIX_KEYS_BY_LENGTH = sorted(_PREFIX, key=len, reverse=True)

# --------------------------------------------------------------------------- #
# conflict-group hierarchy: group -> its ancestor path inside the family
# --------------------------------------------------------------------------- #
# Tailwind's conflict rules are directional, not symmetric: a *shorthand* (a
# parent, e.g. ``p``/``size``/``inset``/``rounded``) evicts an earlier class
# that covers only part of it, but a narrower class never evicts an earlier
# shorthand.  Each group therefore gets a path instead of a flat identity, and
# ``tw_merge`` drops an earlier class when its path starts with the new one's.
#
# Groups absent from this table are their own single-segment family: they are
# only ever evicted by an identical group.  Deliberately excluded from the
# ``size`` family are ``min-w``/``max-w``/``min-h``/``max-h``, which tailwind
# keeps alongside ``w``/``h``.
_GROUP_PATHS: dict[str, tuple[str, ...]] = {
    # padding ------------------------------------------------------------- #
    'p': ('p',),
    'px': ('p', 'x'), 'py': ('p', 'y'),
    'ps': ('p', 'x', 's'), 'pe': ('p', 'x', 'e'),
    'pl': ('p', 'x', 'l'), 'pr': ('p', 'x', 'r'),
    'pt': ('p', 'y', 't'), 'pb': ('p', 'y', 'b'),
    # margin -------------------------------------------------------------- #
    'm': ('m',),
    'mx': ('m', 'x'), 'my': ('m', 'y'),
    'ms': ('m', 'x', 's'), 'me': ('m', 'x', 'e'),
    'ml': ('m', 'x', 'l'), 'mr': ('m', 'x', 'r'),
    'mt': ('m', 'y', 't'), 'mb': ('m', 'y', 'b'),
    # width / height hang off ``size`` ------------------------------------ #
    'size': ('size',), 'w': ('size', 'w'), 'h': ('size', 'h'),
    # gap ----------------------------------------------------------------- #
    'gap': ('gap',), 'gap-x': ('gap', 'x'), 'gap-y': ('gap', 'y'),
    # inset: the physical sides sit below the x/y axes -------------------- #
    'inset': ('inset',),
    'inset-x': ('inset', 'x'), 'inset-y': ('inset', 'y'),
    'left': ('inset', 'x', 'left'), 'right': ('inset', 'x', 'right'),
    'start': ('inset', 'x', 'start'), 'end': ('inset', 'x', 'end'),
    'top': ('inset', 'y', 'top'), 'bottom': ('inset', 'y', 'bottom'),
    # overflow ------------------------------------------------------------ #
    'overflow': ('overflow',),
    'overflow-x': ('overflow', 'x'), 'overflow-y': ('overflow', 'y'),
    # border width -------------------------------------------------------- #
    'border-w': ('border-w',),
    'border-w-x': ('border-w', 'x'), 'border-w-y': ('border-w', 'y'),
    'border-w-l': ('border-w', 'x', 'l'), 'border-w-r': ('border-w', 'x', 'r'),
    'border-w-s': ('border-w', 'x', 's'), 'border-w-e': ('border-w', 'x', 'e'),
    'border-w-t': ('border-w', 'y', 't'), 'border-w-b': ('border-w', 'y', 'b'),
    # border radius, including the two-letter corners --------------------- #
    'rounded': ('rounded',),
    'rounded-x': ('rounded', 'x'), 'rounded-y': ('rounded', 'y'),
    'rounded-t': ('rounded', 't'), 'rounded-b': ('rounded', 'b'),
    'rounded-l': ('rounded', 'l'), 'rounded-r': ('rounded', 'r'),
    'rounded-s': ('rounded', 's'), 'rounded-e': ('rounded', 'e'),
    'rounded-tl': ('rounded', 't', 'l'), 'rounded-tr': ('rounded', 't', 'r'),
    'rounded-bl': ('rounded', 'b', 'l'), 'rounded-br': ('rounded', 'b', 'r'),
    'rounded-ss': ('rounded', 's', 's'), 'rounded-se': ('rounded', 's', 'e'),
    'rounded-es': ('rounded', 'e', 's'), 'rounded-ee': ('rounded', 'e', 'e'),
}


def _path(group: str) -> tuple[str, ...]:
    """Return the ancestor path of a conflict group.

    Unknown groups become a single-segment family of their own, which keeps the
    "unknown classes are never dropped, only de-duplicated" guarantee.
    """
    return _GROUP_PATHS.get(group, (group,))


def _group(base: str) -> str:
    """Return the conflict group of a bare utility (no variants)."""
    b = base.lstrip('!')
    if b.startswith('-'):
        b = b[1:]

    if b in _STATIC:
        return _STATIC[b]
    if b in ('bg-transparent', 'bg-current', 'bg-inherit'):
        return 'bg-color'

    # explicit branch for utilities that take values
    if b.startswith('text-'):
        rest = b[5:]
        if rest in _TEXT_SIZES:
            return 'text-size'
        if rest.startswith('[') or '-' in rest:
            # text-2xl is handled above; anything else with a dash is a colour
            return 'text-color'
        return 'text-color'
    if b.startswith('bg-'):
        rest = b[3:]
        if rest in _BG_MODES or rest.startswith(('linear-', 'radial-', 'conic-')):
            return 'bg-mode'
        if rest.startswith('gradient-'):
            return 'bg-image'
        return 'bg-color'
    if b.startswith('border-'):
        rest = b[len('border-'):]
        if rest in _BORDER_SIDES:
            return f'border-w-{rest}'
        if rest[0] in _BORDER_SIDES and rest[1:2] == '-' and rest[2:].isdigit():
            return f'border-w-{rest[0]}'
        if rest == 'x' or rest.isdigit():
            return 'border-w'
        if rest in ('solid', 'dashed', 'dotted', 'double', 'hidden', 'none'):
            return 'border-style'
        return 'border-color'
    if b.startswith('rounded-'):
        rest = b[len('rounded-'):]
        # A bare radius size is a *size*, not a side.  Test it before the side
        # letters, or ``xl``, ``lg``, ``sm`` and ``xs`` are read as the sides
        # ``x``/``l``/``s``/``x`` and land in a side group that the generic
        # ``rounded`` group can never evict -- which is what made
        # ``Card(classes='rounded-full')`` silently keep its ``rounded-xl``.
        if rest in _RADIUS_SIZES:
            return 'rounded'
        side, _, size = rest.partition('-')
        if side[:1] in _BORDER_SIDES and (not size or size in _RADIUS_SIZES):
            return f'rounded-{side}'
        return 'rounded'
    if b.startswith('shadow-'):
        rest = b[7:]
        if rest in _SHADOW_SIZES:
            return 'shadow'
        return 'shadow-color'
    if b.startswith('ring-'):
        rest = b[5:]
        if rest in _RING_WIDTHS:
            return 'ring-w'
        if rest.startswith('offset-'):
            return 'ring-offset-w' if rest[7:].isdigit() else 'ring-offset-color'
        return 'ring-color'
    if b.startswith('font-'):
        rest = b[5:]
        if rest in _FONT_WEIGHTS:
            return 'font-weight'
        if rest in _FONT_FAMILIES:
            return 'font-family'
        return 'font-family'

    for prefix in _PREFIX_KEYS_BY_LENGTH:
        if b == prefix:
            return _PREFIX[prefix]
        if b.startswith(prefix + '-'):
            return _PREFIX[prefix]

    # unknown -> its own group (de-duplicate only)
    return b


def _split_variants(cls: str) -> tuple[str, str]:
    """Split ``hover:dark:bg-x`` into ``('hover:dark', 'bg-x')``."""
    depth = 0
    last = -1
    for i, ch in enumerate(cls):
        if ch == '[':
            depth += 1
        elif ch == ']':
            depth -= 1
        elif ch == ':' and depth == 0:
            last = i
    if last == -1:
        return '', cls
    return cls[:last], cls[last + 1:]


def tw_merge(*values: str | None) -> str:
    """Merge Tailwind class strings so that later classes win.

    Returns a single space separated class string with all conflicts resolved.
    """
    out: list[str | None] = []
    # (variants, path, index into ``out``) for every class still standing.
    kept: list[tuple[str, tuple[str, ...], int]] = []
    for value in values:
        if not value:
            continue
        for cls in str(value).split():
            variants, base = _split_variants(cls)
            path = _path(_group(base))
            # A later class wins whenever its path is a prefix of an earlier
            # class's path, so a shorthand evicts the narrower classes it covers
            # -- but the narrower class leaves an earlier shorthand alone.
            survivors: list[tuple[str, tuple[str, ...], int]] = []
            for entry in kept:
                if entry[0] == variants and entry[1][:len(path)] == path:
                    out[entry[2]] = None
                else:
                    survivors.append(entry)
            kept = survivors
            out.append(cls)
            kept.append((variants, path, len(out) - 1))
    return ' '.join(c for c in out if c)


def tw_join(*values: str | None) -> str:
    """Concatenate without resolving conflicts (useful for variants)."""
    return ' '.join(str(v) for v in values if v)

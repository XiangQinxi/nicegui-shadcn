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
group*, and lets the last occurrence of a group win.  Anything it does not
recognise is treated as its own group, so unknown classes are never dropped --
they are only de-duplicated.
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
        if rest[0] in _BORDER_SIDES:
            side, _, size = rest.partition('-')
            if not size or size in _RADIUS_SIZES:
                return f'rounded-{side}'
            return 'rounded'
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
    seen: dict[str, int] = {}
    for value in values:
        if not value:
            continue
        for cls in str(value).split():
            variants, base = _split_variants(cls)
            key = f'{variants}|{_group(base)}'
            previous = seen.get(key)
            if previous is not None:
                out[previous] = None
            out.append(cls)
            seen[key] = len(out) - 1
    return ' '.join(c for c in out if c)


def tw_join(*values: str | None) -> str:
    """Concatenate without resolving conflicts (useful for variants)."""
    return ' '.join(str(v) for v in values if v)

"""Inline Lucide icons.

shadcn/ui uses `lucide <https://lucide.dev>`_ icons.  Shipping the
``lucide-vue-next`` package would mean bundling and serving another ~200 kB of
JavaScript just to draw a handful of glyphs, so the handful of icons that the
components actually need are inlined here as raw SVG markup instead.

Every icon is a 24x24 stroked path drawn with ``currentColor``, so an icon
always inherits the surrounding text colour and can be sized with Tailwind
utilities.
"""

from __future__ import annotations

__all__ = ['ICON_NAMES', 'glyph', 'svg']

_ICONS: dict[str, str] = {
    'arrow-left': '<path d="m12 19-7-7 7-7"/><path d="M19 12H5"/>',
    'arrow-right': '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
    'arrow-up': '<path d="m5 12 7-7 7 7"/><path d="M12 19V5"/>',
    'arrow-down': '<path d="M12 5v14"/><path d="m19 12-7 7-7-7"/>',
    'bell': '<path d="M10.268 21a2 2 0 0 0 3.464 0"/>'
            '<path d="M3.262 15.326A1 1 0 0 0 4 17h16a1 1 0 0 0 .74-1.673C19.41 13.956 18 12.499 18 8A6 6 0 0 0 6 8c0 4.499-1.411 5.956-2.738 7.326"/>',
    'calendar': '<path d="M8 2v4"/><path d="M16 2v4"/>'
                '<rect width="18" height="18" x="3" y="4" rx="2"/>'
                '<path d="M3 10h18"/>',
    'check': '<path d="M20 6 9 17l-5-5"/>',
    'chevron-down': '<path d="m6 9 6 6 6-6"/>',
    'chevron-left': '<path d="m15 18-6-6 6-6"/>',
    'chevron-right': '<path d="m9 18 6-6-6-6"/>',
    'chevron-up': '<path d="m18 15-6-6-6 6"/>',
    'chevrons-up-down': '<path d="m7 15 5 5 5-5"/><path d="m7 9 5-5 5 5"/>',
    'circle': '<circle cx="12" cy="12" r="10"/>',
    'circle-check': '<circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/>',
    'circle-x': '<circle cx="12" cy="12" r="10"/>'
                '<path d="m15 9-6 6"/><path d="m9 9 6 6"/>',
    'copy': '<rect width="14" height="14" x="8" y="8" rx="2" ry="2"/>'
            '<path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>',
    'download': '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>'
                '<polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/>',
    'ellipsis': '<circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/>'
                '<circle cx="5" cy="12" r="1"/>',
    'ellipsis-vertical': '<circle cx="12" cy="12" r="1"/>'
                         '<circle cx="12" cy="5" r="1"/><circle cx="12" cy="19" r="1"/>',
    'external-link': '<path d="M15 3h6v6"/><path d="M10 14 21 3"/>'
                     '<path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>',
    'eye': '<path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0"/>'
           '<circle cx="12" cy="12" r="3"/>',
    'eye-off': '<path d="M10.733 5.076a10.744 10.744 0 0 1 11.205 6.575 1 1 0 0 1 0 .696 10.747 10.747 0 0 1-1.444 2.49"/>'
               '<path d="M14.084 14.158a3 3 0 0 1-4.242-4.242"/>'
               '<path d="M17.479 17.499a10.75 10.75 0 0 1-15.417-5.151 1 1 0 0 1 0-.696 10.75 10.75 0 0 1 4.446-5.143"/>'
               '<path d="m2 2 20 20"/>',
    'github': '<path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"/>'
              '<path d="M9 18c-4.51 2-5-2-7-2"/>',
    'info': '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/>'
            '<path d="M12 8h.01"/>',
    'loader-circle': '<path d="M21 12a9 9 0 1 1-6.219-8.56"/>',
    'mail': '<rect width="20" height="16" x="2" y="4" rx="2"/>'
            '<path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>',
    'menu': '<path d="M4 12h16"/><path d="M4 18h16"/><path d="M4 6h16"/>',
    'minus': '<path d="M5 12h14"/>',
    'moon': '<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>',
    'panel-left': '<rect width="18" height="18" x="3" y="3" rx="2"/>'
                  '<path d="M9 3v18"/>',
    'plus': '<path d="M5 12h14"/><path d="M12 5v14"/>',
    'search': '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
    'settings': '<path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/>'
                '<circle cx="12" cy="12" r="3"/>',
    'sun': '<circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/>'
           '<path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/>'
           '<path d="M2 12h2"/><path d="M20 12h2"/>'
           '<path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/>',
    'trash-2': '<path d="M3 6h18"/>'
               '<path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/>'
               '<path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/>'
               '<line x1="10" x2="10" y1="11" y2="17"/>'
               '<line x1="14" x2="14" y1="11" y2="17"/>',
    'triangle-alert': '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/>'
                      '<path d="M12 9v4"/><path d="M12 17h.01"/>',
    'upload': '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>'
              '<polyline points="17 8 12 3 7 8"/><line x1="12" x2="12" y1="3" y2="15"/>',
    'user': '<path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/>'
            '<circle cx="12" cy="7" r="4"/>',
    'x': '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>',
}

ICON_NAMES = tuple(sorted(_ICONS))


def glyph(name: str) -> str:
    """Return the inner SVG markup of a Lucide icon.

    For components that need an ``<svg>`` of their own -- one with a ``role`` or a
    different set of attributes than :func:`svg` hard-codes.

    :param name: icon name, e.g. ``'check'`` (see :data:`ICON_NAMES`)
    """
    try:
        return _ICONS[name]
    except KeyError:
        raise KeyError(f'unknown icon {name!r}; available: {", ".join(ICON_NAMES)}') from None


def svg(name: str, *, size: int | float = 16, stroke_width: float = 2, classes: str = '', **attrs: object) -> str:
    """Return the raw SVG markup for a Lucide icon.

    :param name: icon name, e.g. ``'check'`` (see :data:`ICON_NAMES`)
    :param size: width and height in pixels (default: 16)
    :param stroke_width: stroke width (default: 2)
    :param classes: extra CSS classes appended to the ``lucide`` classes
    :param attrs: extra attributes put on the ``<svg>`` element
    """
    if name not in _ICONS:
        raise KeyError(f'unknown icon {name!r}; available: {", ".join(ICON_NAMES)}')
    extra = ''.join(f' {k.rstrip("_").replace("_", "-")}="{v}"' for k, v in attrs.items())
    class_attr = ' '.join(part for part in ('lucide', f'lucide-{name}', classes) if part)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        f'stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" '
        f'class="{class_attr}" aria-hidden="true"{extra}>{_ICONS[name]}</svg>'
    )

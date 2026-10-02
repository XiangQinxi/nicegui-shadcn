"""Tests for nicegui_shadcn._tw_merge (the Python port of tailwind-merge).

Run directly (``python tests/test_tw_merge.py``) or via pytest.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from nicegui_shadcn._tw_merge import tw_merge  # noqa: E402

CASES: list[tuple[tuple[str, ...], str]] = [
    # caller wins over the component default; surviving classes keep the
    # position they had in the input (this is tailwind-merge's ordering)
    (('h-9 rounded-md bg-primary px-4', 'bg-destructive rounded-full'),
     'h-9 px-4 bg-destructive rounded-full'),
    # same property, later wins
    (('px-4 py-2', 'px-8'), 'py-2 px-8'),
    (('text-sm', 'text-lg'), 'text-lg'),
    # text size and text colour live in different groups
    (('text-sm text-muted-foreground', 'text-lg'),
     'text-muted-foreground text-lg'),
    (('text-primary', 'text-destructive-foreground'),
     'text-destructive-foreground'),
    # different variants do not conflict
    (('hover:bg-primary', 'bg-destructive'), 'hover:bg-primary bg-destructive'),
    (('hover:bg-primary', 'hover:bg-destructive'), 'hover:bg-destructive'),
    (('dark:bg-input', 'bg-background'), 'dark:bg-input bg-background'),
    (('focus-visible:ring-2', 'ring-0'), 'focus-visible:ring-2 ring-0'),
    # border width vs border colour are separate groups
    (('border border-input', 'border-2'), 'border-input border-2'),
    (('border-2 border-input', 'border-transparent'),
     'border-2 border-transparent'),
    (('border-dashed border-input', 'border-solid'), 'border-input border-solid'),
    # rounded sides
    (('rounded-lg', 'rounded-t-none'), 'rounded-lg rounded-t-none'),
    (('rounded-t-lg', 'rounded-t-none'), 'rounded-t-none'),
    # shadow / ring
    (('shadow-sm', 'shadow-lg'), 'shadow-lg'),
    (('shadow-sm', 'shadow-red-500'), 'shadow-sm shadow-red-500'),
    (('ring-2 ring-ring', 'ring-0'), 'ring-ring ring-0'),
    (('ring-offset-2', 'ring-offset-background'), 'ring-offset-2 ring-offset-background'),
    # font weight vs family
    (('font-medium', 'font-bold'), 'font-bold'),
    (('font-medium', 'font-mono'), 'font-medium font-mono'),
    # display / position
    (('flex items-center', 'hidden'), 'items-center hidden'),
    (('absolute', 'relative'), 'relative'),
    # gaps are per axis
    (('gap-2 gap-x-4', 'gap-x-8'), 'gap-2 gap-x-8'),
    # padding sides are independent
    (('p-4 pt-2', 'pt-8'), 'p-4 pt-8'),
    # sizing
    (('size-9 w-full', 'size-4'), 'w-full size-4'),
    # unknown classes are preserved, duplicates removed
    (('my-custom-class', 'my-custom-class'), 'my-custom-class'),
    (('shadcn-foo shadcn-bar', 'shadcn-baz'), 'shadcn-foo shadcn-bar shadcn-baz'),
    # important prefix
    (('!p-2', 'p-4'), 'p-4'),
    # arbitrary values with brackets keep their variant prefix
    (('bg-[--x]', 'bg-[--y]'), 'bg-[--y]'),
    (('[&>*]:p-2', '[&>*]:p-4'), '[&>*]:p-4'),
    (('[&>*]:p-2', 'p-4'), '[&>*]:p-2 p-4'),
    # data / aria variants
    (('data-[state=open]:bg-accent', 'data-[state=open]:bg-primary'),
     'data-[state=open]:bg-primary'),
    # empty / None inputs
    (('', None, 'p-2'), 'p-2'),
    ((), ''),
    # negative values
    (('-mt-2', '-mt-4'), '-mt-4'),
    (('mt-2', '-mt-4'), '-mt-4'),
    # whitespace handling
    (('  p-2   m-2  ', 'p-4'), 'm-2 p-4'),
]


def test_all() -> None:
    failures = []
    for inputs, expected in CASES:
        actual = tw_merge(*inputs)
        if actual != expected:
            failures.append((inputs, expected, actual))
    assert not failures, '\n'.join(
        f'  tw_merge{inputs!r}\n    expected: {expected!r}\n    actual:   {actual!r}'
        for inputs, expected, actual in failures
    )


def main() -> int:
    try:
        test_all()
    except AssertionError as error:
        print('FAILED')
        print(error)
        return 1
    print(f'OK - {len(CASES)} tw_merge cases passed')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

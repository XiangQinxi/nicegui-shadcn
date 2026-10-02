"""Verify README_zh.md against README.md: identical code blocks and live anchors.

The two READMEs are hand-maintained mirrors of each other. Two invariants keep them
from drifting:

* every fenced code block must be **byte-identical** in both files, so the Chinese
  page cannot quietly demonstrate a different API than the English one;
* every ``](#anchor)`` link must point at a heading that actually exists, with
  GitHub's slug rules applied (backticks dropped, punctuation removed, spaces to
  hyphens — ``## The `classes=` keyword`` becomes ``the-classes-keyword``).

    python tests/check_readme.py

Exit code 0 means both hold; 1 prints the offending block or anchor.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EN = (ROOT / 'README.md').read_text(encoding='utf-8')
ZH = (ROOT / 'README_zh.md').read_text(encoding='utf-8')

BLOCK_RE = re.compile(r'^```[^\n]*\n(.*?)^```', re.M | re.S)
en_blocks = BLOCK_RE.findall(EN)
zh_blocks = BLOCK_RE.findall(ZH)

print(f'code blocks: english={len(en_blocks)} chinese={len(zh_blocks)}')
ok = True
if len(en_blocks) != len(zh_blocks):
    print('  FAIL count mismatch')
    ok = False
else:
    bad = [i for i, (a, b) in enumerate(zip(en_blocks, zh_blocks)) if a != b]
    if bad:
        print(f'  FAIL {len(bad)} block(s) differ: {bad}')
        for i in bad[:2]:
            print(f'  --- english block {i} ---\n{en_blocks[i]}')
            print(f'  --- chinese block {i} ---\n{zh_blocks[i]}')
        ok = False
    else:
        print('  OK all code blocks byte-identical')


def anchors(text: str) -> set[str]:
    out = set()
    for heading in re.findall(r'^#{1,6}[ \t]+(.*?)[ \t]*$', text, re.M):
        h = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', heading)  # markdown link -> text
        h = h.replace('`', '').lower()
        h = re.sub(r'[^\w\s-]', '', h)
        out.add(re.sub(r'\s+', '-', h).strip('-'))
    return out


for label, text in (('README.md', EN), ('README_zh.md', ZH)):
    have = anchors(text)
    links = re.findall(r'\]\(#([^)]*)\)', text)
    missing = sorted({link for link in links if link not in have})
    if missing:
        print(f'{label}: FAIL {len(missing)} dead anchor(s): {missing}')
        print(f'  headings available: {sorted(have)}')
        ok = False
    else:
        print(f'{label}: OK all {len(links)} internal anchor link(s) resolve')

print()
print('RESULT:', 'PASS' if ok else 'FAIL')
raise SystemExit(0 if ok else 1)

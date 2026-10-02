/**
 * Headless visual + behavioural check for nicegui-shadcn.
 *
 * The DSH built-in browser is unavailable in this environment, so this drives a
 * locally installed Chromium browser (Edge or Chrome) through `playwright-core`.
 * No browser is downloaded: set CHROME_PATH to override the auto-detected one.
 *
 *     node tests/visual_check.mjs [base-url]
 *
 * It fails (exit 1) on any assertion below and always writes `_shot-light.png`
 * and `_shot-dark.png`, plus a JSON report on stdout.
 *
 * Colours are compared as *computed strings* rather than converted to rgb:
 * Chromium reports an `oklch()` token back as `oklch(...)`, so resolving the
 * same token on a probe element yields an exactly comparable value and proves
 * which design token a component actually used.
 *
 * Two reka-ui lessons are baked into the selectors below: reka does not emit
 * every `data-reka-*` attribute you might hope for, so an attribute is only
 * asserted after confirming it exists; and a reka-rendered primitive gets its
 * own generated `id`, which overrides an id set from Python — so rendered
 * primitives are located structurally rather than by a Python-side id.
 */
import { existsSync } from 'node:fs';
import { chromium } from 'playwright-core';

const BASE = process.argv[2] ?? process.env.SHADCN_DEMO_URL ?? 'http://127.0.0.1:8080/';
const OUT_DIR = process.env.SHADCN_SHOT_DIR ?? '.';

const CANDIDATES = [
  process.env.CHROME_PATH,
  'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe',
  'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
  'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
  'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
  `${process.env.LOCALAPPDATA}\\Google\\Chrome\\Application\\chrome.exe`,
  '/usr/bin/google-chrome',
  '/usr/bin/chromium',
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
].filter(Boolean);

const executablePath = CANDIDATES.find((p) => existsSync(p));
if (!executablePath) {
  console.error('!! no local Chromium found; set CHROME_PATH to one');
  process.exit(2);
}

const failures = [];
const check = (name, ok, detail) => {
  console.log(`${ok ? 'PASS' : 'FAIL'}  ${name}${detail === undefined ? '' : `  -> ${JSON.stringify(detail)}`}`);
  if (!ok) failures.push(name);
};

/** Computed `background-color` of a probe carrying the given CSS value. */
const resolve = (page, css) => page.evaluate((value) => {
  const probe = document.createElement('div');
  probe.style.cssText = `position:absolute;opacity:0;pointer-events:none;background-color:${value}`;
  document.body.appendChild(probe);
  const out = getComputedStyle(probe).backgroundColor;
  probe.remove();
  return out;
}, css);

const token = (page, name) => page.evaluate((n) =>
  getComputedStyle(document.documentElement).getPropertyValue(n).trim(), name);

const browser = await chromium.launch({ executablePath, headless: true });
try {
  const page = await browser.newPage({ viewport: { width: 900, height: 1200 } });

  const consoleErrors = [];
  page.on('console', (m) => { if (m.type() === 'error') consoleErrors.push(m.text()); });
  page.on('pageerror', (e) => consoleErrors.push(`pageerror: ${e.message}`));

  await page.goto(BASE, { waitUntil: 'domcontentloaded' });

  // NiceGUI renders over a websocket, so wait for our own component instead of load.
  await page.waitForSelector('input[placeholder="my-project"]', { timeout: 45000 });
  await page.waitForTimeout(500);

  check('no console/page errors', consoleErrors.length === 0, consoleErrors.slice(0, 5));

  // ---- stylesheet actually loaded --------------------------------------- #
  const cssLoaded = await page.evaluate(() =>
    [...document.styleSheets].some((s) => (s.href ?? '').includes('/_nicegui_shadcn/shadcn.css')));
  check('shadcn.css stylesheet loaded', cssLoaded);

  // ---- design tokens are the shadcn ones, not Quasar's ------------------ #
  const primary = await token(page, '--primary');
  check('--primary is the shadcn token', primary.startsWith('oklch'), primary);

  const defaultButton = page.locator('button', { hasText: /^Default$/ }).first();
  const btn = await defaultButton.evaluate((el) => {
    const s = getComputedStyle(el);
    return {
      display: s.display, position: s.position, radius: s.borderRadius, weight: s.fontWeight,
      height: s.height, bg: s.backgroundColor, color: s.color, cls: el.className,
    };
  });
  // `inline-flex` inside a flex row is reported blockified as `flex` by Chromium,
  // so both spellings mean "the base classes applied".
  check('button carries its base classes (display/radius/weight)',
    ['flex', 'inline-flex'].includes(btn.display) && parseFloat(btn.radius) > 0 && Number(btn.weight) >= 500,
    { display: btn.display, position: btn.position, radius: btn.radius, weight: btn.weight });
  check('button height follows the size variant (h-9 = 36px)', btn.height === '36px', btn.height);
  check('primary button paints var(--primary), not Quasar blue',
    btn.bg === await resolve(page, 'var(--primary)'), { got: btn.bg, token: primary });
  check('primary button text uses var(--primary-foreground)',
    btn.color === await resolve(page, 'var(--primary-foreground)'), btn.color);

  // ---- the .vue components mounted -------------------------------------- #
  // Counts are lower bounds: the demo shows the same component in several
  // cards, and adding a card should not turn this into a false alarm. The
  // point of the check is that every registered component actually compiled and
  // mounted instead of silently rendering nothing.
  // Components that render into a portal (dialog/popover/dropdown content) only
  // exist in the DOM while open, so they are asserted in the overlay block below.
  const MOUNTS = [
    ['input', 3], ['textarea', 1], ['checkbox', 1], ['switch', 1],
    ['tabs', 1], ['tabs_list', 1], ['tabs_content', 2],
    ['accordion', 1], ['accordion_item', 2], ['accordion_trigger', 2], ['accordion_content', 2],
    ['select', 1], ['radio_group', 1], ['slider', 1], ['toggle', 2], ['toggle_group', 1],
    ['dialog_trigger', 1], ['popover_trigger', 1],
    // the second wave of components
    ['aspect_ratio', 1], ['calendar', 1], ['scroll_area', 1], ['native_select', 1],
    ['pagination', 1], ['pagination_previous', 1], ['pagination_next', 1],
    ['collapsible', 1], ['collapsible_trigger', 1], ['collapsible_content', 1],
    ['hover_card_trigger', 1], ['alert_dialog_trigger', 1], ['context_menu_trigger', 1],
    ['drawer_trigger', 1], ['calendar', 1], ['input_otp', 1],
    ['command', 1], ['combobox', 1], ['menubar', 1], ['navigation_menu', 1],
  ];
  const missing = [];
  for (const [name, expected] of MOUNTS) {
    const n = await page.locator(`[data-shadcn_${name}]`).count();
    if (n < expected) missing.push(`${name}(${n}<${expected})`);
  }
  check('every registered .vue component mounted', missing.length === 0, missing);

  const inputStyle = await page.locator('input[placeholder="my-project"]')
    .evaluate((el) => { const s = getComputedStyle(el); return { border: s.borderTopColor, h: s.height }; });
  check('input border resolves to var(--input)',
    inputStyle.border === await resolve(page, 'var(--input)'), inputStyle);
  check('input height follows h-9', inputStyle.h === '36px', inputStyle.h);

  const tick = await page.evaluate(() => {
    const box = document.querySelector('[data-shadcn_checkbox]');
    const svg = box?.querySelector('svg');
    return svg ? getComputedStyle(svg).opacity : null;
  });
  check('checked checkbox draws its tick', tick === '1', tick);

  const knob = await page.evaluate(() => {
    const sw = document.querySelector('[data-shadcn_switch]');
    const el = sw?.querySelector('span');
    return el ? getComputedStyle(el).transform : null;
  });
  check('switch renders a knob', knob !== null, knob);

  const avatar = await page.evaluate(() => {
    const span = [...document.querySelectorAll('span')].find((s) => s.textContent.trim() === 'CN');
    if (!span) return null;
    const host = span.parentElement;
    return { cls: span.className, hostTag: host.tagName, hostRadius: getComputedStyle(host).borderRadius };
  });
  check('avatar fallback sits inside the rounded container',
    avatar !== null && avatar.hostTag === 'DIV' && parseFloat(avatar.hostRadius) > 0, avatar);

  // ---- reka-ui behaviour ------------------------------------------------ #
  // These are the checks that would have caught the RovingFocusGroupContext
  // bug: a reka primitive that fails to inject renders nothing at all, so
  // asserting on the rendered tab strip is what proves the component tree is
  // wired correctly, not just that the CSS compiled.
  const tabs = await page.evaluate(() => {
    const triggers = [...document.querySelectorAll('[role="tab"]')];
    return {
      count: triggers.length,
      labels: triggers.map((t) => t.textContent.trim()),
      active: triggers.filter((t) => t.getAttribute('data-state') === 'active').map((t) => t.textContent.trim()),
      disabled: triggers.filter((t) => t.hasAttribute('disabled')).length,
    };
  });
  check('tabs render one trigger per entry with a single active tab',
    tabs.count === 3 && tabs.labels.join(',') === 'Account,Password,Disabled' && tabs.active.length === 1,
    tabs);
  check('a disabled tab is disabled', tabs.disabled === 1, tabs.disabled);

  const panels = await page.evaluate(() => {
    const list = [...document.querySelectorAll('[data-shadcn_tabs_content]')];
    return list.map((el) => ({ state: el.getAttribute('data-state'), h: el.getBoundingClientRect().height }));
  });
  check('only the active tab panel is visible',
    panels.length === 2 && panels[0].h > 0 && panels[1].h === 0, panels);

  const accordion = await page.evaluate(() => {
    const list = [...document.querySelectorAll('[data-shadcn_accordion_content]')];
    return list.map((el) => el.getBoundingClientRect().height > 0);
  });
  check('accordion opens its value and keeps the other item shut',
    accordion.length === 2 && accordion[0] === true && accordion[1] === false, accordion);

  const radio = await page.evaluate(() => {
    const root = document.querySelector('[data-shadcn_radio_group]');
    if (!root) return null;
    const items = [...root.querySelectorAll('[role="radio"]')];
    return { count: items.length, checked: items.filter((el) => el.getAttribute('data-state') === 'checked').length };
  });
  check('radio group renders its options with one selected',
    radio !== null && radio.count === 3 && radio.checked === 1, radio);

  const slider = await page.evaluate(() => {
    const thumb = document.querySelector('[data-shadcn_slider] [role="slider"]');
    if (!thumb) return null;
    return {
      value: thumb.getAttribute('aria-valuenow'),
      min: thumb.getAttribute('aria-valuemin'),
      max: thumb.getAttribute('aria-valuemax'),
      width: getComputedStyle(thumb).width,
    };
  });
  check('slider exposes the Python value and range',
    slider !== null && slider.value === '40' && slider.min === '0' && slider.max === '100', slider);

  const toggles = await page.evaluate(() => ({
    group: [...document.querySelectorAll('[data-shadcn_toggle_group] [data-state="on"]')].map((el) => el.textContent.trim()),
    single: [...document.querySelectorAll('[data-shadcn_toggle][data-state="on"]')].map((el) => el.textContent.trim()),
  }));
  check('toggle group and toggle reflect their Python values',
    toggles.group.includes('center') && toggles.single.includes('Bold'), toggles);

  const select = await page.evaluate(() => {
    const trigger = document.querySelector('[data-shadcn_select]');
    return trigger ? { tag: trigger.tagName, text: trigger.textContent.trim() } : null;
  });
  check('select trigger is the combobox and shows the current option',
    select !== null && select.tag === 'BUTTON' && select.text === 'System', select);

  // ---- overlays: portal, focus trap and dismiss ------------------------- #
  const dialogPanel = page.locator('[data-shadcn_dialog_content]').first();
  await page.locator('button', { hasText: /^Edit profile$/ }).first().click();
  await page.waitForTimeout(500);
  const dialogText = await dialogPanel.innerText().catch(() => '');
  check('dialog opens with its title and description',
    /Edit profile/.test(dialogText) && /saved locally/.test(dialogText)
      && await page.locator('[data-shadcn_dialog_content]').count() === 1,
    dialogText.replace(/\s+/g, ' ').slice(0, 90));
  await page.keyboard.press('Escape');
  await page.waitForTimeout(500);
  check('dialog closes on Escape', !(await dialogPanel.isVisible().catch(() => false)), null);

  await page.locator('button', { hasText: /Open popover/ }).first().click();
  await page.waitForTimeout(400);
  const popover = page.locator('[data-shadcn_popover_content]').first();
  check('popover opens on trigger click and carries its mount marker',
    await popover.isVisible().catch(() => false) && await popover.count() === 1, await popover.count());
  await page.keyboard.press('Escape');
  await page.waitForTimeout(300);

  await page.locator('button', { hasText: /Open menu/ }).first().click();
  await page.waitForTimeout(400);
  const menuItems = await page.locator('[role="menuitem"]').allInnerTexts().catch(() => []);
  check('dropdown menu renders the items passed from Python',
    menuItems.length >= 3 && await page.locator('[data-shadcn_dropdown_menu]').count() === 1, menuItems);
  await page.keyboard.press('Escape');
  await page.waitForTimeout(300);

  await page.locator('button', { hasText: /Hover me/ }).first().hover();
  await page.waitForTimeout(900);
  const tooltip = await page.locator('[role="tooltip"]').first().innerText().catch(() => '');
  check('tooltip appears on hover', tooltip.trim().length > 0, tooltip);

  // Switch to the second tab and back, so the screenshot below still shows the
  // first panel.
  const passwordTab = page.locator('[role="tab"]', { hasText: /^Password$/ }).first();
  await passwordTab.click();
  await page.waitForTimeout(400);
  const pwPanel = await page.evaluate(() => {
    const list = [...document.querySelectorAll('[data-shadcn_tabs_content]')];
    return list.map((el) => el.getBoundingClientRect().height > 0);
  });
  check('clicking a tab switches the visible panel', pwPanel[0] === false && pwPanel[1] === true, pwPanel);
  await page.locator('[role="tab"]', { hasText: /^Account$/ }).first().click();
  await page.waitForTimeout(300);

  // ---- two-way binding through NiceGUI ---------------------------------- #
  // Submit notifies `Hello {form.name}!`, so the round trip proves the value
  // the .vue input emitted reached the bound dataclass on the server.
  await page.locator('input[placeholder="my-project"]').fill('renamed-project');
  await page.locator('button', { hasText: /^Submit$/ }).first().click();
  const notified = await page.locator('.q-notification').first().innerText({ timeout: 15000 }).catch(() => '');
  check('typed value round-tripped to the server', notified.includes('renamed-project'), notified.trim());

  // ======================================================================= //
  // Newly added component families
  // ======================================================================= //
  // Every interactive widget below writes to `#probe-log` on the server, so a
  // check that waits for its own token in that line proves the click travelled
  // all the way through the websocket into the bound Python handler.
  const probeText = () => page.locator('#probe-log').innerText().catch(() => '');
  let probeSnapshot = '';
  const waitForEvent = async (needle, timeout = 6000) => {
    const deadline = Date.now() + timeout;
    while (Date.now() < deadline) {
      probeSnapshot = await probeText();
      if (probeSnapshot.includes(needle)) return true;
      await page.waitForTimeout(150);
    }
    return false;
  };

  // ---- button group / kbd / spinner / marker ----------------------------- #
  const groups = await page.evaluate(() => [...document.querySelectorAll('div')]
    .filter((d) => (d.className ?? '').includes('[&>*]:rounded-none'))
    .map((box) => ({
      cls: box.className,
      children: [...box.children].map((c) => ({ tag: c.tagName, text: c.textContent.trim(), cls: c.className })),
    })));
  check('button group renders a segmented row of buttons',
    groups.length >= 1 && groups[0].children.length === 3
      && groups[0].children.map((c) => c.text).join(',') === 'Day,Week,Month'
      && groups[0].children.every((c) => c.tag === 'BUTTON'),
    groups.map((g) => g.children.map((c) => c.text)));
  const labelled = groups.find((g) => g.children.some((c) => c.text === 'Zoom'));
  check('button group text and separator render between the buttons',
    labelled !== undefined && labelled.children.length === 3
      && labelled.children[0].tag === 'DIV' && labelled.children[2].text === 'Fit'
      && labelled.children[1].cls.includes('w-px') && labelled.children[1].cls.includes('bg-input'),
    labelled?.children.map((c) => `${c.tag}:${c.text}:${c.cls.slice(0, 24)}`));

  const kbds = await page.evaluate(() => [...document.querySelectorAll('kbd')]
    .map((k) => ({ tag: k.tagName, text: k.textContent.trim(), bg: getComputedStyle(k).backgroundColor })));
  check('kbd renders shortcut keys as <kbd> elements',
    kbds.length >= 2 && kbds.map((k) => k.text).join('') === 'CtrlK'
      && kbds.every((k) => k.tag === 'KBD'),
    kbds.map((k) => `${k.tag}:${k.text}`));
  check('kbd paints var(--muted)',
    kbds.length > 0 && kbds[0].bg === await resolve(page, 'var(--muted)'), kbds[0]?.bg);

  const spinners = await page.evaluate(() => [...document.querySelectorAll('[role="status"]')]
    .map((s) => ({
      label: s.getAttribute('aria-label'),
      spins: s.classList.contains('animate-spin') || !!s.querySelector('.animate-spin'),
    })));
  check('spinner announces itself and animates',
    spinners.length >= 2 && spinners.some((s) => s.label === 'Loading') && spinners.every((s) => s.spins),
    spinners);

  const markers = await page.evaluate(() => [...document.querySelectorAll('div')]
    .filter((d) => (d.className ?? '').startsWith('flex items-center gap-2 text-sm'))
    .map((d) => ({
      text: d.textContent.trim(),
      dotCls: d.firstElementChild?.className ?? '',
      bg: d.firstElementChild ? getComputedStyle(d.firstElementChild).backgroundColor : null,
    })));
  const markerColors = markers.map((m) => m.bg);
  check('marker renders one dot per status',
    markers.length === 5 && markers.map((m) => m.text).join(',') === 'Default,Success,Warning,Error,Live',
    markers.map((m) => m.text));
  check('marker default dot uses var(--primary)',
    markers[0]?.bg === await resolve(page, 'var(--primary)'), markers[0]?.bg);
  check('marker status dots use distinct palette colours',
    markerColors.length === 5 && markerColors.every((c) => c && c !== 'rgba(0, 0, 0, 0)')
      && new Set(markerColors).size === 5,
    markerColors);
  check('marker can pulse', markers[4]?.dotCls.includes('animate-pulse') === true, markers[4]?.dotCls);

  // ---- typography -------------------------------------------------------- #
  const typo = await page.evaluate(() => {
    const find = (sel, text) => [...document.querySelectorAll(sel)]
      .find((el) => el.textContent.trim().startsWith(text));
    const size = (el) => (el ? getComputedStyle(el).fontSize : null);
    const h1 = find('h1', 'Heading one');
    const quote = find('blockquote', 'Every CSS class');
    const qs = quote ? getComputedStyle(quote) : null;
    const code = find('code', 'from nicegui_shadcn');
    const list = [...document.querySelectorAll('ul')].find((u) => u.textContent.includes('Copy a component'));
    const muted = find('p', 'Muted supporting copy');
    return {
      sizes: [size(h1), size(find('h2', 'Heading two')), size(find('h3', 'Heading three')), size(find('h4', 'Heading four'))],
      tags: [h1, find('h2', 'Heading two'), find('h3', 'Heading three'), find('h4', 'Heading four')].map((el) => el?.tagName),
      weight: h1 ? getComputedStyle(h1).fontWeight : null,
      lead: size(find('p', 'A lead paragraph')),
      large: size(find('.text-lg', 'Large and semibold')),
      small: size(find('small', 'Small print')),
      quote: qs ? { style: qs.fontStyle, border: qs.borderLeftWidth } : null,
      code: code ? { bg: getComputedStyle(code).backgroundColor, tag: code.tagName } : null,
      listItems: list ? list.querySelectorAll(':scope > li').length : 0,
      listTag: list?.tagName,
      muted: muted ? getComputedStyle(muted).color : null,
    };
  });
  check('typography renders the h1..h4 scale from Python `level`',
    typo.sizes.join(',') === '36px,30px,24px,20px' && typo.tags.join(',') === 'H1,H2,H3,H4'
      && Number(typo.weight) >= 800, typo.sizes);
  check('lead / large / small / muted follow their variants',
    typo.lead === '20px' && typo.large === '18px' && typo.small === '14px'
      && typo.muted === await resolve(page, 'var(--muted-foreground)'),
    { lead: typo.lead, large: typo.large, small: typo.small, muted: typo.muted });
  check('blockquote carries its rule and inline_code paints var(--muted)',
    typo.quote?.style === 'italic' && typo.quote?.border === '2px'
      && typo.code?.tag === 'CODE' && typo.code?.bg === await resolve(page, 'var(--muted)'),
    { quote: typo.quote, code: typo.code });
  check('bullet list renders one <li> per entry',
    typo.listTag === 'UL' && typo.listItems === 3, { tag: typo.listTag, items: typo.listItems });

  // ---- content: aspect ratio, empty state, scroll area, direction -------- #
  const content = await page.evaluate(() => {
    const empty = document.querySelector('[class*="border-dashed"]');
    const ar = document.querySelector('[data-shadcn_aspect_ratio]');
    const wrap = ar?.parentElement;
    const sc = document.querySelector('[data-shadcn_scroll_area]');
    const vp = sc?.querySelector('[class*="size-full"]');
    return {
      empty: empty ? {
        radius: getComputedStyle(empty).borderTopLeftRadius,
        dashed: getComputedStyle(empty).borderTopStyle,
        svg: !!empty.querySelector('svg'),
        title: /No projects yet/.test(empty.textContent),
        description: /Create your first project/.test(empty.textContent),
        button: !!empty.querySelector('button'),
      } : null,
      ratio: wrap ? { inline: wrap.style.paddingBottom, relative: getComputedStyle(wrap).position } : null,
      scroll: sc ? {
        overflow: getComputedStyle(sc).overflow,
        scrollHeight: vp?.scrollHeight ?? 0,
        clientHeight: vp?.clientHeight ?? 0,
      } : null,
      direction: document.querySelector('#direction-block')?.getAttribute('dir') ?? null,
    };
  });
  check('empty state renders media, title, description and content',
    content.empty !== null && content.empty.svg && content.empty.title
      && content.empty.description && content.empty.button
      && content.empty.dashed === 'dashed' && parseFloat(content.empty.radius) > 0,
    content.empty);
  check('aspect ratio reserves its box through the reka wrapper',
    content.ratio?.relative === 'relative' && content.ratio?.inline === '56.25%', content.ratio);
  check('scroll area clips its viewport around taller content',
    content.scroll?.overflow === 'hidden' && content.scroll.scrollHeight > content.scroll.clientHeight,
    content.scroll);
  check('direction element carries the dir attribute from Python',
    content.direction === 'rtl', content.direction);

  // ---- item --------------------------------------------------------------- #
  const items = await page.evaluate(() => {
    const n = (slot) => document.querySelectorAll(`[data-slot="${slot}"]`).length;
    const pick = (variant) => [...document.querySelectorAll('[data-slot="item"]')]
      .find((el) => el.getAttribute('data-variant') === variant);
    const outline = pick('outline');
    const muted = pick('muted');
    return {
      slots: ['item', 'item-media', 'item-content', 'item-title', 'item-description',
        'item-actions', 'item-footer', 'item-separator'].map((s) => `${s}:${n(s)}`),
      variants: [...document.querySelectorAll('[data-slot="item"]')].map((el) => el.getAttribute('data-variant')),
      sizes: [...document.querySelectorAll('[data-slot="item"]')].map((el) => el.getAttribute('data-size')),
      outlineBorder: outline ? getComputedStyle(outline).borderTopColor : null,
      mutedBg: muted ? getComputedStyle(muted).backgroundColor : null,
      groupRole: document.querySelector('[data-slot="item"]')?.parentElement?.getAttribute('role') ?? null,
    };
  });
  check('item family renders every slot',
    items.slots.join(',') === 'item:2,item-media:2,item-content:2,item-title:2,item-description:2,item-actions:1,item-footer:1,item-separator:1'
      && items.groupRole === 'list', items.slots);
  check('item variants drive the border and background',
    items.variants.join(',') === 'outline,muted' && items.sizes.join(',') === 'default,sm'
      && items.outlineBorder === await resolve(page, 'var(--border)')
      && items.mutedBg !== 'rgba(0, 0, 0, 0)',
    { variants: items.variants, sizes: items.sizes, border: items.outlineBorder, muted: items.mutedBg });

  // ---- breadcrumb / native select / pagination ---------------------------- #
  const crumb = await page.evaluate(() => {
    const nav = document.querySelector('nav[aria-label="breadcrumb"]');
    if (!nav) return null;
    return {
      ol: nav.querySelectorAll('ol').length,
      items: nav.querySelectorAll('li').length,
      links: [...nav.querySelectorAll('a')].map((a) => a.textContent.trim()),
      separators: nav.querySelectorAll('li[role="presentation"][aria-hidden="true"]').length,
      current: nav.querySelector('[aria-current="page"]')?.textContent.trim() ?? null,
      ellipsis: nav.querySelector('.sr-only')?.textContent.trim() ?? null,
    };
  });
  check('breadcrumb renders a trailer of links, separators and a page',
    crumb !== null && crumb.ol === 1 && crumb.items === 7 && crumb.links.join(',') === 'Home,Components'
      && crumb.separators === 3 && crumb.current === 'Breadcrumb', crumb);
  check('breadcrumb ellipsis is hidden from sight but not from screen readers',
    crumb?.ellipsis === 'More', crumb?.ellipsis);

  const nativeSelect = await page.evaluate(() => {
    const el = document.querySelector('[data-shadcn_native_select] select');
    return el ? {
      tag: el.tagName, value: el.value,
      options: [...el.options].map((o) => `${o.value}:${o.textContent.trim()}`),
      height: getComputedStyle(el).height,
    } : null;
  });
  check('native select is a real <select> carrying the Python value',
    nativeSelect !== null && nativeSelect.tag === 'SELECT' && nativeSelect.value === 'growth'
      && nativeSelect.options.join(',') === 'starter:Starter,growth:Growth,scale:Scale'
      && nativeSelect.height === '36px',
    nativeSelect);

  const pager = await page.evaluate(() => {
    const nav = document.querySelector('[data-shadcn_pagination]');
    if (!nav) return null;
    return {
      tag: nav.tagName,
      label: nav.getAttribute('aria-label'),
      current: nav.querySelector('[aria-current="page"]')?.textContent.trim() ?? null,
      numbers: [...nav.querySelectorAll('button')].map((b) => b.getAttribute('aria-label')).filter((l) => /^Go to page \d+$/.test(l)).length,
      prevDisabled: nav.querySelector('[data-shadcn_pagination_previous]')?.hasAttribute('disabled') ?? null,
      nextDisabled: nav.querySelector('[data-shadcn_pagination_next]')?.hasAttribute('disabled') ?? null,
    };
  });
  check('pagination marks the current page and keeps both arrows live',
    pager !== null && pager.tag === 'NAV' && pager.label === 'Pagination' && pager.current === '3'
      && pager.numbers === 5 && pager.prevDisabled === false && pager.nextDisabled === false,
    pager);

  // ---- collapsible --------------------------------------------------------- #
  const collapsed = await page.locator('[data-shadcn_collapsible_content]').first()
    .evaluate((el) => el.getBoundingClientRect().height);
  await page.locator('[data-shadcn_collapsible_trigger]').first().click();
  await page.waitForTimeout(500);
  const expanded = await page.locator('[data-shadcn_collapsible_content]').first()
    .evaluate((el) => el.getBoundingClientRect().height);
  check('collapsible opens its content and tells Python about it',
    collapsed === 0 && expanded > 0 && await waitForEvent('collapsible:True'),
    { collapsed, expanded, probe: probeSnapshot });
  await page.locator('[data-shadcn_collapsible_trigger]').first().click();
  await page.waitForTimeout(400);

  // ---- button group + empty-state round trips ------------------------------ #
  await page.locator('button', { hasText: /^Week$/ }).first().click();
  check('button group click reaches Python', await waitForEvent('group:week'), probeSnapshot);
  await page.locator('button', { hasText: /^Fit$/ }).first().click();
  check('button group text/separator row click reaches Python', await waitForEvent('group:fit'), probeSnapshot);
  await page.locator('button', { hasText: /Create project/ }).first().click();
  check('empty-state action reaches Python', await waitForEvent('empty:create'), probeSnapshot);
  await page.locator('[data-slot="item-actions"] button').first().click();
  check('item action reaches Python', await waitForEvent('item:open'), probeSnapshot);

  // ---- sheet / drawer ------------------------------------------------------ #
  await page.locator('button', { hasText: /Open sheet/ }).first().click();
  await page.waitForTimeout(600);
  const sheet = page.locator('[data-shadcn_sheet_content]').first();
  const sheetText = await sheet.innerText().catch(() => '');
  check('sheet opens as a side panel with its title and description',
    await sheet.isVisible().catch(() => false) && /Edit settings/.test(sheetText)
      && /Changes apply immediately/.test(sheetText) && await waitForEvent('sheet:True'),
    sheetText.replace(/\s+/g, ' ').slice(0, 80));
  await page.keyboard.press('Escape');
  await page.waitForTimeout(600);
  check('sheet closes on Escape and reports it back',
    !(await sheet.isVisible().catch(() => false)) && await waitForEvent('sheet:False'), probeSnapshot);

  await page.locator('button', { hasText: /Open drawer/ }).first().click();
  await page.waitForTimeout(700);
  const drawer = page.locator('[data-shadcn_drawer_content]').first();
  check('drawer slides in from the bottom edge',
    await drawer.isVisible().catch(() => false)
      && (await drawer.evaluate((el) => getComputedStyle(el).bottom)) === '0px'
      && await waitForEvent('drawer:True'),
    await drawer.evaluate((el) => el.className).catch(() => ''));
  await page.keyboard.press('Escape');
  await page.waitForTimeout(600);
  check('drawer closes on Escape and reports it back',
    !(await drawer.isVisible().catch(() => false)) && await waitForEvent('drawer:False'), probeSnapshot);

  // ---- alert dialog -------------------------------------------------------- #
  await page.locator('button', { hasText: /Delete project/ }).first().click();
  await page.waitForTimeout(600);
  const alertPanel = page.locator('[data-shadcn_alert_dialog_content]').first();
  const alertText = await alertPanel.innerText().catch(() => '');
  check('alert dialog is a modal alertdialog with its title and description',
    await alertPanel.isVisible().catch(() => false)
      && await alertPanel.getAttribute('role') === 'alertdialog'
      && /Delete project\?/.test(alertText) && /cannot be undone/.test(alertText),
    alertText.replace(/\s+/g, ' ').slice(0, 80));
  await page.locator('button', { hasText: /^Cancel$/ }).first().click();
  await page.waitForTimeout(500);
  check('alert dialog cancel dismisses it', !(await alertPanel.isVisible().catch(() => false)), null);

  await page.locator('button', { hasText: /Delete project/ }).first().click();
  await page.waitForTimeout(500);
  await page.locator('button', { hasText: /^Delete$/ }).first().click();
  const alertRan = await waitForEvent('alert:delete');
  await page.waitForTimeout(600);
  check('alert dialog action runs its Python handler before closing',
    alertRan && !(await alertPanel.isVisible().catch(() => false)),
    { probe: probeSnapshot, visible: await alertPanel.isVisible().catch(() => false) });

  // ---- context menu -------------------------------------------------------- #
  await page.locator('[data-shadcn_context_menu_trigger]').first().click({ button: 'right' });
  await page.waitForTimeout(700);
  const ctx = page.locator('[data-shadcn_context_menu]').first();
  const ctxItems = await page.locator('[data-shadcn_context_menu] [role="menuitem"]').allInnerTexts().catch(() => []);
  check('context menu opens on right-click only when it is asked to',
    await ctx.isVisible().catch(() => false) && ctxItems.map((t) => t.trim()).join(',') === 'Copy,Cut,Delete',
    ctxItems);
  await page.locator('[data-shadcn_context_menu] [role="menuitem"]', { hasText: /^Copy$/ }).first().click();
  check('context menu selection reaches Python', await waitForEvent('context:copy'), probeSnapshot);

  // ---- hover card ---------------------------------------------------------- #
  await page.locator('button', { hasText: /^@nicegui$/ }).first().hover();
  await page.waitForTimeout(1200);
  const hoverCard = page.locator('[data-shadcn_hover_card_content]').first();
  const hoverText = await hoverCard.innerText().catch(() => '');
  check('hover card appears on hover with its content',
    await hoverCard.isVisible().catch(() => false) && /NiceGUI/.test(hoverText)
      && (await hoverCard.evaluate((el) => getComputedStyle(el).backgroundColor)) === await resolve(page, 'var(--popover)'),
    hoverText.replace(/\s+/g, ' ').slice(0, 60));
  await page.mouse.move(0, 0);
  await page.waitForTimeout(600);

  // ---- toast --------------------------------------------------------------- #
  await page.locator('button', { hasText: /Show toast/ }).first().click();
  await page.waitForTimeout(800);
  const toast = page.locator('[data-shadcn_toast]').first();
  const toastText = await toast.innerText().catch(() => '');
  check('toast opens on the Python `.open()` call with title and description',
    await toast.isVisible().catch(() => false) && /Deployment queued/.test(toastText)
      && /email you when it is live/.test(toastText) && await waitForEvent('toast:open'),
    toastText.replace(/\s+/g, ' ').slice(0, 70));
  const viewport = await page.evaluate(() => {
    const el = [...document.querySelectorAll('div,ol,ul')]
      .find((d) => (d.className ?? '').includes('max-h-screen') && getComputedStyle(d).position === 'fixed');
    return el ? { z: getComputedStyle(el).zIndex, bottom: getComputedStyle(el).bottom, right: getComputedStyle(el).right } : null;
  });
  check('toast provider pins the viewport to the requested corner',
    viewport !== null && viewport.z === '50' && viewport.bottom === '0px' && viewport.right === '0px', viewport);

  // ---- pagination / native select round trips ------------------------------ #
  await page.locator('[data-shadcn_pagination_next]').first().click();
  await page.waitForTimeout(500);
  check('pagination next page reaches Python and moves the marker',
    await waitForEvent('page:4')
      && (await page.locator('[data-shadcn_pagination] [aria-current="page"]').innerText()) === '4',
    probeSnapshot);
  await page.locator('[data-shadcn_native_select] select').selectOption('scale');
  await page.waitForTimeout(600);
  check('native select change reaches Python',
    await waitForEvent('native:scale')
      && (await page.locator('[data-shadcn_native_select] select').inputValue()) === 'scale',
    probeSnapshot);

  // ---- calendar / date picker ---------------------------------------------- #
  const calendar = await page.evaluate(() => {
    const cal = document.querySelector('[data-shadcn_calendar]');
    if (!cal) return null;
    const cells = [...cal.querySelectorAll('[data-reka-calendar-cell-trigger]')];
    return {
      heading: [...cal.querySelectorAll('*')].map((e) => e.textContent.trim()).find((t) => /^[A-Z][a-z]+ \d{4}$/.test(t)) ?? null,
      cells: cells.length,
      selected: cells.filter((c) => c.getAttribute('data-selected') === 'true').map((c) => c.getAttribute('data-value')),
      labelled: cells.filter((c) => (c.getAttribute('aria-label') ?? '').length > 0).length,
    };
  });
  check('calendar renders a labelled month grid with the Python date selected',
    calendar !== null && calendar.cells === 35 && calendar.selected.join(',') === '2026-03-15'
      && calendar.labelled === 35,
    calendar);
  await page.locator('[data-shadcn_calendar] [data-reka-calendar-cell-trigger][data-value="2026-03-10"]').first().click();
  await page.waitForTimeout(600);
  check('picking a calendar day reaches Python and moves the selection',
    await waitForEvent('calendar:2026-03-10')
      && (await page.evaluate(() => document.querySelector('[data-shadcn_calendar] [data-selected="true"]')?.getAttribute('data-value'))) === '2026-03-10',
    probeSnapshot);

  const dateTrigger = page.locator('button', { hasText: /2026/ }).first();
  check('date picker formats the Python date in its trigger',
    (await dateTrigger.innerText()).trim() === 'March 15, 2026', await dateTrigger.innerText());
  await dateTrigger.click();
  await page.waitForTimeout(600);
  const datePopover = page.locator('[data-shadcn_popover_content]').first();
  check('date picker opens a popover holding a calendar',
    await datePopover.isVisible().catch(() => false)
      && await page.locator('[data-shadcn_popover_content] [data-shadcn_calendar]').count() === 1,
    await page.locator('[data-shadcn_popover_content] [data-reka-calendar-cell-trigger]').count());
  await page.locator('[data-shadcn_popover_content] [data-reka-calendar-cell-trigger][data-value="2026-03-20"]').first().click();
  await page.waitForTimeout(700);
  check('date picker reports the picked date to Python and rewrites its trigger',
    await waitForEvent('date:2026-03-20')
      && (await dateTrigger.innerText()).trim() === 'March 20, 2026'
      && !(await datePopover.isVisible().catch(() => false)),
    { probe: probeSnapshot, trigger: await dateTrigger.innerText() });

  // ---- input OTP ------------------------------------------------------------ #
  const otp = await page.evaluate(() => {
    const root = document.querySelector('[data-shadcn_input_otp]');
    if (!root) return null;
    const input = root.querySelector('input');
    return {
      inputs: root.querySelectorAll('input').length,
      value: input?.value,
      maxlength: input?.getAttribute('maxlength'),
      aria: input?.getAttribute('aria-label'),
      slots: root.querySelectorAll('[data-slot="input-otp-slot"]').length,
      separators: root.querySelectorAll('[data-slot="input-otp-separator"]').length,
    };
  });
  check('input OTP renders one hidden input, six slots and a group separator',
    otp !== null && otp.inputs === 1 && otp.value === '123456' && otp.maxlength === '6'
      && otp.aria === 'One-time password' && otp.slots === 6 && otp.separators === 1,
    otp);
  await page.locator('[data-shadcn_input_otp] input').fill('654321');
  await page.waitForTimeout(700);
  check('typing into the OTP slots reaches Python',
    await waitForEvent('otp:654321')
      && (await page.locator('[data-shadcn_input_otp] input').inputValue()) === '654321',
    probeSnapshot);

  // ---- command palette ------------------------------------------------------ #
  const command = await page.evaluate(() => {
    const cmd = document.querySelector('[data-shadcn_command]');
    if (!cmd) return null;
    const input = cmd.querySelector('input');
    return {
      role: input?.getAttribute('role'),
      placeholder: input?.getAttribute('placeholder'),
      listbox: cmd.querySelectorAll('[role="listbox"]').length,
      options: [...cmd.querySelectorAll('[role="option"]')].map((o) => o.textContent.trim()),
      disabled: cmd.querySelectorAll('[role="option"][aria-disabled="true"]').length,
      shortcuts: [...cmd.querySelectorAll('span')].filter((s) => s.textContent.trim() === '⌘K').length,
    };
  });
  check('command palette renders a labelled listbox with grouped entries',
    command !== null && command.role === 'combobox'
      && command.placeholder === 'Type a command or search...'
      && command.listbox === 1 && command.options.length === 4 && command.disabled === 1
      && command.shortcuts === 1,
    command);
  await page.locator('[data-shadcn_command] [role="option"]').first().click();
  check('command palette selection reaches Python', await waitForEvent('command:calendar'), probeSnapshot);

  // ---- combobox -------------------------------------------------------------- #
  const comboTrigger = page.locator('[data-shadcn_combobox] button').first();
  check('combobox trigger is a collapsed combobox showing the Python value',
    await comboTrigger.getAttribute('role') === 'combobox'
      && await comboTrigger.getAttribute('data-state') === 'closed'
      && (await comboTrigger.innerText()).trim() === 'Next.js',
    await comboTrigger.innerText());
  await comboTrigger.click();
  await page.waitForTimeout(500);
  const comboPanel = await page.evaluate(() => {
    const root = document.querySelector('[data-shadcn_combobox]');
    return {
      expanded: root.querySelector('button')?.getAttribute('aria-expanded'),
      listbox: root.querySelectorAll('[role="listbox"]').length,
      search: root.querySelector('[role="listbox"] input')?.getAttribute('placeholder'),
      options: [...root.querySelectorAll('[role="option"]')].map((o) => o.textContent.trim()),
      selected: [...root.querySelectorAll('[role="option"]')]
        .filter((o) => o.getAttribute('data-selected') === 'true').length,
    };
  });
  check('combobox opens a filterable listbox with the current option marked',
    comboPanel.expanded === 'true' && comboPanel.listbox === 1 && comboPanel.search === 'Search...'
      && comboPanel.options.join(',') === 'Next.js,SvelteKit,Nuxt.js' && comboPanel.selected === 1,
    comboPanel);
  await page.locator('[data-shadcn_combobox] [role="option"]', { hasText: /^SvelteKit$/ }).first().click();
  await page.waitForTimeout(600);
  check('combobox selection reaches Python and updates the trigger',
    await waitForEvent('combobox:svelte') && (await comboTrigger.innerText()).trim() === 'SvelteKit',
    probeSnapshot);

  // ---- menubar --------------------------------------------------------------- #
  const menubar = await page.evaluate(() => {
    const bar = document.querySelector('[data-shadcn_menubar]');
    return bar ? {
      triggers: [...bar.querySelectorAll('button')].map((b) => b.textContent.trim()),
      state: [...bar.querySelectorAll('button')].map((b) => b.getAttribute('data-state')),
    } : null;
  });
  check('menubar renders one trigger per menu with none of them open',
    menubar !== null && menubar.triggers.join(',') === 'File,Edit'
      && menubar.state.every((s) => s === 'closed'),
    menubar);
  await page.locator('[data-shadcn_menubar] button', { hasText: /^File$/ }).first().click();
  await page.waitForTimeout(600);
  const fileItems = await page.locator('[role="menuitem"]').allInnerTexts().catch(() => []);
  check('menubar opens its panel with the items passed from Python',
    fileItems.map((t) => t.trim()).filter((t) => ['New', 'Open', 'Quit'].includes(t)).length === 3,
    fileItems);
  await page.locator('[role="menuitem"]', { hasText: /^New$/ }).first().click();
  check('menubar selection reaches Python', await waitForEvent('menubar:new'), probeSnapshot);

  // ---- navigation menu --------------------------------------------------------- #
  const navMenu = await page.evaluate(() => {
    const root = document.querySelector('[data-shadcn_navigation_menu]');
    if (!root) return null;
    return {
      orientation: root.getAttribute('data-orientation'),
      topLevel: root.querySelectorAll('ul > li').length,
      triggers: [...root.querySelectorAll('[data-navigation-menu-trigger]')].map((b) => b.textContent.trim()),
      links: [...root.querySelectorAll('a')].map((a) => a.textContent.trim()),
      // reka renders the panel lazily; a `data-reka-navigation-menu-content`
      // attribute is NOT emitted, so the panel is located through the trigger's
      // aria-controls instead of a guessed attribute.
      controls: root.querySelector('[data-navigation-menu-trigger]')?.getAttribute('aria-controls') ?? null,
    };
  });
  check('navigation menu renders top-level triggers and direct links',
    navMenu !== null && navMenu.orientation === 'horizontal' && navMenu.topLevel === 2
      && navMenu.triggers.join(',') === 'Getting started' && navMenu.links.join(',') === 'Components'
      && navMenu.controls !== null,
    navMenu);
  await page.locator('[data-shadcn_navigation_menu] [data-navigation-menu-trigger]').first().click();
  await page.waitForTimeout(700);
  const navPanel = await page.evaluate((id) => {
    const root = document.querySelector('[data-shadcn_navigation_menu]');
    const panel = [...root.querySelectorAll('ul')].find((u) => u.textContent.includes('Introduction'));
    return panel ? {
      matchesControls: panel.closest('[id]')?.id === id || panel.id === id,
      entries: [...panel.querySelectorAll('a')].map((a) => a.textContent.trim()),
      descriptions: [...panel.querySelectorAll('span')].filter((s) => /works|project|Add the/.test(s.textContent)).length,
      visible: panel.getBoundingClientRect().height > 0,
    } : null;
  }, navMenu.controls);
  check('navigation menu reveals a described panel on click',
    navPanel !== null && navPanel.visible && navPanel.entries.length === 2
      && navPanel.entries[0].replace(/\s+/g, '').startsWith('IntroductionHowthelibraryworks.')
      && navPanel.entries[1].replace(/\s+/g, '').startsWith('InstallationAddthepackagetoyourproject.')
      && navPanel.descriptions === 2 && navPanel.matchesControls,
    navPanel);
  await page.keyboard.press('Escape');
  await page.waitForTimeout(400);

  check('no console/page errors after all interactions',
    consoleErrors.length === 0, consoleErrors.slice(0, 5));

  // ---- light / dark ----------------------------------------------------- #
  await page.screenshot({ path: `${OUT_DIR}/_shot-light.png`, fullPage: true });
  const cardOf = () => page.evaluate(() => {
    const el = document.querySelector('.bg-card');
    return el ? getComputedStyle(el).backgroundColor : null;
  });
  const lightCard = await cardOf();
  check('light card paints var(--card)',
    lightCard === await resolve(page, 'var(--card)'), lightCard);

  await page.locator('button', { hasText: /^Dark mode$/ }).first().click();
  await page.waitForTimeout(600);
  check('dark mode toggles body.body--dark',
    await page.evaluate(() => document.body.classList.contains('body--dark')));
  const darkCard = await cardOf();
  check('dark card switches to the .dark token', darkCard !== lightCard, { light: lightCard, dark: darkCard });
  await page.screenshot({ path: `${OUT_DIR}/_shot-dark.png`, fullPage: true });

  // ---- layout sanity ---------------------------------------------------- #
  const overflow = await page.evaluate(() =>
    document.documentElement.scrollWidth - document.documentElement.clientWidth);
  check('no horizontal overflow', overflow <= 1, overflow);

  const clipping = await page.evaluate(() => [...document.querySelectorAll('.bg-card')]
    .filter((c) => c.scrollWidth > c.clientWidth + 1)
    .map((c) => c.querySelector('div')?.textContent?.slice(0, 20) ?? '?'));
  check('no card clips its content', clipping.length === 0, clipping);

  // A square `size='icon'` button with a visible label spills its text out of
  // its own 36px box, which is invisible to a page-level overflow check.
  const spilling = await page.evaluate(() => [...document.querySelectorAll('button')]
    .filter((b) => b.scrollWidth > b.clientWidth + 1)
    .map((b) => b.innerText.trim()));
  check('no button overflows its own box', spilling.length === 0, spilling);

  // NiceGUI hands `loopback` down as a Vue prop. A template that does not declare it receives it
  // in `$attrs`, and Vue renders that onto the root element — invalid HTML, and a reliable signal
  // that the template is missing the declaration.
  const leaked = await page.evaluate(() => [...document.querySelectorAll('[loopback]')]
    .map((el) => `${el.tagName.toLowerCase()}${el.id ? '#' + el.id : ''}`));
  check('no loopback prop leaks into the DOM', leaked.length === 0, leaked);

  console.log('\n' + JSON.stringify({ errors: consoleErrors, failures, button: btn }, null, 2));
} finally {
  await browser.close();
}

console.log(failures.length === 0
  ? '\nall visual checks passed'
  : `\n${failures.length} visual check(s) failed: ${failures.join(', ')}`);
process.exit(failures.length === 0 ? 0 : 1);

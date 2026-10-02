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

  console.log('\n' + JSON.stringify({ errors: consoleErrors, failures, button: btn }, null, 2));
} finally {
  await browser.close();
}

console.log(failures.length === 0
  ? '\nall visual checks passed'
  : `\n${failures.length} visual check(s) failed: ${failures.join(', ')}`);
process.exit(failures.length === 0 ? 0 : 1);

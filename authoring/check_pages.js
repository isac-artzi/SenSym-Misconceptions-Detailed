/* check_pages.js — headless verification for every course page.
 *
 *   node check_pages.js docs/s1/week01.html [more...]
 *   node check_pages.js --all
 *
 * Fails a page on: console errors, page errors, unrendered $math$,
 * blank canvases, missing local assets, or broken relative links.
 */
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

function collect(dir, out) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) { if (e.name !== 'vendor' && e.name !== 'assets') collect(p, out); }
    else if (e.name.endsWith('.html')) out.push(p);
  }
  return out;
}

(async () => {
  let files = process.argv.slice(2);
  if (files.length === 1 && files[0] === '--all') files = collect('docs', []).sort();
  if (!files.length) { console.error('usage: node check_pages.js <file.html>|--all'); process.exit(2); }

  const browser = await chromium.launch({ executablePath: process.env.PW_CHROME || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  let bad = 0;

  for (const f of files) {
    // deviceScaleFactor 2 = a Retina display. Run at 2, not 1: a whole class of
    // canvas sizing bugs is invisible at dpr 1 because multiplying by 1 is a no-op.
    const page = await browser.newPage({
      viewport: { width: 1100, height: 900 },
      deviceScaleFactor: 2,
    });
    const errs = [];
    page.on('console', m => { if (m.type() === 'error') errs.push('console: ' + m.text()); });
    page.on('pageerror', e => errs.push('pageerror: ' + e.message));
    page.on('requestfailed', r => errs.push('404/failed: ' + r.url().split('/').slice(-2).join('/')));

    await page.goto('file://' + path.resolve(f), { waitUntil: 'load' });
    await page.waitForTimeout(650);

    const res = await page.evaluate(() => {
      const out = {};
      out.katex = document.querySelectorAll('.katex').length;
      // unrendered math: a $...$ pair still sitting in visible text
      const txt = document.body.innerText;
      const m = txt.match(/\$[^$\n]{1,120}\$/g);
      out.rawMath = m ? m.slice(0, 3) : [];
      // blank canvases
      out.canvases = [];
      document.querySelectorAll('canvas').forEach(c => {
        const ctx = c.getContext('2d');
        let ink = 0;
        try {
          const d = ctx.getImageData(0, 0, c.width, c.height).data;
          for (let i = 0; i < d.length; i += 400) {
            if (d[i + 3] !== 0 && !(d[i] > 248 && d[i + 1] > 248 && d[i + 2] > 248)) ink++;
          }
        } catch (e) { ink = -1; }
        out.canvases.push({ id: c.id || '(anon)', ink, w: c.width, h: c.height });
      });
      // local links that point at files
      out.links = [...document.querySelectorAll('a[href]')]
        .map(a => a.getAttribute('href'))
        .filter(h => h && !h.startsWith('http') && !h.startsWith('#') && !h.startsWith('mailto'));
      out.exercises = document.querySelectorAll('.exercise').length;
      out.solutions = document.querySelectorAll('.exercise details').length;
      out.objectives = document.querySelectorAll('.objectives li').length;
      out.h2 = document.querySelectorAll('main h2').length;
      return out;
    });

    // Canvas geometry must survive redraws. Drive every slider a few times and
    // confirm no canvas changes rendered height — catches the class of bug where
    // a redraw re-reads an attribute it has already written to.
    const grew = await page.evaluate(async () => {
      const heights = () => [...document.querySelectorAll('canvas')]
        .map(c => Math.round(c.getBoundingClientRect().height));
      const before = heights();
      const sliders = [...document.querySelectorAll('.controls input[type=range]')];
      for (const r of sliders) {
        const step = parseFloat(r.step) || 1, max = parseFloat(r.max);
        for (let i = 0; i < 3; i++) {
          const next = parseFloat(r.value) + step;
          r.value = String(next > max ? parseFloat(r.min) : next);
          r.dispatchEvent(new Event('input'));
          await new Promise(res => setTimeout(res, 25));
        }
      }
      const after = heights();
      return before
        .map((h, i) => (h !== after[i]
          ? `${document.querySelectorAll('canvas')[i].id || i}: ${h}px -> ${after[i]}px`
          : null))
        .filter(Boolean);
    });

    // resolve relative links on disk
    const base = path.dirname(f);
    const broken = [...new Set(res.links)].filter(h => {
      const target = path.resolve(base, h.split('#')[0]);
      return !fs.existsSync(target);
    });

    const blank = res.canvases.filter(c => c.ink === 0);
    const problems = [];
    if (errs.length) problems.push(...[...new Set(errs)].slice(0, 4));
    if (res.rawMath.length) problems.push('unrendered math: ' + res.rawMath.join(' | '));
    if (blank.length) problems.push('blank canvas: ' + blank.map(c => c.id).join(', '));
    if (grew.length) problems.push('canvas resized on redraw: ' + grew.join('; '));
    if (broken.length) problems.push('broken link: ' + broken.join(', '));
    if (res.exercises && res.solutions < res.exercises) {
      problems.push(`only ${res.solutions}/${res.exercises} exercises have solutions`);
    }

    const tag = problems.length ? 'FAIL' : ' ok ';
    console.log(`[${tag}] ${f}  katex=${res.katex} h2=${res.h2} ex=${res.exercises} obj=${res.objectives} canvas=${res.canvases.length}`);
    problems.forEach(p => console.log('        · ' + p));
    if (problems.length) bad++;
    await page.close();
  }

  await browser.close();
  console.log(bad ? `\n${bad} page(s) failed.` : `\nAll ${files.length} page(s) passed.`);
  process.exit(bad ? 1 : 0);
})();

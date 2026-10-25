const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const htmlPath = path.join(root, 'index.html');
const readmePath = path.join(root, 'README.md');
const html = fs.readFileSync(htmlPath, 'utf8');
const readme = fs.readFileSync(readmePath, 'utf8');
const css = html;

test('index.html starts with DOCTYPE and sets lang="en"', () => {
  assert.match(html, /^<!doctype html>/i);
  assert.match(html, /<html[^>]+lang="en"/i);
});

test('head includes charset, viewport, title, and description meta', () => {
  assert.match(html, /<meta\s+charset="utf-8"/i);
  assert.match(html, /<meta\s+name="viewport"[^>]+width=device-width/i);
  assert.match(html, /<title>[^<]{10,}<\/title>/i);
  assert.match(html, /<meta\s+name="description"[^>]+content="[^"]{30,}"/i);
});

test('head includes complete OpenGraph and Twitter meta tags plus inline SVG favicon', () => {
  assert.match(html, /<meta\s+property="og:title"[^>]+content="[^"]+"/i);
  assert.match(html, /<meta\s+property="og:description"[^>]+content="[^"]+"/i);
  assert.match(html, /<meta\s+property="og:type"[^>]+content="website"/i);
  assert.match(html, /<meta\s+property="og:url"[^>]+content="https:\/\/aariv\.me\/snek-volt\/"/i);
  assert.match(html, /<meta\s+name="twitter:card"[^>]+content="summary"/i);
  assert.match(html, /<link\s+rel="icon"[^>]+href="data:image\/svg\+xml/i);
});

test('skip-link targets matching main landmark id and noscript fallback is present', () => {
  assert.match(html, /<a\s+class="[^"]*skip-link[^"]*"\s+href="#rig">Skip to main content<\/a>/);
  assert.match(html, /<main[^>]+id="rig"/);
  assert.match(html, /<noscript>[\s\S]+?<\/noscript>/i);
});

test('document has exactly one h1 and follows logical heading hierarchy', () => {
  const h1s = html.match(/<h1\b/gi) || [];
  assert.strictEqual(h1s.length, 1, `Expected 1 <h1>, found ${h1s.length}`);
  const headings = [...html.matchAll(/<h([1-6])\b/gi)].map(m => Number(m[1]));
  assert.strictEqual(headings[0], 1, 'First heading must be h1');
  for (let i = 1; i < headings.length; i++) {
    assert.ok(headings[i] - headings[i - 1] <= 1, `Heading jumped from h${headings[i - 1]} to h${headings[i]}`);
  }
});

test('all DOM id attributes in index.html are unique', () => {
  const htmlWithoutScripts = html.replace(/<script[\s\S]*?<\/script>/gi, '');
  const ids = [...htmlWithoutScripts.matchAll(/\sid="([^"]+)"/g)].map(m => m[1]);
  assert.ok(ids.length >= 5, 'Expected at least 5 id attributes in DOM');
  const seen = new Set();
  for (const id of ids) {
    assert.ok(!seen.has(id), `Duplicate DOM id found: ${id}`);
    seen.add(id);
  }
});

test('CSS includes overflow-x clip, focus-visible ring, prefers-reduced-motion, and tabular-nums', () => {
  assert.match(css, /overflow-x:\s*clip/);
  assert.match(css, /:focus-visible/);
  assert.match(css, /prefers-reduced-motion:\s*reduce/);
  assert.match(css, /font-variant-numeric:\s*tabular-nums/);
});

test('repository contains zero em-dashes, en-dashes, emojis, or personal contact leaks', () => {
  const dashRegex = /[\u2013\u2014]/;
  const emojiRegex = /[\u{1F300}-\u{1FAFF}]/u;
  assert.ok(!dashRegex.test(html), 'index.html contains an en-dash or em-dash');
  assert.ok(!dashRegex.test(readme), 'README.md contains an en-dash or em-dash');
  assert.ok(!emojiRegex.test(html), 'index.html contains an emoji');
  assert.ok(!emojiRegex.test(readme), 'README.md contains an emoji');
  assert.ok(!/[a-z0-9._%+-]+@gmail\.com/i.test(html + readme), 'Personal email leaked');
});

test('circuit snake board, oscilloscope rail monitor, polarity controls, and audio synth exist', () => {
  for (const id of ['rig', 'sound', 'pause', 'score', 'best', 'length', 'pol-name', 'charge-num', 'charge-meter', 'board', 'overlay', 'btn-pol', 'btn-dash', 'scope', 'ro-rail', 'ro-ripple', 'ro-clock', 'status']) {
    assert.ok(html.includes(`id="${id}"`), `Missing DOM id ${id}`);
  }
  assert.match(html, /AudioContext|webkitAudioContext/);
});

test('desktop Pygame companion script and sprite assets exist alongside web build', () => {
  assert.ok(fs.existsSync(path.join(root, 'main.py')));
  assert.ok(fs.existsSync(path.join(root, 'requirements.txt')));
  assert.ok(fs.existsSync(path.join(root, 'assets/capacitor_orb.png')));
  assert.ok(fs.existsSync(path.join(root, 'assets/emp_hazard.png')));
});

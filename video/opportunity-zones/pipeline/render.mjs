// Frame renderer: loads a scene HTML with a deterministic window.seek(t),
// captures PNG frames at a fixed fps.
// usage: node render.mjs <scene.html> <duration> <fps> <outDir> [alpha]
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import { mkdirSync, existsSync } from 'fs';
import { resolve } from 'path';

const [, , htmlPath, durationS, fpsS, outDir, alphaFlag] = process.argv;
const duration = parseFloat(durationS);
const fps = parseFloat(fpsS);
const alpha = alphaFlag === 'alpha';
const total = Math.round(duration * fps);
mkdirSync(outDir, { recursive: true });

const browser = await chromium.launch({ args: ['--force-color-profile=srgb', '--disable-lcd-text', '--hide-scrollbars'] });
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
await page.goto('file://' + resolve(htmlPath));
await page.evaluate(() => document.fonts.ready);
await page.waitForFunction(() => typeof window.seek === 'function');
// let any setup (map parsing etc.) finish
await page.waitForFunction(() => window.__ready !== false);

const t0 = Date.now();
for (let i = 0; i < total; i++) {
  const t = i / fps;
  await page.evaluate((tt) => window.seek(tt), t);
  const name = `${outDir}/f${String(i).padStart(5, '0')}.png`;
  if (existsSync(name)) continue; // resume support
  await page.screenshot({ path: name, omitBackground: alpha });
  if (i % 60 === 0) {
    const rate = (i + 1) / ((Date.now() - t0) / 1000);
    console.log(`frame ${i}/${total} (${rate.toFixed(1)} fps capture)`);
  }
}
await browser.close();
console.log(`done: ${total} frames -> ${outDir}`);

const { chromium } = require('playwright-core');
const path = require('path');
const fs = require('fs');

const FPS = 30;

(async () => {
  const outDir = path.join(__dirname, 'frames');
  fs.mkdirSync(outDir, { recursive: true });
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--no-sandbox', '--force-color-profile=srgb', '--disable-lcd-text'] });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  await page.goto('file://' + path.join(__dirname, 'index.html'));
  await page.waitForFunction('window.renderFrame !== undefined');
  await page.evaluate(async () => { await document.fonts.ready; });
  const total = await page.evaluate('window.TOTAL');
  const nFrames = Math.ceil(total * FPS);
  console.log('rendering', nFrames, 'frames @', FPS, 'fps');
  const t0 = Date.now();
  for (let i = 0; i < nFrames; i++) {
    const t = i / FPS;
    await page.evaluate(`renderFrame(${t})`);
    await page.screenshot({ path: path.join(outDir, `f${String(i).padStart(5, '0')}.png`), type: 'png' });
    if (i % 150 === 0) {
      const el = (Date.now() - t0) / 1000;
      console.log(`frame ${i}/${nFrames}  elapsed ${el.toFixed(0)}s  eta ${(el / Math.max(i, 1) * (nFrames - i)).toFixed(0)}s`);
    }
  }
  await browser.close();
  console.log('DONE', nFrames, 'frames in', ((Date.now() - t0) / 1000).toFixed(0), 's');
})();

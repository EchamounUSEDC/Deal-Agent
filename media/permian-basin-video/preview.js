const { chromium } = require('playwright-core');
const path = require('path');

(async () => {
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--no-sandbox', '--force-color-profile=srgb'] });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  await page.goto('file://' + path.join(__dirname, 'index.html'));
  await page.waitForFunction('window.renderFrame !== undefined');
  await page.evaluate(async () => { await document.fonts.ready; });
  const times = process.argv[2] ? process.argv[2].split(',').map(Number) : [2.5, 6, 13, 24, 26, 35, 47, 58, 61, 69, 79];
  for (const t of times) {
    await page.evaluate(`renderFrame(${t})`);
    await page.screenshot({ path: path.join(__dirname, `preview_${t.toFixed(1)}.png`), type: 'png' });
    console.log('preview at', t);
  }
  await browser.close();
})();

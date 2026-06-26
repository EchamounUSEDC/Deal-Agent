// =============================================================================
// render-video.mjs — render the casino display to a video file (offline).
// -----------------------------------------------------------------------------
// Spins up a headless Chromium, loads index.html in deterministic capture mode,
// drives the animation one frame at a time on a virtual clock, screenshots each
// frame, and pipes the frames straight into ffmpeg to encode an MP4 (H.264).
//
// Usage:
//   node render-video.mjs [--seconds 30] [--fps 60] [--width 1920] [--height 1080]
//                         [--out casino.mp4] [--title "..."] [--subtitle "..."]
//                         [--crf 18] [--webm]
//
// Requires: playwright (global) + an ffmpeg binary. We auto-discover ffmpeg
// from imageio-ffmpeg (H.264) and fall back to Playwright's bundled VP8 build.
// =============================================================================

import { chromium } from 'playwright';
import { spawn, execSync } from 'node:child_process';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// ---- args -------------------------------------------------------------------
const argv = process.argv.slice(2);
function arg(name, def) {
  const i = argv.indexOf(`--${name}`);
  if (i === -1) return def;
  const v = argv[i + 1];
  return v && !v.startsWith('--') ? v : true;
}
const SECONDS = parseFloat(arg('seconds', '30'));
const FPS     = parseInt(arg('fps', '60'), 10);
const WIDTH   = parseInt(arg('width', '1920'), 10);
const HEIGHT  = parseInt(arg('height', '1080'), 10);
const CRF     = parseInt(arg('crf', '18'), 10);
const WEBM    = !!arg('webm', false);
const TITLE   = arg('title', null);
const SUBT    = arg('subtitle', null);
const SS      = parseFloat(arg('ss', '2'));   // supersample factor (renders at WIDTH*SS, downscales)
const OUT     = arg('out', WEBM ? 'casino.webm' : 'casino.mp4');
const TOTAL_FRAMES = Math.round(SECONDS * FPS);
const SHOOT_W = Math.round(WIDTH * SS);
const SHOOT_H = Math.round(HEIGHT * SS);

// ---- locate ffmpeg ----------------------------------------------------------
function findFfmpeg() {
  // 1) imageio-ffmpeg static build (has libx264) — preferred for MP4.
  try {
    const p = execSync('python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())"',
      { stdio: ['ignore', 'pipe', 'ignore'] }).toString().trim();
    if (p && fs.existsSync(p)) return { bin: p, h264: true };
  } catch {}
  // 2) system ffmpeg
  try {
    const p = execSync('command -v ffmpeg', { stdio: ['ignore', 'pipe', 'ignore'] }).toString().trim();
    if (p) return { bin: p, h264: true };
  } catch {}
  // 3) Playwright's bundled ffmpeg (VP8/WebM only).
  const guess = '/opt/pw-browsers/ffmpeg-1011/ffmpeg-linux';
  if (fs.existsSync(guess)) return { bin: guess, h264: false };
  throw new Error('No ffmpeg found. `pip install imageio-ffmpeg` or install ffmpeg.');
}
const ff = findFfmpeg();
const useWebm = WEBM || !ff.h264;
const outFile = useWebm ? OUT.replace(/\.mp4$/, '.webm') : OUT;
if (useWebm && !ff.h264) console.warn('! Only VP8 ffmpeg available — encoding WebM instead of MP4.');

// ---- tiny static server -----------------------------------------------------
const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript',
  '.css': 'text/css', '.json': 'application/json', '.png': 'image/png', '.map': 'application/json' };
const server = http.createServer((req, res) => {
  const url = decodeURIComponent(req.url.split('?')[0]);
  let file = path.join(__dirname, url === '/' ? 'index.html' : url);
  if (!file.startsWith(__dirname)) { res.writeHead(403).end(); return; }
  fs.readFile(file, (err, data) => {
    if (err) { res.writeHead(404).end('not found'); return; }
    res.writeHead(200, { 'Content-Type': MIME[path.extname(file)] || 'application/octet-stream' });
    res.end(data);
  });
});
await new Promise(r => server.listen(0, r));
const port = server.address().port;

// ---- build page URL ---------------------------------------------------------
const q = new URLSearchParams({ capture: '1', fps: String(FPS) });
if (TITLE) q.set('title', TITLE);
if (SUBT)  q.set('subtitle', SUBT);
const pageUrl = `http://127.0.0.1:${port}/index.html?${q.toString()}`;

console.log(`> Rendering ${TOTAL_FRAMES} frames, shoot ${SHOOT_W}x${SHOOT_H} (${SS}x SSAA) -> ${WIDTH}x${HEIGHT} ${FPS}fps (${SECONDS}s) -> ${outFile}`);

// ---- ffmpeg: read PNG frames from stdin, encode -----------------------------
// Downscale the supersampled frames to the target size with a sharp Lanczos
// filter — this is what removes aliasing/pixelation.
const scaleFilter = `scale=${WIDTH}:${HEIGHT}:flags=lanczos`;
const ffArgs = useWebm
  ? ['-y', '-f', 'image2pipe', '-framerate', String(FPS), '-i', 'pipe:0',
     '-vf', scaleFilter,
     '-c:v', 'libvpx', '-b:v', '8M', '-crf', '8', '-pix_fmt', 'yuv420p', outFile]
  : ['-y', '-f', 'image2pipe', '-framerate', String(FPS), '-i', 'pipe:0',
     '-vf', scaleFilter,
     '-c:v', 'libx264', '-preset', 'medium', '-crf', String(CRF),
     '-pix_fmt', 'yuv420p', '-movflags', '+faststart', outFile];

const ffproc = spawn(ff.bin, ffArgs, { cwd: __dirname, stdio: ['pipe', 'inherit', 'inherit'] });
const ffDone = new Promise((resolve, reject) => {
  ffproc.on('close', code => code === 0 ? resolve() : reject(new Error('ffmpeg exited ' + code)));
  ffproc.on('error', reject);
});

// ---- launch browser ---------------------------------------------------------
const browser = await chromium.launch({
  headless: true,
  args: [
    '--use-gl=angle', '--use-angle=swiftshader',   // reliable software WebGL in headless
    '--enable-webgl', '--ignore-gpu-blocklist',
    '--no-sandbox', '--disable-dev-shm-usage',
    `--window-size=${WIDTH},${HEIGHT}`,
  ],
});
const page = await browser.newPage({ viewport: { width: WIDTH, height: HEIGHT }, deviceScaleFactor: SS });
page.on('pageerror', e => console.error('PAGE ERROR:', e.message));
page.on('console', m => { if (m.type() === 'error') console.error('console:', m.text()); });

await page.goto(pageUrl, { waitUntil: 'load' });
await page.waitForFunction('window.__captureReady === true', null, { timeout: 60000 });
console.log('> Scene warmed up, capturing...');

// ---- frame loop -------------------------------------------------------------
function writeFrame(buf) {
  return new Promise((resolve) => {
    if (!ffproc.stdin.write(buf)) ffproc.stdin.once('drain', resolve);
    else resolve();
  });
}

const t0 = Date.now();
for (let i = 0; i < TOTAL_FRAMES; i++) {
  await page.evaluate('window.__renderFrame()');
  const png = await page.screenshot({ type: 'png' });
  await writeFrame(png);
  if (i % FPS === 0 || i === TOTAL_FRAMES - 1) {
    const pct = (((i + 1) / TOTAL_FRAMES) * 100).toFixed(0);
    process.stdout.write(`\r  frame ${i + 1}/${TOTAL_FRAMES} (${pct}%)   `);
  }
}
process.stdout.write('\n');

ffproc.stdin.end();
await browser.close();
server.close();
await ffDone;

const secs = ((Date.now() - t0) / 1000).toFixed(1);
const size = (fs.statSync(path.join(__dirname, outFile)).size / 1e6).toFixed(1);
console.log(`> Done in ${secs}s -> ${outFile} (${size} MB)`);

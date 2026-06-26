import { chromium } from 'playwright';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const __dirname = path.dirname(fileURLToPath(import.meta.url));

const MIME = { '.html':'text/html','.js':'text/javascript','.css':'text/css','.png':'image/png','.json':'application/json' };
const server = http.createServer((req,res)=>{
  let f = path.join(__dirname, req.url.split('?')[0]==='/'?'index.html':req.url.split('?')[0]);
  fs.readFile(f,(e,d)=>{ if(e){res.writeHead(404).end();return;} res.writeHead(200,{'Content-Type':MIME[path.extname(f)]||'application/octet-stream'}); res.end(d); });
});
await new Promise(r=>server.listen(0,r));
const port = server.address().port;

const browser = await chromium.launch({ headless:true, args:['--use-gl=angle','--use-angle=swiftshader','--no-sandbox'] });
const page = await browser.newPage();
await page.goto(`http://127.0.0.1:${port}/index.html`, { waitUntil:'load' });
await page.waitForFunction('window.__TC');
const which = process.argv[2] || 'cardBack';
const dataUrl = await page.evaluate((w)=> window.__TC[w].length === 0 ? window.__TC[w]().image.toDataURL() : window.__TC[w]().image.toDataURL(), which);
const b64 = dataUrl.replace(/^data:image\/png;base64,/, '');
fs.writeFileSync(path.join(__dirname, `texcheck-${which}.png`), Buffer.from(b64,'base64'));
console.log(`wrote texcheck-${which}.png`);
await browser.close(); server.close();

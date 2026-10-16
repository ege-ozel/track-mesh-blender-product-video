// Captures the demo-ui-v4 build (real desktop source, synthetic status) for each Studio B state.
// 'ask' adds the native question the real Get shows before files change (ProjectCard.tsx dawClosed →
// tauri-plugin-dialog). The page cannot open a native dialog, so the capture draws a Windows-style one
// with the same title, message and buttons over the app.
const path = require('node:path');
const fs = require('node:fs');
const http = require('node:http');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || 'C:/Users/4D/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root = path.resolve(__dirname, '..');
const out = path.join(root, 'assets/screens/v4');
const states = {idle: 'Neon Forest', new: 'New version from Studio A', ask: 'New version from Studio A',
  get97: '97 %', get98: '98 %', get99: '99 %', done: "Studio A's version"};
const DIALOG = {title: 'Is this project closed in your DAW?', message: "TrackMesh will replace the files in this folder with Studio A's version.",
  ok: "Yes, it's closed", cancel: 'Cancel'};
function drawDialog({title, message, ok, cancel}) {
  const box = document.createElement('div');
  // Drawn at 150 % (a common Windows display scale) so it reads on the 3D screen. Dimmed a little: on the lit 3D screen a pure white panel clips and blooms over its own text.
  box.innerHTML = `<div style="position:fixed;inset:0;display:flex;align-items:center;justify-content:center;z-index:9999;font-family:'Segoe UI',sans-serif;filter:brightness(.7)">
    <div style="transform:scale(1.5);width:470px;background:#fff;border:1px solid #8a8a8a;border-radius:8px;box-shadow:0 18px 50px rgba(0,0,0,.55);overflow:hidden;color:#1a1a1a">
      <div style="display:flex;align-items:center;height:32px;padding:0 0 0 12px;background:#f3f3f3;font-size:12px">
        <span style="flex:1">${title}</span><span style="width:46px;text-align:center;font-size:14px">✕</span></div>
      <div style="padding:22px 22px 26px;font-size:14px;line-height:1.45;background:#fff">${message}</div>
      <div style="display:flex;justify-content:flex-end;gap:8px;padding:14px 16px;background:#f0f0f0;border-top:1px solid #dfdfdf">
        <span style="min-width:96px;padding:5px 14px;text-align:center;font-size:13px;border:2px solid #0067c0;border-radius:4px;background:#fdfdfd">${ok}</span>
        <span style="min-width:96px;padding:6px 14px;text-align:center;font-size:13px;border:1px solid #c8c8c8;border-radius:4px;background:#fdfdfd">${cancel}</span></div>
    </div></div>`;
  document.body.appendChild(box);
}
(async () => {
  fs.mkdirSync(out, {recursive: true});
  const base = path.join(root, 'demo-ui-v4/dist');
  const server = http.createServer((req, res) => {
    const name = decodeURIComponent(req.url.split('?')[0]);
    const file = path.resolve(base, '.' + (name === '/' ? '/index.html' : name));
    if (!file.startsWith(base + path.sep)) {res.writeHead(403); res.end(); return;}
    fs.readFile(file, (err, data) => {
      if (err) {res.writeHead(404); res.end(); return;}
      res.setHeader('Content-Type', file.endsWith('.js') ? 'text/javascript' : file.endsWith('.css') ? 'text/css' : 'text/html'); res.end(data);
    });
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const browser = await chromium.launch({channel: 'chrome', headless: true});
  const log = {};
  try {
    for (const [state, expect] of Object.entries(states)) {
      const page = await browser.newPage({viewport: {width: 1536, height: 864}, deviceScaleFactor: 1.25, locale: 'en-GB', timezoneId: 'Europe/Istanbul'});
      const errors = [];
      page.on('pageerror', e => errors.push(e.message));
      await page.addInitScript(() => { localStorage.setItem('trackmesh.lang', 'en'); });
      await page.route('**/*', route => new URL(route.request().url()).hostname === '127.0.0.1' ? route.continue() : route.abort());
      await page.goto(`http://127.0.0.1:${server.address().port}/?state=${state}`);
      await page.getByText(expect).first().waitFor();
      if (state === 'ask') await page.evaluate(drawDialog, DIALOG);
      await page.evaluate(() => document.fonts.ready);
      await page.waitForTimeout(300);
      const file = path.join(out, `app-${state}.png`);
      await page.screenshot({path: file});
      log[state] = {file, errors, body: await page.locator('body').innerText()};
      await page.close();
      if (errors.length) throw new Error(errors.join('\n'));
    }
    fs.writeFileSync(path.join(root, 'logs/ui-capture-v4.json'), JSON.stringify(log, null, 2));
    console.log('Captured ' + Object.keys(log).join(', '));
  } finally {await browser.close(); await new Promise(resolve => server.close(resolve));}
})().catch(e => {console.error(e); process.exitCode = 1;});

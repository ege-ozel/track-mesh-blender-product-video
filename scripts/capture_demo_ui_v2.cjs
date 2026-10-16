// Captures the demo-ui-v2 build (real desktop source, synthetic status) for each Studio B state.
const path = require('node:path');
const fs = require('node:fs');
const http = require('node:http');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || 'C:/Users/4D/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root = path.resolve(__dirname, '..');
const out = path.join(root, 'assets/screens/v2');
const states = {idle: 'Neon Forest', new: 'New version from Studio A', getting: "Getting Studio A's version", done: "Studio A's version"};
(async () => {
  fs.mkdirSync(out, {recursive: true});
  const base = path.join(root, 'demo-ui-v2/dist');
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
      await page.evaluate(() => document.fonts.ready);
      await page.waitForTimeout(300);
      const file = path.join(out, `app-${state}.png`);
      await page.screenshot({path: file});
      log[state] = {file, errors, body: await page.locator('body').innerText()};
      await page.close();
      if (errors.length) throw new Error(errors.join('\n'));
    }
    fs.writeFileSync(path.join(root, 'logs/ui-capture-v2.json'), JSON.stringify(log, null, 2));
    console.log('Captured ' + Object.keys(log).join(', '));
  } finally {await browser.close(); await new Promise(resolve => server.close(resolve));}
})().catch(e => {console.error(e); process.exitCode = 1;});

const path = require('node:path');
const fs = require('node:fs');
const http = require('node:http');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || 'C:/Users/4D/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root = path.resolve(__dirname, '..');
(async () => {
  const base = path.join(root, 'demo-ui/dist');
  const server = http.createServer((req, res) => {
    const name = decodeURIComponent(req.url.split('?')[0]);
    const file = path.resolve(base, '.' + (name === '/' ? '/index.html' : name));
    if (!file.startsWith(base + path.sep)) {res.writeHead(403);res.end();return;}
    fs.readFile(file, (err, data) => {
      if (err) {res.writeHead(404);res.end();return;}
      res.setHeader('Content-Type', file.endsWith('.js') ? 'text/javascript' : file.endsWith('.css') ? 'text/css' : 'text/html');res.end(data);
    });
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const browser = await chromium.launch({channel: 'chrome', headless: true});
  try {
    const page = await browser.newPage({viewport: {width:1536,height:864},deviceScaleFactor:1.25,locale:'en-GB',timezoneId:'Europe/Istanbul'});
    const errors=[];
    page.on('pageerror', e => errors.push(e.message));
    await page.route('**/*', route => new URL(route.request().url()).hostname === '127.0.0.1' ? route.continue() : route.abort());
    await page.goto(`http://127.0.0.1:${server.address().port}/`);
    await page.getByRole('heading',{name:'Neon Forest Demo'}).waitFor();
    await page.evaluate(() => document.fonts.ready);
    const screenshot=path.join(root,'assets/screens/trackmesh.png');
    if (fs.existsSync(screenshot)) throw new Error('Screenshot already exists; choose a new version.');
    await page.screenshot({path:screenshot});
    const details={errors,viewport:{width:1536,height:864,scale:1.25},raster:{width:1920,height:1080},body:await page.locator('body').innerText()};
    fs.writeFileSync(path.join(root,'logs/ui-capture.json'),JSON.stringify(details,null,2));
    if(errors.length) throw new Error(errors.join('\n'));
    console.log('Created 1920x1080 real React screenshot: '+screenshot);
  } finally {await browser.close();await new Promise(resolve=>server.close(resolve));}
})().catch(e=>{console.error(e);process.exitCode=1});

// Reflow the approved synthetic UI wording independently for each aspect ratio.
const fs=require('node:fs'),path=require('node:path');
const {chromium}=require('C:/Users/4D/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=path.resolve(__dirname,'..'),out=path.join(root,'assets/screens/v10-edit');
const refresh99=process.argv.includes('--refresh-transfer99');
if(fs.existsSync(path.join(out,'manifest.json'))&&!refresh99)throw Error('Preserve previous completed UI assets');fs.mkdirSync(out,{recursive:true});
const capture=fs.readFileSync(path.join(root,'scripts/capture_demo_ui_v5.cjs'),'utf8');
const dialog=JSON.parse(capture.match(/const DIALOG = (\{[^\r\n]+\});/)[1]);
const escape=s=>s.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
function html(aspect,state){
 const mobile=aspect==='9x16',W=mobile?1080:1920,H=mobile?1920:1080;
 const isDialog=state==='dialog',done=state==='done',isTransfer=state.startsWith('transfer');
 const pct=isTransfer?Number(state.slice(-2)):null,amount=pct===97?'44.0':pct===98?'29.0':'11.0';
 const title=isDialog||state==='get' ? "Get it when you're ready." : done?"Got Studio A's version ✓":"Getting Studio A's version…";
 let body;
 if(isDialog){body=`<section class="dialog"><header>${escape(dialog.title)}</header><div class="message">${escape(dialog.message)}</div><footer><button id="confirm-get">Get</button><button>Cancel</button></footer></section>`;}
 else{
 body=`<section class="card"><div class="head"><strong>Neon Forest</strong><span>Connected · Studio A</span></div>
 <div class="notice">${done?"You have Studio A's latest version":"New version from Studio A · 21.10.2026 19:31"}</div>
 ${state==='get'?`<p>Brings Studio A's latest version into this folder.</p><button id="card-get">Get Studio A's version</button>`:
 done?`<div class="complete">Got Studio A's version ✓</div>`:
 `<div class="counts">${amount} MB left · ${pct} %</div><div class="track"><i style="width:${pct}%"></i></div><button class="stop">Stop</button>`}
 </section>`;
 }
 const uiTop=mobile?(isDialog?280:360):(isDialog?225:285);
 return `<!doctype html><meta charset="utf-8"><style>
 *{box-sizing:border-box}body{margin:0;width:${W}px;height:${H}px;background:#0b121b;color:#f5f7f7;font-family:'Segoe UI',sans-serif}
 h1{position:absolute;left:${mobile?60:190}px;top:${mobile?84:60}px;margin:0;font-size:${mobile?54:64}px;font-weight:600}
 .qualifier{position:absolute;left:${mobile?60:190}px;top:${mobile?178:157}px;color:#6ed9c2;font-size:${mobile?30:28}px}
 section{position:absolute;left:${mobile?60:190}px;top:${uiTop}px;width:${mobile?960:1540}px;border:2px solid #304452;border-radius:12px;overflow:hidden}
 .dialog{background:#fff;color:#1a1a1a;width:${mobile?960:1380}px;left:${mobile?60:270}px}
 .dialog header{padding:22px 28px;background:#f1f1f1;border-bottom:1px solid #ccc;font-size:${mobile?38:36}px}
 .message{padding:28px;font-size:${mobile?38:32}px;line-height:1.42;white-space:pre-line}
 .dialog footer{display:flex;justify-content:flex-end;gap:18px;padding:22px;background:#f0f0f0;border-top:1px solid #ddd}
 button{font:inherit;font-size:${mobile?38:34}px;padding:16px 28px;border-radius:6px;border:2px solid #c8c8c8;background:#fafafa;color:#1a1a1a}
 #confirm-get{border:3px solid #0067c0;min-width:200px}.dialog footer button{min-width:200px}
 .card{padding:${mobile?40:50}px;background:#142130;min-height:${mobile?810:470}px}
 .head{display:flex;flex-direction:${mobile?'column':'row'};justify-content:space-between;gap:24px}.head strong{font-size:${mobile?54:52}px}.head span{color:#82dfb8;font-size:${mobile?30:28}px}
 .notice{margin:${mobile?38:20}px 0;padding:${mobile?26:20}px;border:1px solid #37526c;border-radius:9px;font-size:${mobile?34:30}px}
 p{font-size:${mobile?40:34}px;line-height:1.4;margin:36px 0}
 #card-get{display:block;background:#7fdfb9;border-color:#a4efcf;width:${mobile?'100%':'auto'};font-size:${mobile?40:34}px}
 .counts{font-size:${mobile?40:34}px;color:#b2c2c7;text-align:right;margin:20px 0}
 .track{height:${mobile?18:16}px;border-radius:12px;background:#6d7377;overflow:hidden}.track i{height:100%;display:block;background:#91d8be;border-radius:12px}
 .stop{margin-top:35px;color:#f5f7f7;background:#1b2d40;border-color:#37526c}
 .complete{color:#82dfb8;font-size:${mobile?48:54}px;line-height:1.4;margin:70px 0 40px}
 </style><h1>${escape(title)}</h1>${isDialog?'<div class="qualifier">Reconstructed confirmation</div>':''}${body}`;
}
(async()=>{const browser=await chromium.launch({channel:'chrome',headless:true});let report=refresh99?JSON.parse(fs.readFileSync(path.join(out,'manifest.json'),'utf8')):{dialog,assets:{}};
try{for(const aspect of ['16x9','9x16'])for(const state of (refresh99?['transfer99']:['get','dialog','transfer97','transfer98','transfer99','done'])){
 const mobile=aspect==='9x16',p=await browser.newPage({viewport:{width:mobile?1080:1920,height:mobile?1920:1080},deviceScaleFactor:1});
 await p.route('**/*',r=>r.abort());await p.setContent(html(aspect,state));await p.evaluate(()=>document.fonts.ready);
 const section=await p.locator('section').boundingBox();
 if(section.y+section.height>(state==='dialog'?(mobile?1770:1015):(mobile?1490:870)))throw Error(`UI exceeds allotted area: ${aspect} ${state} ${JSON.stringify(section)}`);
 const buttons={};for(const id of ['card-get','confirm-get'])if(await p.locator('#'+id).count())buttons[id]=await p.locator('#'+id).boundingBox();
 const file=path.join(out,`${aspect}-${state}.png`);await p.screenshot({path:file});
 report.assets[`${aspect}-${state}`]={file,section,buttons,body:await p.locator('section').innerText()};await p.close();
}fs.writeFileSync(path.join(out,'manifest.json'),JSON.stringify(report,null,2));console.log('Captured 12 UI inserts; exact dialog wording retained.');
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});

const path=require('node:path'), fs=require('node:fs');
const {chromium}=require('C:/Users/4D/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const out=path.resolve(__dirname,'../renders/previews/'+(process.argv[2]||'studios-v09-mobile-get-trial02'));
(async()=>{const b=await chromium.launch({channel:'chrome',headless:true});try{
 const p=await b.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
 await p.route('**/*',r=>r.request().url().startsWith('file:')?r.continue():r.abort());
 await p.goto('file:///'+path.join(out,'confirmation.html').replaceAll('\\','/'));
 await p.evaluate(()=>document.fonts.ready);
 const rect=await p.locator('.dialog').boundingBox();
 if(rect.y+rect.height>1750)throw Error('Dialog overlaps disclosure');
 fs.writeFileSync(path.join(out,'button.json'),JSON.stringify(await p.locator('#get').boundingBox()));
 await p.screenshot({path:path.join(out,'confirmation.png')});
 console.log(JSON.stringify({dialog:rect,body:await p.locator('.body').innerText()}));
}finally{await b.close()}})().catch(e=>{console.error(e);process.exitCode=1});

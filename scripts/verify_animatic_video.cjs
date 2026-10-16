// Inspect native Chrome decoding and seek representative concept states.
const http=require('node:http');const fs=require('node:fs');const path=require('node:path');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'C:/Users/4D/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=path.resolve(__dirname,'..');const version=process.argv[2]||'v04';
const videoFile=path.join(root,`renders/previews/animatic-${version}-3s.webm`);
(async()=>{
 const server=http.createServer((req,res)=>{
  if(req.url==='/') {res.setHeader('Content-Type','text/html');res.end('<!doctype html><html><body style="margin:0;background:#080b0f"><video width="960" height="540" preload="auto" muted src="/clip.webm"></video></body></html>');return;}
  if(req.url==='/clip.webm'){
   const length=fs.statSync(videoFile).size;res.setHeader('Content-Type','video/webm');res.setHeader('Accept-Ranges','bytes');
   const match=/^bytes=(\d+)-(\d*)$/.exec(req.headers.range||'');
   if(match){const start=Number(match[1]);const end=match[2]?Math.min(Number(match[2]),length-1):length-1;res.writeHead(206,{'Content-Range':`bytes ${start}-${end}/${length}`,'Content-Length':end-start+1});fs.createReadStream(videoFile,{start,end}).pipe(res);}
   else{res.setHeader('Content-Length',length);fs.createReadStream(videoFile).pipe(res);}return;
  }
  res.writeHead(404);res.end();
 });
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
 const browser=await chromium.launch({channel:'chrome',headless:true});
 try {
  const page=await browser.newPage({viewport:{width:960,height:540}});
  await page.goto(`http://127.0.0.1:${server.address().port}/`);
  await page.waitForFunction(()=>{const v=document.querySelector('video');return v.readyState>=2&&Number.isFinite(v.duration)});
  const info=await page.evaluate(()=>{const v=document.querySelector('video');return {duration:v.duration,width:v.videoWidth,height:v.videoHeight,error:v.error?.message||null}});
  if(Math.abs(info.duration-3)>.02||info.width!==960||info.height!==540||info.error)throw new Error(JSON.stringify(info));
  const seeks=[];
  for(const [name,time] of [['wide',.5],['save',1.45],['settle',1.98],['ready',2.7]]) {
   const presented=await page.evaluate(t=>new Promise((resolve,reject)=>{
    const v=document.querySelector('video');
    v.addEventListener('error',reject,{once:true});
    const timeout=setTimeout(()=>reject(new Error('Presented frame timeout at '+t)),8000);
    const onFrame=(_,meta)=>{
      if(Math.abs(meta.mediaTime-t)>.06){v.requestVideoFrameCallback(onFrame);return;}
      clearTimeout(timeout);resolve({mediaTime:meta.mediaTime,presentedFrames:meta.presentedFrames});
    };
    v.requestVideoFrameCallback(onFrame);
    v.currentTime=t;
   }),time);
   const data=await page.evaluate(()=>{const v=document.querySelector('video');const c=document.createElement('canvas');c.width=v.videoWidth;c.height=v.videoHeight;c.getContext('2d').drawImage(v,0,0);return c.toDataURL('image/png').split(',')[1]});
   fs.writeFileSync(path.join(root,`logs/video-${version}-${name}.png`),Buffer.from(data,'base64'));
   if(Math.abs(presented.mediaTime-time)>.06)throw new Error('Unexpected presented timestamp: '+JSON.stringify(presented));
   seeks.push({state:name,time,...presented});
  }
  await page.evaluate(()=>document.querySelector('video').play());
  await page.waitForFunction(()=>document.querySelector('video').ended);
  fs.writeFileSync(path.join(root,`logs/video-verification-${version}.json`),JSON.stringify({...info,representative_seeks:seeks,playback_to_end:true},null,2));
  console.log('Video decoded in Chrome: 960x540, 3 seconds, all concept states sought, playback to end passed.');
 } finally {await browser.close();await new Promise(resolve=>server.close(resolve));}
})().catch(e=>{console.error(e);process.exitCode=1});

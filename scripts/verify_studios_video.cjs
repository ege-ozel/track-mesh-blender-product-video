// Decode and play the local review MP4 in Chrome; keep screenshots inside this workspace.
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || 'C:/Users/4D/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root = path.resolve(__dirname, '..');
const movie = path.resolve(root, process.argv[2] || '');
const expected = process.argv[3] ? JSON.parse(fs.readFileSync(path.resolve(root, process.argv[3]), 'utf8')) : {frames:720,duration_seconds:30,resolution:[1920,1080]};
if (!movie.startsWith(root + path.sep) || path.extname(movie) !== '.mp4') throw new Error('Expected a workspace MP4');
const stem = path.basename(movie, '.mp4');
const output = path.join(root, 'logs', `${stem}-decoded`);
if (fs.existsSync(output) && fs.readdirSync(output).some(n=>n!=='player.html')) throw new Error(`Preserving existing verification: ${output}`);
fs.mkdirSync(output,{recursive:true});
(async () => {
  const server = http.createServer((req, res) => {
    if (req.url === '/') {
      res.setHeader('Content-Type', 'text/html');
      res.end('<!doctype html><video muted preload="auto" src="/film.mp4"></video>');
    } else if (req.url === '/film.mp4') {
      const length = fs.statSync(movie).size;
      const range = /^bytes=(\d+)-(\d*)$/.exec(req.headers.range || '');
      res.setHeader('Content-Type', 'video/mp4');
      res.setHeader('Accept-Ranges', 'bytes');
      if (range) {
        const start = Number(range[1]), end = range[2] ? Math.min(Number(range[2]), length-1) : length-1;
        res.writeHead(206, {'Content-Range': `bytes ${start}-${end}/${length}`, 'Content-Length': end-start+1});
        fs.createReadStream(movie, {start, end}).pipe(res);
      } else {
        res.setHeader('Content-Length', length);
        fs.createReadStream(movie).pipe(res);
      }
    } else { res.writeHead(404); res.end(); }
  });
  const localFile = expected.tag?.startsWith('studios-v10-final-');
  if(!localFile)await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const browser = await chromium.launch({channel: 'chrome', headless: true});
  try {
    const page = await browser.newPage();
    if(localFile){
      const {pathToFileURL}=require('node:url');
      const player=path.join(output,'player.html');
      fs.writeFileSync(player,`<!doctype html><body style="margin:0;background:#0b121b"><video muted preload="auto" src="${pathToFileURL(movie).href}"></video>`);
      await page.setContent('<!doctype html><body style="margin:0;background:#0b121b"><video muted preload="auto"></video>');
      // Same-origin Blob keeps local decoding/canvas capture independent of
      // loopback networking and file-origin canvas restrictions.
      await page.evaluate(encoded=>{
        const raw=atob(encoded),bytes=new Uint8Array(raw.length);
        for(let i=0;i<raw.length;i++)bytes[i]=raw.charCodeAt(i);
        document.querySelector('video').src=URL.createObjectURL(new Blob([bytes],{type:'video/mp4'}));
      },fs.readFileSync(movie).toString('base64'));
    }else await page.goto(`http://127.0.0.1:${server.address().port}/`);
    await page.waitForFunction(() => {const v=document.querySelector('video'); return v.readyState>=2 && Number.isFinite(v.duration);});
    const info = await page.evaluate(() => {const v=document.querySelector('video'); return {duration:v.duration,width:v.videoWidth,height:v.videoHeight,error:v.error?.message || null};});
    if (Math.abs(info.duration-expected.duration_seconds)>.001 || info.width !== expected.resolution[0] || info.height !== expected.resolution[1] || info.error) throw new Error(JSON.stringify(info));
    const seeks = [];
    const reviewFrames = expected.review_frames || (process.argv[3] ? [...new Set([1,18,25,40,43,60,67,70,94,120,195,198,199,204,205,217,220,228,229,246,247,255,261,expected.frames].filter(f=>f<=expected.frames))].sort((a,b)=>a-b) : [60,135,175,210,300,370,398,400,406,430,530,560,690,716]);
    for (const frame of reviewFrames) {
      const time = (frame-1)/24 + .002;
      const shown = await page.evaluate(t => new Promise((resolve, reject) => {
        const v = document.querySelector('video');
        const timeout = setTimeout(() => reject(new Error(`Frame seek timed out: ${t}`)), 10000);
        const onFrame = (_, metadata) => {
          if (Math.abs(metadata.mediaTime-t) > .045) { v.requestVideoFrameCallback(onFrame); return; }
          clearTimeout(timeout); resolve({mediaTime:metadata.mediaTime});
        };
        v.requestVideoFrameCallback(onFrame);
        v.currentTime = t;
      }), time);
      const pixels = await page.evaluate(() => {
        const v=document.querySelector('video'), canvas=document.createElement('canvas');
        canvas.width=v.videoWidth; canvas.height=v.videoHeight;
        canvas.getContext('2d').drawImage(v,0,0);
        return canvas.toDataURL('image/png').split(',')[1];
      });
      fs.writeFileSync(path.join(output, `frame_${String(frame).padStart(4,'0')}.png`), Buffer.from(pixels,'base64'));
      seeks.push({frame, targetTime:time, ...shown});
    }
    let normalSpeedReview = null;
    if (expected.tag?.startsWith('studios-v10-final-')) {
      normalSpeedReview = await page.evaluate(async cfg => {
        const v=document.querySelector('video');v.style.width=cfg.width+'px';v.playbackRate=1;
        await new Promise(resolve=>{v.addEventListener('seeked',resolve,{once:true});v.currentTime=0;});
        const samples=[];let last=-1;const start=performance.now();
        const finished=new Promise((resolve,reject)=>{
          const timer=setTimeout(()=>reject(Error('Normal-speed playback timed out')),45000);
          v.addEventListener('ended',()=>{clearTimeout(timer);resolve();},{once:true});
        });
        const onFrame=(_,meta)=>{
          if(meta.mediaTime-last>=.48 && meta.mediaTime<cfg.duration){
            const canvas=document.createElement('canvas');canvas.width=cfg.width;canvas.height=Math.round(cfg.width*v.videoHeight/v.videoWidth);
            canvas.getContext('2d').drawImage(v,0,0,canvas.width,canvas.height);
            samples.push({mediaTime:meta.mediaTime,frame:Math.round(meta.mediaTime*24)+1,png:canvas.toDataURL('image/png').split(',')[1]});last=meta.mediaTime;
          }
          if(!v.ended)v.requestVideoFrameCallback(onFrame);
        };
        v.requestVideoFrameCallback(onFrame);await v.play();await finished;
        return {samples,wallSeconds:(performance.now()-start)/1000,playbackRate:v.playbackRate,displayWidth:cfg.width};
      },{width:expected.resolution[0]<expected.resolution[1]?390:960,duration:expected.duration_seconds});
      const folder=path.join(output,'normal-speed');fs.mkdirSync(folder);
      for(const sample of normalSpeedReview.samples){fs.writeFileSync(path.join(folder,`frame_${String(sample.frame).padStart(4,'0')}.png`),Buffer.from(sample.png,'base64'));delete sample.png;}
      if(normalSpeedReview.playbackRate!==1 || normalSpeedReview.wallSeconds<expected.duration_seconds-.5)throw Error('Playback was not at normal speed');
    } else {
      await page.evaluate(async () => {const v=document.querySelector('video'); v.currentTime=0; await v.play();});
    }
    await page.waitForFunction(() => document.querySelector('video').ended, null, {timeout:45000});
    const playback = await page.evaluate(() => {const v=document.querySelector('video'), q=v.getVideoPlaybackQuality(); return {ended:v.ended,error:v.error?.message || null,decodedFrames:q.totalVideoFrames,droppedFrames:q.droppedVideoFrames};});
    if (playback.error || !playback.ended || playback.decodedFrames < expected.frames) throw new Error(JSON.stringify(playback));
    const report = {...info, movie, seeks, playback, normalSpeedReview, publicationApproved:false};
    fs.writeFileSync(path.join(output, 'verification.json'), JSON.stringify(report, null, 2));
    console.log(JSON.stringify(report, null, 2));
  } finally { await browser.close(); if(server.listening)await new Promise(resolve => server.close(resolve)); }
})().catch(error => {console.error(error); process.exitCode=1;});

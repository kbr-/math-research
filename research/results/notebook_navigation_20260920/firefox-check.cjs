const fs=require('node:fs'), http=require('node:http'), os=require('node:os'), path=require('node:path');
const {spawn}=require('node:child_process');
const {ws:WebSocket}=require(path.join(process.cwd(),'node_modules/playwright-core/lib/utilsBundle.js'));
const delay=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
 const book=fs.readFileSync('notebook.html','utf8');
 const templates=[process.env.NOTEBOOK_BEFORE||'/tmp/notebook-navigation-before.html','index.html'];
 const server=http.createServer((req,res)=>{
  res.setHeader('Content-Type',req.url==='/revision'?'application/json':'text/html');
  res.end(req.url==='/revision'?'{"revision":"ff-test"}':fs.readFileSync(templates[req.url.includes('before')?0:1],'utf8').replace('__REVISION__','ff-test').replace('<!-- NOTEBOOK -->',book));
 });
 await new Promise(r=>server.listen(0,'127.0.0.1',r));
 const profile=fs.mkdtempSync(path.join(os.tmpdir(),'notebook-firefox-'));
 const firefox=spawn('firefox',['--headless','--no-remote','--profile',profile,'--remote-debugging-port','0'],{stdio:['ignore','pipe','pipe']});
 let socket;const report=[];
 try{
  const endpoint=await new Promise((resolve,reject)=>{
   const timeout=setTimeout(()=>reject(Error('Firefox startup timeout')),15000);
   const read=data=>{const match=String(data).match(/WebDriver BiDi listening on (ws:\/\/\S+)/);if(match){clearTimeout(timeout);resolve(match[1]+'/session')}};
   firefox.stdout.on('data',read);firefox.stderr.on('data',read);firefox.on('error',reject);
  });
  socket=new WebSocket(endpoint);await new Promise((r,j)=>{socket.once('open',r);socket.once('error',j)});
  let sequence=0;const requests=new Map();
  socket.on('message',data=>{const m=JSON.parse(String(data));if(!requests.has(m.id))return;const {resolve,reject}=requests.get(m.id);requests.delete(m.id);m.type==='error'?reject(Error(JSON.stringify(m))):resolve(m.result)});
  const command=(method,params)=>new Promise((resolve,reject)=>{const id=++sequence;requests.set(id,{resolve,reject});socket.send(JSON.stringify({id,method,params}))});
  const session=await command('session.new',{capabilities:{}});
  console.log('Firefox',session.capabilities.browserVersion);
  const {context}=await command('browsingContext.create',{type:'tab'});
  const evaluate=async expression=>{
   const result=await command('script.evaluate',{expression:`JSON.stringify(${expression})`,target:{context},awaitPromise:true});
   if(result.type==='exception')throw Error(JSON.stringify(result));
   return JSON.parse(result.result.value);
  };
  const click=async name=>{
   const point=await evaluate(`(()=>{const r=document.querySelector('[data-scroll="${name}"]').getBoundingClientRect();return {x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2)}})()`);
   await command('input.performActions',{context,actions:[{type:'pointer',id:'mouse',parameters:{pointerType:'mouse'},actions:[{type:'pointerMove',x:point.x,y:point.y},{type:'pointerDown',button:0},{type:'pointerUp',button:0}]}]});
  };
  for(const version of ['before','after']){
   await command('browsingContext.navigate',{context,url:`http://127.0.0.1:${server.address().port}/?${version}`,wait:'complete'});
   for(let i=0;i<100 && !await evaluate('Boolean(window.mathReady)');i++)await delay(100);
   if(!await evaluate('Boolean(window.mathReady)'))throw Error('MathJax did not load');
   const count=await evaluate("document.querySelectorAll('main h2, main h3').length");
   await click('end');await delay(2200);
   for(let step=1;step<=6;step++){
    await click('previous');await delay(2000);
    report.push({version,step,...await evaluate(`(()=>{const e=document.querySelectorAll('main h2, main h3')[${count-1-step}];return {title:e.textContent,top:e.getBoundingClientRect().top}})()`)});
   }
   for(let n=0;n<3;n++)await click('previous');await delay(2200);
   report.push({version,step:'rapid',...await evaluate(`(()=>{const e=document.querySelectorAll('main h2, main h3')[${count-10}];return {title:e.textContent,top:e.getBoundingClientRect().top}})()`)});
  }
  console.log(JSON.stringify(report,null,2));
  fs.writeFileSync(process.env.NOTEBOOK_REPORT||'/tmp/firefox-navigation.json',JSON.stringify(report,null,2)+'\n');
  if(report.filter(r=>r.version==='after').some(r=>Math.abs(r.top-16)>3))throw Error('Firefox alignment failed');
  await command('session.end',{});
 }finally{socket?.close();firefox.kill('SIGTERM');server.close();await new Promise(r=>{if(firefox.exitCode!==null)r();else firefox.once('exit',r)});fs.rmSync(profile,{recursive:true,force:true});}
})().catch(e=>{console.error(e);process.exitCode=1});

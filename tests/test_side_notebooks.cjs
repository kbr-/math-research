// Headless acceptance for live + static routes and lazy cross-notebook TeX search.
// Uses the already installed Playwright; run through compute.sh. No downloads.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const http = require('node:http');
const path = require('node:path');
const {spawn, execFileSync} = require('node:child_process');
const {chromium} = require('playwright');
const os = require('node:os');
(async () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'side-notebook-browser-'));
  const report = {samples: [], errors: []};
  let browser, live, staticServer;
  try {
    execFileSync('python3', ['-c', `
import sys,shutil,json
from pathlib import Path
root=Path(sys.argv[1]);repo=Path.cwd();sys.path.insert(0,str(repo/'tools'))
from branch import create,SECTIONS
from build_pages import build
for name in ['index.html','notebook.html','server.py','LICENSES/MIT.txt','research/context-budgets.json','tools/notebooks.py','tools/notebook_site.py']:
 p=root/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(repo/name,p)
context={k:'<p>Initial context.</p>' for k in SECTIONS};context['goal']='Independent test thread';context['remaining-route']='<li data-route-item="side-test">Test obligation</li>'
for name in ['alpha','beta']:
 create(name,name.title(),context,root)
 p=root/'research/branches'/name/'notebook.html'
 # Growing records are loaded only on explicit all-notebook search.
 entries=''.join('<article id="'+name+'-'+str(i)+'"><h3>Entry '+str(i)+'</h3><p>\\\\(\\\\operatorname{sideprobe} x^2\\\\) '+name+' unique-target</p></article>' for i in range(1000))
 s=p.read_text();n=s.rfind('</section>');p.write_text(s[:n]+entries+s[n:])
build(root/'site',root)
`, root]);
    staticServer = http.createServer((req,res) => {
      let file = decodeURIComponent(req.url.split('?')[0]).replace(/^\/math-research\//,'');
      if(!file || file.endsWith('/'))file+='index.html';
      const dest=path.resolve(root,'site',file);
      if(!dest.startsWith(path.resolve(root,'site')+path.sep)) {res.writeHead(404);res.end();return;}
      try {res.setHeader('Content-Type',file.endsWith('.json')?'application/json':'text/html');res.end(fs.readFileSync(dest));}
      catch {res.writeHead(404);res.end();}
    });
    await new Promise(r=>staticServer.listen(0,'127.0.0.1',r));
    const reserve=http.createServer();await new Promise(r=>reserve.listen(0,'127.0.0.1',r));const port=reserve.address().port;await new Promise(r=>reserve.close(r));
    live=spawn('python3',[path.join(root,'server.py'),'--port',String(port)],{stdio:['ignore','pipe','pipe']});
    await new Promise((resolve,reject)=>{live.stdout.once('data',resolve);live.once('exit',()=>reject(new Error('Live server failed')));});
    browser=await chromium.launch({headless:true});
    report.browser=browser.version();
    for(const [mode,base] of [['static',`http://127.0.0.1:${staticServer.address().port}/math-research/`],['live',`http://127.0.0.1:${port}/math-research/`]]) {
      const page=await browser.newPage();const requests=[];
      page.on('request',r=>requests.push(r.url()));page.on('pageerror',e=>report.errors.push(e.message));
      await page.goto(base,{waitUntil:'domcontentloaded'});
      await page.waitForTimeout(500);
      assert.equal(requests.filter(u=>/notebooks\.json|notebook-source/.test(u)).length,0,'No other notebooks fetched on startup');
      assert.equal(await page.locator('#search-scope').inputValue(),'current');
      const startup=await page.evaluate(()=>({domReadyMs:performance.getEntriesByType('navigation')[0].domContentLoadedEventEnd,math:window.MathJax?.startup?.document?.math ? [...MathJax.startup.document.math].length : null}));
      await page.locator('#search-open').click();
      const currentStart=Date.now();await page.locator('#search-query').fill('sideprobe');
      await page.waitForFunction(()=>document.getElementById('search-status').dataset.state==='ready');
      assert.match(await page.locator('#search-status').textContent(),/No matching/);
      const currentSearchMs=Date.now()-currentStart;
      assert.equal(requests.filter(u=>/notebooks\.json|notebook-source/.test(u)).length,0);
      const allStart=Date.now();await page.locator('#search-scope').selectOption('all');
      await page.waitForFunction(()=>document.getElementById('search-status').dataset.state==='ready',{},{timeout:30000});
      assert.match(await page.locator('#search-status').textContent(),/2000 matching/);
      const allSearchMs=Date.now()-allStart;
      await page.locator('#search-results button').first().click();
      await page.waitForURL('**/branches/alpha/#alpha-0');
      assert.match(await page.locator('.thread-navigation').textContent(),/Alpha/);
      await page.goBack();assert.equal(new URL(page.url()).pathname,new URL(base).pathname);
      await page.goto(base+'branches/alpha/');
      if(mode==='live') {
        const revision=await page.request.get(base+'branches/alpha/revision');assert.equal(revision.status(),200);
        const f=path.join(root,'research/branches/alpha/notebook.html');fs.appendFileSync(f,'\n<!-- live-change -->');
        await page.waitForTimeout(1500);assert.ok((await page.content()).includes('live-change'),'Side page refreshes its source');
      }
      await page.setViewportSize({width:390,height:844});
      assert.ok(await page.locator('#search-open').isVisible());
      report.samples.push({mode,...startup,currentSearchMs,allSearchMs,otherSourceRequests:requests.filter(u=>/notebook-source/.test(u)).length});
      await page.close();
    }
    assert.deepEqual(report.errors,[]);
    const out=process.env.SIDE_NOTEBOOK_REPORT;
    if(out){fs.mkdirSync(path.dirname(out),{recursive:true});fs.writeFileSync(out,JSON.stringify(report,null,2)+'\n');}
    console.log(JSON.stringify(report,null,2));
  } finally {if(browser)await browser.close();if(live)live.kill();if(staticServer)await new Promise(r=>staticServer.close(r));fs.rmSync(root,{recursive:true,force:true});}
})().catch(e=>{console.error(e);process.exitCode=1;});

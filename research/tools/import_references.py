#!/usr/bin/env python3
"""Acquire the four cited mathematical papers from public locations.
No authentication, access-control bypass, code execution, or automatic installs.
Acquisition status is not a mathematical verification of the reference.
"""
from __future__ import annotations
import argparse, concurrent.futures, hashlib, json, os, re, shutil, subprocess, sys, time
import urllib.error, urllib.parse, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MAX_BYTES=40*1024*1024

def sha(p:Path)->str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def extract_text(pdf:Path, dest:Path, timeout:float)->dict:
    t=time.perf_counter();dest.parent.mkdir(parents=True,exist_ok=True)
    try:
        if shutil.which('pdftotext'):
            r=subprocess.run(['pdftotext','-layout',str(pdf),str(dest)],capture_output=True,text=True,timeout=timeout)
            if r.returncode:raise RuntimeError(r.stderr.strip() or 'pdftotext failed')
            engine='pdftotext -layout'
        else:
            try:from pypdf import PdfReader
            except ImportError:return {'status':'extractor-unavailable','note':'Install/use pdftotext or pypdf if desired; PDF acquisition can still succeed.','elapsed_s':time.perf_counter()-t}
            reader=PdfReader(str(pdf));dest.write_text('\n\n'.join(f'[PDF page {i+1}]\n'+(p.extract_text() or '') for i,p in enumerate(reader.pages)),encoding='utf-8');engine='pypdf'
        text=dest.read_text(encoding='utf-8',errors='replace')
        detected=re.findall(r'arXiv:\s*([0-9.]+v\d+)',text[:12000])
        return {'status':'extracted','path':str(dest.relative_to(ROOT)),'engine':engine,'characters':len(text),'detected_arxiv_versions':sorted(set(detected)),'sha256':sha(dest),'elapsed_s':time.perf_counter()-t,'note':'Text is a search aid; inspect equations in original/math HTML when formatting is ambiguous.'}
    except Exception as e:return {'status':'extraction-failed','error':str(e),'elapsed_s':time.perf_counter()-t}

def acquire(ref:dict, fetch:bool, extract:bool, timeout:float)->dict:
    t=time.perf_counter();rid=ref['id'];pdf=ROOT/'references/cache'/f'{rid}.pdf';pdf.parent.mkdir(parents=True,exist_ok=True)
    result={'id':rid,'status':'not-downloaded','record_url':ref['record_url'],'requested_version':ref.get('version'),'mathematical_audit':'not-performed-by-importer','attempts':[]}
    if pdf.exists():
        if pdf.read_bytes()[:5]!=b'%PDF-':
            result.update(status='invalid-existing-file',error='Refusing to overwrite a non-PDF cache file.');return result
        result.update(status='cached',path=str(pdf.relative_to(ROOT)),sha256=sha(pdf),bytes=pdf.stat().st_size)
    elif fetch:
        for url in ref['pdf_candidates']:
            start=time.perf_counter();a={'url':url}
            tmp=pdf.with_suffix('.part')
            try:
                if urllib.parse.urlparse(url).scheme!='https':raise ValueError('Only HTTPS source URLs are accepted')
                request=urllib.request.Request(url,headers={'User-Agent':'ResearchReferenceImporter/1.0 (personal scholarly reference acquisition)'})
                with urllib.request.urlopen(request,timeout=timeout) as response:
                    if urllib.parse.urlparse(response.url).scheme!='https':raise ValueError('Refusing an insecure redirect')
                    a.update(final_url=response.url,http_status=response.status,content_type=response.headers.get('Content-Type',''))
                    count=0;first=True
                    with tmp.open('wb') as f:
                        while True:
                            chunk=response.read(65536)
                            if not chunk:break
                            if first and not chunk.startswith(b'%PDF-'):raise ValueError('Response is not a PDF (possibly a landing/login/error page)')
                            first=False;count+=len(chunk)
                            if count>MAX_BYTES:raise ValueError('Reference exceeds download size cap')
                            f.write(chunk)
                    if first:raise ValueError('Empty response')
                tmp.replace(pdf);a['status']='downloaded'
                result.update(status='downloaded',path=str(pdf.relative_to(ROOT)),source_url=url,final_url=a['final_url'],sha256=sha(pdf),bytes=count)
            except Exception as e:
                if tmp.exists():tmp.unlink()
                a.update(status='failed',error=str(e))
            a['elapsed_s']=time.perf_counter()-start;result['attempts'].append(a)
            if result['status']=='downloaded':break
        if result['status']!='downloaded':result['status']='download-failed'
    if extract and result['status'] in ('cached','downloaded'):
        result['extraction']=extract_text(pdf,ROOT/'references/extracted'/f'{rid}.txt',timeout)
    result['elapsed_s']=time.perf_counter()-t
    return result

def main()->None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--list',action='store_true');ap.add_argument('--fetch',action='store_true');ap.add_argument('--extract',action='store_true')
    ap.add_argument('--reference',action='append',help='One or more citation keys; default is all four')
    ap.add_argument('--workers',type=int,default=2);ap.add_argument('--timeout',type=float,default=25)
    args=ap.parse_args();refs=json.loads((ROOT/'references/manifest.json').read_text())['references']
    if args.reference:
        wanted=set(args.reference);known={r['id'] for r in refs}
        if wanted-known:ap.error('Unknown references: '+', '.join(sorted(wanted-known)))
        refs=[r for r in refs if r['id'] in wanted]
    if args.list or not (args.fetch or args.extract):
        for r in refs:print(f"{r['id']}: {r['title']}\n  {r['record_url']}\n  Read: {'; '.join(r['reading_targets'])}")
        return
    if args.workers<1 or args.workers>4:ap.error('Use 1--4 workers; avoid hammering scholarly servers')
    if args.timeout<=0:ap.error('Timeout must be positive')
    t=time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        results=list(pool.map(lambda ref:acquire(ref,args.fetch,args.extract,args.timeout),refs))
    status_path=ROOT/'references/import_status.json'
    try:old=json.loads(status_path.read_text())
    except (FileNotFoundError,json.JSONDecodeError):old={}
    entries=old.get('references',{})
    entries.update({r['id']:r for r in results})
    report={'stage':'local-import','utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'batch_elapsed_s':time.perf_counter()-t,'max_workers':args.workers,'references':entries,'note':'Elapsed includes network/DNS/server and local processing; acquisition is not a theorem audit.'}
    status_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    for r in results:print(r['id'],r['status'],f"{r['elapsed_s']:.3f}s",r.get('extraction',{}).get('status',''))
    print('Recorded references/import_status.json. Missing sources are not silently counted as imported.')
    if any(r['status'] not in ('cached','downloaded') for r in results):sys.exit(1)
if __name__=='__main__':main()

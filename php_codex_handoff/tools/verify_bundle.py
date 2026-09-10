#!/usr/bin/env python3
"""Check the exported snapshot's hashes and original archive contents.
This is file-integrity verification, not verification of mathematical claims.
"""
from __future__ import annotations
import argparse,hashlib,json,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def sha(p:Path)->str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def main()->None:
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--include-mutable',action='store_true',help='Also compare initial note/log/import-status files, which are expected to change during work')
    args=ap.parse_args();mf=ROOT/'provenance/handoff_manifest.json'
    if not mf.exists():raise SystemExit('No handoff manifest. It is created when the export is finalized.')
    manifest=json.loads(mf.read_text());checked=0;skipped=0;errors=[]
    for rec in manifest['files']:
        if rec.get('mutable_by_design') and not args.include_mutable:skipped+=1;continue
        p=ROOT/rec['path']
        if not p.resolve().is_relative_to(ROOT.resolve()):errors.append('Invalid manifest path: '+rec['path']);continue
        if not p.is_file():errors.append('Missing: '+rec['path']);continue
        if p.stat().st_size!=rec['bytes'] or sha(p)!=rec['sha256']:errors.append('Changed: '+rec['path'])
        checked+=1
    archives=0
    for z in (ROOT/'checks/original_archives').glob('*.zip'):
        with zipfile.ZipFile(z) as f:
            bad=f.testzip()
            if bad:errors.append(z.name+': corrupt member '+bad)
        archives+=1
    report={'checked_files':checked,'skipped_mutable_files':skipped,'original_check_archives':archives,'errors':errors,'scope':'Bytes and ZIP integrity only; no research suites executed or mathematical claims verified.'}
    print(json.dumps(report,indent=2));sys.exit(1 if errors else 0)
if __name__=='__main__':main()

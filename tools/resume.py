#!/usr/bin/env python3
"""Prepare complete resume context once; deliver it in bounded cached parts."""
import argparse
import hashlib
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import uuid

from notebook_context import excerpt
from recovery_evidence import Store, observe

ROOT=Path(__file__).resolve().parents[1]
FILES=('research/notes/RESUME.md','AGENTS.md','research/AGENTS.md','COMPUTATION_RULES.md')
PART_BYTES=20000


def save_bundle(root, parts):
    text='RESUME BUNDLE — continue through all parts; do not prepare it again.\n'
    for label,body,_,_ in parts:
        text+=f'\n--- {label} ---\n{body.rstrip()}\n'
    text+='\nEND RESUME BUNDLE — load further sources only as the restored task requires.\n'
    raw=text.encode('utf-8');key=uuid.uuid4().hex
    directory=root/'research/logs/resume-bundles'/key
    directory.mkdir(parents=True)
    (directory/'bundle.txt').write_bytes(raw)
    chunks=[];start=0
    while start<len(raw):
        end=min(start+PART_BYTES,len(raw))
        if end<len(raw):
            newline=raw.rfind(b'\n',max(start,end-2048),end)
            if newline>=max(start,end-2048):end=newline+1
        while end<len(raw) and raw[end]&0xc0==0x80:end-=1
        body=raw[start:end]
        chunks.append({'offset':start,'bytes':len(body),'sha256':hashlib.sha256(body).hexdigest()})
        start=end
    manifest={'version':1,'bundle':key,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'parts':chunks}
    (directory/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


def read_part(root, key, number):
    if len(key)!=32 or any(c not in '0123456789abcdef' for c in key):
        raise ValueError('Use the bundle ID returned by resume preparation')
    directory=root/'research/logs/resume-bundles'/key
    manifest=json.loads((directory/'manifest.json').read_text())
    if manifest.get('version')!=1 or manifest.get('bundle')!=key:
        raise ValueError('Invalid resume manifest')
    if not 1<=number<=len(manifest['parts']):raise ValueError('Part number out of range')
    row=manifest['parts'][number-1]
    if not 0<row['bytes']<=PART_BYTES or (directory/'bundle.txt').stat().st_size!=manifest['bytes']:
        raise ValueError('Invalid or incomplete resume cache')
    with (directory/'bundle.txt').open('rb') as source:
        source.seek(row['offset']);raw=source.read(row['bytes'])
    if hashlib.sha256(raw).hexdigest()!=row['sha256']:raise ValueError('Resume part changed; refusing inconsistent context')
    return raw.decode('utf-8'),len(manifest['parts'])


def emit_part(root, key, number):
    body,total=read_part(root,key,number)
    print(f'RESUME PART {number}/{total} — {len(body.encode())} payload bytes')
    sys.stdout.write(body)
    print(f'\nEND RESUME PART {number}/{total}')
    if number<total:
        print(f'NEXT: python3 tools/resume.py --read {key} --part {number+1}')
    observe('read',root=root,tool='resume-part',selector={'part':number,'format':2},text=body)


def active_turn(root):
    store=None
    try:
        store=Store(root);turn=store.state()['turn']
        if not turn:return None
        events=[json.loads(line) for line in (root/'research/logs'/f'{turn}.jsonl').read_text().splitlines()]
        if any(e['event']=='stop' for e in events):return None
        boot=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
        first=next(e for e in events if e['event']=='start')
        return turn if first.get('boot_id')==boot else None
    except (OSError,ValueError,StopIteration,sqlite3.Error):
        return None
    finally:
        if store:store.db.close()


def bundle(root, formalization=False, tail=10):
    files=FILES+(('formalization/AGENTS.md','formalization/README.md') if formalization else ())
    parts=[(path,(root/path).read_text(), 'resume-file',path) for path in files]
    source=(root/'notebook.html').read_text();book=excerpt.Notebook(source)
    current=source[:book.anchor('research-record')['start']].rstrip()+'\n'
    parts.append(('notebook.html — living sections',current,'notebook-excerpt',
                  {'anchor':None,'until':None,'current':True,'toc':False,'tail':None,'since':'None'}))
    toc,omitted=book.toc(tail=tail)
    parts.append((f'Research-record contents — latest {tail}; {omitted} earlier entries omitted',toc,
                  'notebook-excerpt',{'anchor':None,'until':None,'current':False,'toc':True,'tail':tail,'since':'None'}))
    return parts


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--session',help='Active timing session; otherwise use this stream’s last active session')
    parser.add_argument('--formalization',action='store_true',help='Include assigned formalization instructions')
    parser.add_argument('--tail',type=int,default=10)
    parser.add_argument('--read',metavar='BUNDLE_ID',help='Read a saved bundle without recording another resume')
    parser.add_argument('--part',type=int,help='One bounded part of --read BUNDLE_ID')
    args=parser.parse_args()
    if args.read:
        if args.part is None or args.session or args.formalization or args.tail!=10:
            parser.error('--read requires --part and cannot be combined with preparation options')
    elif args.part is not None:parser.error('--part requires --read')
    try:
        if args.read:
            emit_part(ROOT,args.read,args.part)
            return
        parts=bundle(ROOT,args.formalization,args.tail)  # Missing context must not become a partial bundle.
        turn=args.session or active_turn(ROOT)
        if turn:
            # Existing CLI validates session name, active state and boot. No new
            # research clock is started, and resource enforcement is untouched.
            subprocess.run([str(ROOT/'compute.sh'),'phase',turn,'restoration',
                            '--note','Explicit resume bundle'],cwd=ROOT,check=True,capture_output=True,text=True)
        manifest=save_bundle(ROOT,parts)
        observe('resume',root=ROOT,turn=turn)
        print(json.dumps({'bundle':manifest['bundle'],'path':f"research/logs/resume-bundles/{manifest['bundle']}/bundle.txt",
            'bytes':manifest['bytes'],'parts':len(manifest['parts']),'part_bytes_at_most':PART_BYTES}))
        emit_part(ROOT,manifest['bundle'],1)
    except subprocess.CalledProcessError as error:
        parser.exit(2,'resume: '+(error.stderr or str(error)).strip()+'\n')
    except (OSError,ValueError) as error:
        parser.exit(2,f'resume: {error}\n')


if __name__=='__main__':main()

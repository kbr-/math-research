#!/usr/bin/env python3
"""Emit the required research context once and explicitly record restoration."""
import argparse
import json
from pathlib import Path
import sqlite3
import subprocess
import sys

from notebook_context import excerpt
from recovery_evidence import Store, observe

ROOT=Path(__file__).resolve().parents[1]
FILES=('research/notes/RESUME.md','AGENTS.md','research/AGENTS.md','COMPUTATION_RULES.md')


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
    args=parser.parse_args()
    try:
        parts=bundle(ROOT,args.formalization,args.tail)  # Missing context must not become a partial bundle.
        turn=args.session or active_turn(ROOT)
        if turn:
            # Existing CLI validates session name, active state and boot. No new
            # research clock is started, and resource enforcement is untouched.
            subprocess.run([str(ROOT/'compute.sh'),'phase',turn,'restoration',
                            '--note','Explicit resume bundle'],cwd=ROOT,check=True,capture_output=True,text=True)
        observe('resume',root=ROOT,turn=turn)
        print('RESUME BUNDLE — read once; do not re-run this command from the included guide.')
        for label,text,tool,selector in parts:
            print(f'\n--- {label} ---\n{text.rstrip()}')
            observe('read',root=ROOT,tool=tool,selector=selector,text=text)
        print('\nEND RESUME BUNDLE — load further sources only as the restored task requires.')
    except subprocess.CalledProcessError as error:
        parser.exit(2,'resume: '+(error.stderr or str(error)).strip()+'\n')
    except (OSError,ValueError) as error:
        parser.exit(2,f'resume: {error}\n')


if __name__=='__main__':main()

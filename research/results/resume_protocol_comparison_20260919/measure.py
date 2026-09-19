#!/usr/bin/env python3
"""Execute pinned old/new resume read plans in temporary checkouts; save metrics only."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import statistics
import subprocess
import sys
import tempfile
import time

ROOT=Path(__file__).resolve().parents[3]
OLD='23cedfe6168c18ec848b532b7d6f5dd9f4669b95'
NEW='5388deceb889410ffb2c0526f4cc683d66c07dad'
DOCS=['research/notes/RESUME.md','AGENTS.md','research/AGENTS.md','COMPUTATION_RULES.md']

def git_file(revision,path):
    return subprocess.check_output(['git','show',revision+':'+path],cwd=ROOT)

def materialize(root,revision,tools_revision=None,new=False):
    paths=DOCS+['notebook.html','tools/notebook-excerpt.py']
    if new:paths+=['tools/resume.py','tools/notebook_context.py','tools/recovery_evidence.py','compute.sh']
    for name in paths:
        path=root/name;path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(git_file(tools_revision if name.startswith('tools/') and tools_revision else revision,name))

def stats(data):
    return {'bytes':len(data),'characters':len(data.decode()),
            'whitespace_words':len(data.decode().split()),'sha256':hashlib.sha256(data).hexdigest()}

def run(root,args,env):
    start=time.perf_counter()
    p=subprocess.run(args,cwd=root,env=env,capture_output=True,check=True)
    return {'command':args,'elapsed_s':time.perf_counter()-start,
            'stdout':stats(p.stdout),'stderr':stats(p.stderr)},p.stdout

def old_plan(root,env,batched):
    if batched:
        commands=[['cat',DOCS[0]],['cat',*DOCS[1:]],
                  ['bash','-c','python3 tools/notebook-excerpt.py --current && python3 tools/notebook-excerpt.py --toc']]
    else:
        commands=[['cat',p] for p in DOCS]+[['python3','tools/notebook-excerpt.py',mode] for mode in ('--current','--toc')]
    rows=[];outputs=[]
    for command in commands:
        row,output=run(root,command,env);rows.append(row);outputs.append(output)
    return rows,outputs

def new_plan(root,env):
    row,output=run(root,['python3','tools/resume.py'],env)
    info=json.loads(output.splitlines()[0]);rows=[row];outputs=[output]
    for part in range(2,info['parts']+1):
        row,output=run(root,['python3','tools/resume.py','--read',info['bundle'],'--part',str(part)],env)
        row['command'][3]='BUNDLE_ID'  # Runtime cache IDs are not reproducibility inputs.
        rows.append(row);outputs.append(output)
    # Reassemble the actual emitted payload, not merely the saved file.
    pieces=[]
    for i,output in enumerate(outputs,1):
        if i==1:output=output.split(b'\n',1)[1]
        body=output.split(b'\n',1)[1].rsplit(b'\nEND RESUME PART ',1)[0]
        assert len(body)<=16000
        pieces.append(body)
    assert b''.join(pieces)==(root/info['path']).read_bytes()
    return rows,outputs

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--rounds',type=int,default=7)
    args=parser.parse_args()
    if not 1<=args.rounds<=20:parser.error('Use 1–20 bounded repetitions')
    env=dict(os.environ,MATH_RECOVERY_STREAM='isolated-benchmark-stream',MATH_RECOVERY_DISABLED='0')
    runs={name:[] for name in ('old_separate','old_batched','old_batched_current_content','new_cached')}
    with tempfile.TemporaryDirectory(prefix='resume-comparison-') as temp:
        roots={k:Path(temp)/k for k in ('old','control','new')}
        materialize(roots['old'],OLD)
        materialize(roots['control'],NEW,tools_revision=OLD)
        materialize(roots['new'],NEW,new=True)
        rng=random.Random(1947)
        references={}
        for iteration in range(args.rounds):
            order=list(runs);rng.shuffle(order)
            for name in order:
                if name=='new_cached':rows,outputs=new_plan(roots['new'],env)
                else:
                    root=roots['control'] if name=='old_batched_current_content' else roots['old']
                    rows,outputs=old_plan(root,env,name!='old_separate')
                if name in ('old_separate','old_batched'):
                    value=hashlib.sha256(b''.join(outputs)).hexdigest()
                    references[name]=value
                    if len(references)==2:assert len(set(references.values()))==1,'Old batching changed content'
                runs[name].append({'round':iteration+1,'calls':rows,'call_count':len(rows),
                                  'command_elapsed_s':sum(r['elapsed_s'] for r in rows),
                                  'output_bytes':sum(r['stdout']['bytes']+r['stderr']['bytes'] for r in rows),
                                  'largest_stdout_bytes':max(r['stdout']['bytes'] for r in rows)})
    summary={}
    for name,rows in runs.items():
        times=[r['command_elapsed_s'] for r in rows]
        summary[name]={'shell_tool_calls':rows[0]['call_count'],
                       'output_bytes':rows[0]['output_bytes'],
                       'largest_stdout_bytes':rows[0]['largest_stdout_bytes'],
                       'median_command_seconds':round(statistics.median(times),4),
                       'min_command_seconds':round(min(times),4),'max_command_seconds':round(max(times),4)}
    report={'old_revision':OLD,'new_revision':NEW,'rounds':args.rounds,'order_seed':1947,
            'python':sys.version.split()[0],'summary':summary,'runs':runs,
            'same_old_content_verified':True,'new_complete_reassembly_verified':True,
            'scope':'Cold full-context plan, assuming no required file already loaded; OS caches are not flushed. '
                    'Actual commands run in temporary pinned checkouts. Call counts are calls under explicit grouping plans, '
                    'not an observed distribution of agent behavior. Timings measure subprocess execution, not model reasoning, '
                    'API round trips, approval latency, or end-to-end recovery. No model tokens measured. '
                    'Current-content control separates changed documents from delivery overhead. '
                    'Real tool-response truncation is not simulated by subprocess capture. Synthetic telemetry stays in temporary checkouts.'}
    with args.out.open('x') as output:json.dump(report,output,indent=2);output.write('\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()

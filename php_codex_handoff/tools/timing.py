#!/usr/bin/env python3
"""Observable wall-clock accounting with explicit reading phases and timed commands.
Pure cognition and pure network latency are not measured. Overlapping windows
are counted once in the exclusive breakdown, not added as worker durations.
"""
from __future__ import annotations
import argparse,json,os,re,signal,subprocess,sys,time,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PHASES=('reading','reasoning_writing','preparation','external_tool','network_tool','other')
RUNS=('computation','network_tool','external_tool','local_processing')

def path(name:str)->Path:
    if not re.fullmatch(r'[A-Za-z0-9_.-]+',name):raise ValueError('Use a simple session name: letters, digits, _, -, .')
    p=ROOT/'logs'/(name+'.jsonl');p.parent.mkdir(parents=True,exist_ok=True);return p

def add(p:Path,event:str,**kwargs)->dict:
    rec={'event':event,'monotonic_s':time.monotonic(),'unix_s':time.time(),**kwargs}
    with p.open('a',encoding='utf-8') as f:f.write(json.dumps(rec,ensure_ascii=False)+'\n')
    return rec

def read(p:Path)->list[dict]:return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]

def summary(events:list[dict],end:float)->dict:
    begin=next(e['monotonic_s'] for e in events if e['event']=='start')
    phases=[(begin,'preparation')]+[(e['monotonic_s'],e['category']) for e in events if e['event']=='phase']
    phases=sorted((max(begin,min(end,t)),c) for t,c in phases)
    segments=[]
    for i,(a,c) in enumerate(phases):
        b=phases[i+1][0] if i+1<len(phases) else end
        if b>a:segments.append((a,b,c,False))
    runs={};failures=[]
    for e in events:
        if e['event']=='run_start':runs[e['id']]=e
        elif e['event']=='run_end' and e['id'] in runs:
            a=runs[e['id']]
            segments.append((a['monotonic_s'],min(e['monotonic_s'],end),a['category'],True))
            if e.get('returncode')!=0:failures.append(e)
    finished={e['id'] for e in events if e['event']=='run_end'}
    for rid,a in runs.items():
        if rid not in finished:segments.append((a['monotonic_s'],end,a['category'],True))
    cuts=sorted({begin,end}|{max(begin,min(end,x)) for a,b,_,_ in segments for x in (a,b)})
    totals={}
    for a,b in zip(cuts,cuts[1:]):
        if b<=a:continue
        mid=(a+b)/2;active=[s for s in segments if s[0]<=mid<s[1]]
        timed=[s for s in active if s[3]]
        if timed:
            cats={s[2] for s in timed};cat=next(iter(cats)) if len(cats)==1 else 'overlapping_tool_categories'
        else:cat=active[-1][2] if active else 'unclassified'
        totals[cat]=totals.get(cat,0.0)+(b-a)
    return {'total_instrumented_s':end-begin,'exclusive_categories_s':totals,'command_runs':len(runs),'failed_or_timed_out_commands':len(failures),
      'unfinished_commands':len(set(runs)-finished),
      'scope':'Reading phases include interpretation; reasoning_writing is a designated phase, not an internal cognition timer. Network/tool windows include server and orchestration latency. Final-answer generation after the snapshot is excluded.'}

def main()->None:
    raw=sys.argv[1:];command=[]
    if '--' in raw:i=raw.index('--');command=raw[i+1:];raw=raw[:i]
    ap=argparse.ArgumentParser(description=__doc__);sub=ap.add_subparsers(dest='action',required=True)
    a=sub.add_parser('start');a.add_argument('session')
    a=sub.add_parser('phase');a.add_argument('session');a.add_argument('category',choices=PHASES);a.add_argument('--note',default='')
    a=sub.add_parser('run');a.add_argument('session');a.add_argument('--category',choices=RUNS,default='computation');a.add_argument('--timeout',type=float,default=180)
    a=sub.add_parser('report');a.add_argument('session');a.add_argument('--stop',action='store_true')
    args=ap.parse_args(raw);p=path(args.session)
    if args.action=='start':
        if p.exists():ap.error('Session exists; choose a new session ID')
        add(p,'start');print(p.relative_to(ROOT));return
    if not p.exists():ap.error('Start the session first')
    events=read(p)
    if any(e['event']=='stop' for e in events) and args.action!='report':ap.error('Session already stopped; start a new one')
    if args.action=='phase':add(p,'phase',category=args.category,note=args.note);return
    if args.action=='run':
        if not command:ap.error('Use -- followed by the command to run')
        rid=uuid.uuid4().hex[:10];log=ROOT/'logs'/f'{args.session}-{rid}.output.txt'
        add(p,'run_start',id=rid,category=args.category,command=command,output=str(log.relative_to(ROOT)))
        rc=1;timedout=False
        try:
            with log.open('w',encoding='utf-8') as f:
                proc=subprocess.Popen(command,cwd=Path.cwd(),stdout=f,stderr=subprocess.STDOUT,text=True,start_new_session=(os.name=='posix'))
                try:rc=proc.wait(timeout=args.timeout)
                except subprocess.TimeoutExpired:
                    timedout=True
                    if os.name=='posix':
                        try:os.killpg(proc.pid,signal.SIGKILL)
                        except ProcessLookupError:pass
                    else:
                        try:subprocess.run(['taskkill','/PID',str(proc.pid),'/T','/F'],capture_output=True,timeout=10)
                        except Exception:proc.kill()
                    proc.wait();rc=124
        except Exception as e:
            with log.open('a',encoding='utf-8') as f:f.write('\nRunner exception: '+repr(e)+'\n')
        finally:add(p,'run_end',id=rid,returncode=rc,timed_out=timedout)
        print(log.read_text(encoding='utf-8',errors='replace'),end='');print(f'\nExit {rc}; log: {log.relative_to(ROOT)}');sys.exit(rc)
    if args.action=='report':
        stop=next((e for e in events if e['event']=='stop'),None)
        if args.stop and stop is None:stop=add(p,'stop');events=read(p)
        end=stop['monotonic_s'] if stop else time.monotonic();result=summary(events,end)
        dest=p.with_suffix('.summary.json');dest.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()

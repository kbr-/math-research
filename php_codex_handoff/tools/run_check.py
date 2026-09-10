#!/usr/bin/env python3
"""Run one historical suite in a fresh copy; keep archived scripts/results intact."""
from __future__ import annotations
import argparse, ast, hashlib, json, os, shutil, signal, subprocess, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ENTRY={
'A01':('annihilating_functional_checks','check_generic_functional.py'),
'A02':('ens_lifting_checks','ens_lifting_checks/verify_lifting.py'),
'A03':('factor_packing_lift_checks','factor_packing_lift_checks/checks.py'),
'A04':('shared_conditioning_packing_checks','shared_conditioning_packing/check_packing.py'),
'A05':('base_aware_lifting_checks','base_aware_lifting_checks/check.py'),
'A06':('joint_moment_lifting_checks','joint_moment_lifting/checks.py'),
'A07':('two_block_lifting_checks','checks.py'),
'A08':('batch_lifting_attack_checks','batch_lifting_attack/check_prefix_certificate.py'),
'A09':('nested_batch_elimination_checks','check_chain.py'),
'A10':('core_residual_batch_elimination_checks','check_residual_batch.py'),
'A11':('decomposition_optimization_checks','decomposition_attack/check_decomposition.py'),
}
class WorkerCap(ast.NodeTransformer):
    def __init__(self,n:int):self.n=n;self.count=0
    def visit_Call(self,node):
        self.generic_visit(node)
        if isinstance(node.func,ast.Name) and node.func.id=='ProcessPoolExecutor':
            for kw in node.keywords:
                if kw.arg=='max_workers':kw.value=ast.Constant(self.n);self.count+=1
        return node

def sha(data:bytes)->str:return hashlib.sha256(data).hexdigest()
def terminate(p:subprocess.Popen)->None:
    if os.name=='posix':
        try:os.killpg(p.pid,signal.SIGKILL)
        except ProcessLookupError:pass
    else:
        try:subprocess.run(['taskkill','/PID',str(p.pid),'/T','/F'],capture_output=True,timeout=10)
        except Exception:p.kill()

def main()->None:
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--list',action='store_true');ap.add_argument('--suite',choices=ENTRY)
    ap.add_argument('--workers',type=int,default=min(4,os.cpu_count() or 1));ap.add_argument('--timeout',type=float,default=180)
    ap.add_argument('--script',help='Optional alternate .py entry within selected suite, notably A01')
    ap.add_argument('--prepare-only',action='store_true',help='Create/adapt disposable copy but do not execute it')
    args=ap.parse_args()
    if args.list or not args.suite:
        for k,(d,s) in ENTRY.items():print(k,d,'->',s)
        return
    if not 1<=args.workers<=max(1,os.cpu_count() or 1):ap.error('Worker count must be within available CPUs')
    if args.timeout<=0:ap.error('Timeout must be positive')
    suite,entry=ENTRY[args.suite];entry=args.script or entry
    src=ROOT/'checks/suites'/suite
    if not (src/entry).resolve().is_relative_to(src.resolve()) or not (src/entry).is_file():ap.error('Entry must be an existing file in the chosen suite')
    stamp=time.strftime('%Y%m%dT%H%M%S',time.gmtime())+f'-{time.time_ns()%1000000:06d}'
    work=ROOT/'.runs'/f'{stamp}-{args.suite}';shutil.copytree(src,work)
    adaptations=[]
    for p in work.rglob('*.py'):
        original=p.read_bytes();text=original.decode('utf-8')
        oldpath='/mnt/data/research_work';replaced=oldpath in text
        text=text.replace(oldpath,str(work).replace('\\','/'))
        tree=ast.parse(text);cap=WorkerCap(args.workers);tree=cap.visit(tree);ast.fix_missing_locations(tree)
        # Changes are made only to copies; AST rewriting may alter formatting, never original files.
        if replaced or cap.count:
            p.write_text(ast.unparse(tree)+'\n')
            adaptations.append({'file':str(p.relative_to(work)),'original_sha256':sha(original),'copy_sha256':sha(p.read_bytes()),'absolute_path_remapped':replaced,'worker_pools_capped':cap.count})
    script=work/entry;command=[sys.executable,str(script)]
    env=os.environ.copy()
    for v in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):env[v]='1'
    env['PYTHONHASHSEED']='0'
    report={'suite':args.suite,'entry':entry,'work_directory':str(work.relative_to(ROOT)),'command':command,'workers':args.workers,'adaptations':adaptations,'status':'prepared','note':'A new run; original archived results unchanged. This run is not a proof of general theorem validity.'}
    if not args.prepare_only:
        t=time.perf_counter()
        with (work/'runner_stdout.txt').open('w') as out,(work/'runner_stderr.txt').open('w') as err:
            proc=subprocess.Popen(command,cwd=script.parent,env=env,stdout=out,stderr=err,start_new_session=(os.name=='posix'))
            try:
                rc=proc.wait(timeout=args.timeout);report.update(status='passed-command' if rc==0 else 'failed-command',returncode=rc)
            except subprocess.TimeoutExpired:
                terminate(proc);proc.wait();report.update(status='timed-out',returncode=proc.returncode)
        report['elapsed_s']=time.perf_counter()-t
    else:report['elapsed_s']=0.0
    (work/'runner_report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    if report['status'] not in ('prepared','passed-command'):sys.exit(1)
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Finish the fixed53..97 original complement after the uniform bulk cutoff.

Stages: exact coefficient plan already saved; shared PARI source/reference determinants
(two prime workers, at most four single-thread GP workers); then independent FLINT
products and one FFPACK factorization per point for all requested nested degrees.
No already-filtered matrix is built. Maximum simultaneous GP stack caps total8 GB.
"""
import argparse
import concurrent.futures
import json
import subprocess
from pathlib import Path

parser=argparse.ArgumentParser()
parser.add_argument('--out',type=Path,required=True)
parser.add_argument('--checker',type=Path,required=True)
args=parser.parse_args()
plan=json.loads((args.out/'plan.json').read_text())
assert [p for p,_ in plan]==[53,59,61,67,71,73,79,83,89,97]
expected=sum(len(ds) for _,parts in plan for ds in parts)
assert expected==52 and args.checker.is_file()
print(f'SIZED_PLAN primes=10 original_matrices={expected} maximum_rows=1793 gp_workers_at_most=4 aggregate_gp_stack_cap=8000000000',flush=True)

def reference(item):
    prime,parts=item
    directory=args.out/f'p{prime}'
    assert not directory.exists()
    command=['python3','research/tools/bmd_filtered_original_series_20261009.py',
             '--prime',str(prime),'--filter',str(args.out/f'filter-p{prime}.gp'),'--out',str(directory)]
    print(f'REFERENCE_START p={prime} degrees={parts}',flush=True)
    log=args.out/f'reference-p{prime}.txt'
    with log.open('x') as output:
        result=subprocess.run(command,stdout=output,stderr=subprocess.STDOUT,timeout=150)
    assert result.returncode==0, f'reference p={prime}: inspect {log}'
    summary=json.loads((directory/'summary.json').read_text())
    assert summary['prime']==prime and summary['direct_degrees']==parts
    assert summary['direct_count']==sum(map(len,parts))
    print(f'REFERENCE_COMPLETE p={prime} count={summary["direct_count"]}',flush=True)
    return (directory/'manifest.txt').read_text().splitlines(),summary

with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    results=list(pool.map(reference,plan))
inputs=[line for lines,_ in results for line in lines]
assert len(inputs)==20 and len(set(inputs))==20
manifest=args.out/'independent-manifest.txt'
manifest.write_text('\n'.join(inputs)+'\n')
print('INDEPENDENT_START fields=20 workers=3 nested_factorizations=true',flush=True)
independent=args.out/'independent.txt'
with independent.open('x') as output:
    result=subprocess.run([str(args.checker),str(manifest),str(args.out/'independent'),'7','3'],
                          stdout=output,stderr=subprocess.STDOUT,timeout=150)
text=independent.read_text()
assert result.returncode==0 and f'COMPLETE independently_matched={expected} max_degree=7 FLINT_products_FFPACK_nested_LU=true' in text,text
summary=dict(primes=[p for p,_ in plan],direct_determinants=expected,
             skipped_by_proved_coefficient=110-expected,complete_original_pairs=20,
             independent_matches=expected,fields=[summary for _,summary in results],
             bulk_dependency='cor:four-pair-bulk-normality',
             lower_dependency='thm:cube-eight-all-odd-normality',
             coefficient_dependency='lem:cube-joint-leading-coefficient',
             dimension_ten_parents_require_finite_nine_degrees_and_proved_degree_seven=True)
(args.out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(f'COMPLETE exact_original_determinants={expected} independent_matches={expected} coefficient_skips={110-expected} pairs=20',flush=True)

"""Nonvacuity count for the accumulation test: for a base, compare dim(C_{D+1}(base) cap R_{<=D})
with the semantic dimension at D (from c3_saturation.json).  A positive gap means that containment
of a degree-<=D element in C_{D+1}(base) is not forced by soundness.
Usage: lowgap.py CONFIG D  (base instances of CONFIG at degree D; writes c3_lowgap_CONFIG_D.json)"""
import json, os, sys
import numpy as np
from multiprocessing import Pool
from conservativity import *

def work(job):
    inst = make(*job); v = inst['v']; D = inst['D']
    tA = sum(len(b) for b in inst['base'])
    gens0, k = [], v
    for b in inst['base']:
        gens0 += block_generators(b, list(range(k, k + len(b))), v, v + tA); k += len(b)
    sp = Space(v, tA, D + 1); P, W, piv = closure(sp, gens0)
    return dict(name=inst['name'], D=D, low_dim_next=int((sp.deg[piv] <= D).sum()))

if __name__ == '__main__':
    cfg, D = sys.argv[1], int(sys.argv[2])
    sat = {(r['name'], r['D']): r for r in json.load(open(os.path.join(HERE, 'c3_saturation.json')))}
    jobs = [j for j in CONFIGS[cfg] if j[2] == D and j[6] == 'random']
    with Pool(min(8, len(jobs))) as pool: res = pool.map(work, jobs)
    for r in res:
        s = sat[(r['name'], D)]
        r.update(dim_base=s['dim_base'], semantic=s['semantic'], gap_next=s['semantic'] - r['low_dim_next'])
        print(r)
    json.dump(res, open(os.path.join(HERE, f'c3_lowgap_{cfg}_D{D}.json'), 'w'), indent=1)

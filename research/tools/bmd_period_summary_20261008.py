"""Independently verify the complete two-curve coefficient cover and its exact cyclic failure sets."""
import csv
import hashlib
import json
import math
import time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/results/bmd-exception-period-cover-20261008'
start=time.monotonic()
periods=(28080,74880)
dimensions=(140,47,10,1)
arrays=[]
evidence={}
for ci,L in enumerate(periods):
    path=OUT/f'full/curve-{ci}-ranks.csv'
    rows=list(csv.DictReader(path.open()))
    assert len(rows)==L
    assert [int(r['exponent_residue']) for r in rows]==list(range(L))
    data=[[int(r[f'b{b}']) for b in range(4)] for r in rows]
    assert all(-1<=row[b]<=dimensions[b] for row in data for b in range(4))
    arrays.append(data)
    evidence[str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
common=math.lcm(*periods)
assert common==224640
reported={(int(r['b']),int(r['exponent_residue']),int(r['nonordinary_rank']),int(r['ordinary_rank']))
          for r in csv.DictReader((OUT/'full/uncovered.csv').open())}
actual=set()
summary=[]
for b,h in enumerate(dimensions):
    mask=bytearray(common)
    for s in range(common):
        r0=arrays[0][s%periods[0]][b]
        r1=arrays[1][s%periods[1]][b]
        if r0!=h and r1!=h:
            assert r0>=0 and r1>=0
            mask[s]=1
            actual.add((b,s,r0,r1))
    bits=bytes(mask)
    minimal=(bits+bits).find(bits,1)
    assert minimal>0 and common%minimal==0
    residues=[i for i in range(minimal) if mask[i]]
    assert all(bool(mask[s])==(s%minimal in residues) for s in range(common))
    item={'b':b,'centres':([3] if b==0 else [3-b,3+b]),'kernel_dimension':h,
          'common_period_failures':sum(mask),'failure_period':minimal,'failure_residues':residues}
    summary.append(item)
assert actual==reported
assert (0,4,79,81) in actual
result={'scope':'Complete fixed-mark coefficient-certificate cover, not the original exception set',
        'coefficient_periods':periods,'common_period':common,'minimum_exponent_for_normality':20,
        'cases':summary,'matrices_evaluated':sum(v>=0 for data in arrays for row in data for v in row),
        'rank_files_sha256':evidence,'structural_81_jet_control':{'residue':4,'ranks':[79,81]}}
(OUT/'cover-summary.json').write_text(json.dumps(result,indent=2)+'\n')
for item in summary:
    print(json.dumps(item,sort_keys=True))
print(f"PERIOD_SUMMARY_COMPLETED matrices={result['matrices_evaluated']} wall_seconds={time.monotonic()-start:.6f}")

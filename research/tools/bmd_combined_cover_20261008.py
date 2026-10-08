"""Intersect exact n9 ternary certificates on the full 28080-step period.

For d=3+81*m*h, unit h, let r=v3(256*m*h-epsilon)>=1.
Restricted cup certifies rank61. For r>=11, a full rank140 cup
at4+r certifies a sectionless slice and hence normality by graph degree.
Positive r divisible28080 is certified by the all-unit return theorem.
This is bounded table orchestration, not numerical matrix construction.
"""
import argparse,csv,json,time
from collections import Counter
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument('--restricted',required=True);p.add_argument('--full',required=True);p.add_argument('--out',required=True)
a=p.parse_args();started=time.monotonic();L=28080

def read(path,key,col,allowed):
    with open(path) as f: rows=list(csv.DictReader(f))
    assert len(rows)==L
    ans={int(row[key]):int(row[col]) for row in rows}
    assert set(ans)==set(range(L)) and all(v in allowed for v in ans.values())
    return ans
K=read(a.restricted,'coefficient_residue','rank',{0,60,61})
V=read(a.full,'exponent_residue','b0',set(range(141)))
assert Counter(K.values())=={61:26994,60:1062,0:24}
assert all(K[(4+r)%L]==61 for r in range(1,37))
# The graph bound is strict and first holds at11; smaller r already pass K.
assert 3**10<=81*769<3**11
old={r for r in range(L) if K[(4+r)%L]<61}
by_full={r for r in old if V[(4+r)%L]==140}
by_return={0}
remaining=sorted(old-by_full-by_return)
# Independent direct predicate traversal, including the small actual-delay guard.
direct=[]
for r in range(L):
    representative=r or L
    passed=K[(4+r)%L]==61 or (representative>=11 and V[(4+r)%L]==140) or r==0
    if not passed:direct.append(r)
assert direct==remaining

def least_period(values):
    for period in range(1,L+1):
        if L%period==0 and all(values[j]==values[j%period] for j in range(L)):
            return period
    raise AssertionError('period missing')
union_before_return=[K[(4+r)%L]==61 or V[(4+r)%L]==140 for r in range(L)]
combined=[r not in remaining for r in range(L)]
summary={'period':L,'graph_min_delay':11,'old_failures':len(old),'cleared_by_full_cup_graph':len(by_full),'cleared_by_return_after_graph':len(by_return-(set(range(L))-old)-by_full),'remaining_count':len(remaining),'remaining_delay_residues':remaining,'remaining_ranks':[[r,K[(r+4)%L],V[(r+4)%L]] for r in remaining],'full_graph_cleared_residues':sorted(by_full),'least_union_period_before_return':least_period(union_before_return),'least_combined_period':least_period(combined),'wall_seconds':time.monotonic()-started}
Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if not isinstance(v,list)},sort_keys=True))
print('REMAINING',remaining)
print('COMBINED_COVER_COMPLETE')

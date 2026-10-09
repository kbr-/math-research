"""Bounded arithmetic controls: normality is an input, not a tested conclusion.
All enumerations are fixed and small (seconds); no original source ranks computed.
"""
import argparse,itertools,json,time
from pathlib import Path
ap=argparse.ArgumentParser(); ap.add_argument('--out',required=True); args=ap.parse_args()
t=time.monotonic()
def profile(n,x,j,h):
    B=2**(n-1); g=1+(n-3)*B//2; d=n+x-j
    return max(0,B*d+1-g-max(B*d-h,0))
checks=0
for x,a,j,h in itertools.product(range(21),range(3),range(3),range(32)):
    assert profile(4,x,j,h)==profile(4,min(x,2),j,h)
    assert min(3*x+a,2)==min(3*min(x,2)+a,2)
    checks+=1
calibration=[]
for h,a in itertools.product([0,768,1537,2303],range(3)):
    children=[]
    for r in range(3):
        c=(a-2*r)//3
        hp=2304+256*c+( -(256*(9+a)-h-r)//3 )
        children.append(0 if hp<0 else profile(9,20,-c,hp))
    parent=profile(9,60+a,0,h); rank=sum(children)-parent
    assert 0<=rank<=2304
    calibration.append(dict(delta=h,digit=a,children=children,parent=parent,compatibility_rank=rank))
trans=[[min(3*q+a,5) for a in range(3)] for q in range(6)]
out=[int(q==4) for q in range(6)]
assert out[1]==out[2] and out[trans[1][1]]!=out[trans[2][1]]
part=out[:]; rounds=0
def eq(v): return [[v[q]==v[r] for r in range(6)] for q in range(6)]
while True:
    keys=[(out[q],tuple(part[s] for s in trans[q])) for q in range(6)]
    ids={key:i for i,key in enumerate(dict.fromkeys(keys))}
    new=[ids[key] for key in keys]
    same=eq(new)==eq(part); part=new
    if same: break
    rounds+=1
    assert rounds<=5
words=[w for k in range(6) for w in itertools.product(range(3),repeat=k)]
assert len(words)==364
obs=[]
for q in range(6):
    row=[]
    for word in words:
        s=q
        for a in word: s=trans[s][a]
        row.append(out[s])
    obs.append(row)
assert eq(part)==eq(obs)
classes=sorted([[q for q in range(6) if part[q]==c] for c in set(part)])
assert classes==[[0],[1],[2,3,5],[4]]
result=dict(scope=__doc__,profile_comparisons=checks,calibration=calibration,
    negative_control_classes=classes,refinement_rounds=rounds,word_count=len(words),
    observations=6*len(words),elapsed_seconds=time.monotonic()-t,completed=True)
Path(args.out).write_text(json.dumps(result,indent=2)+'\n'); print(json.dumps(result,indent=2))

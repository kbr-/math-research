#!/usr/bin/env python3
"""Exact first-jet interpolation controls, including GF(9), without dependencies beyond NumPy."""
import argparse, hashlib, itertools, json
from pathlib import Path
import numpy as np

def tables(q):
    p=3 if q==9 else q
    a,b=np.indices((q,q),dtype=np.int64)
    if q==9:
        add=(a%3+b%3)%3+3*((a//3+b//3)%3)
        mul=((a%3)*(b%3)-(a//3)*(b//3))%3+3*(((a%3)*(b//3)+(a//3)*(b%3))%3)
    else:add=(a+b)%q;mul=(a*b)%q
    neg=np.array([int(np.flatnonzero(add[i]==0)[0]) for i in range(q)])
    inv=np.array([0]+[int(np.flatnonzero(mul[i]==1)[0]) for i in range(1,q)])
    assert all(mul[i,inv[i]]==1 for i in range(1,q))
    return p,add,mul,neg,inv

def rank(matrix,field):
    _,add,mul,neg,inv=field
    a=matrix.copy();r=0
    for col in range(a.shape[1]):
        candidates=np.flatnonzero(a[r:,col])
        if not len(candidates):continue
        pivot=r+int(candidates[0]);a[[r,pivot]]=a[[pivot,r]]
        a[r]=mul[a[r],inv[a[r,col]]]
        factors=a[:,col].copy();factors[r]=0
        a=add[a,neg[mul[factors[:,None],a[r][None,:]]]]
        r+=1
        if r==a.shape[0]:break
    return r

def exponents(n,d):
    if n==1:return [(i,) for i in range(d+1)]
    return [(i,)+tail for i in range(d+1) for tail in exponents(n-1,d-i)]

def jets(q,n,d,field):
    p,add,mul,neg,inv=field
    points=np.array(list(itertools.product(range(q),repeat=n)),dtype=np.int64)
    e=np.array(exponents(n,d),dtype=np.int64)
    powers=np.ones((q,d+1),dtype=np.int64)
    for k in range(1,d+1):powers[:,k]=mul[powers[:,k-1],np.arange(q)]
    blocks=[]
    for derivative in [-1,*range(n)]:
        f=np.ones((len(points),len(e)),dtype=np.int64)
        for j in range(n):f=mul[f,powers[points[:,j,None],np.maximum(e[None,:,j]-(j==derivative),0)]]
        if derivative>=0:f=mul[f,(e[:,derivative]%p)[None,:]]
        blocks.append(f)
    return points,blocks

def run(q,n):
    field=tables(q);D=n*(q-1);target=D+q-1
    reports=[]
    for d in (target-1,target,target+1):
        points,blocks=jets(q,n,d,field)
        off=np.concatenate([b[1:] for b in blocks])
        r=rank(off,field)
        with_origin=rank(np.concatenate([off,*[b[:1] for b in blocks]]),field)
        with_value=rank(np.concatenate([off,blocks[0][:1]]),field)
        assert (with_origin-r)==(0 if d<target else 1 if d==target else n+1)
        assert (with_value-r)==(0 if d<target else 1)
        # If the origin value is forced to zero, a nonzero first derivative
        # first becomes possible at D+q, one degree beyond the optimal cover.
        assert with_origin-with_value == (0 if d<=target else n)
        reports.append(dict(degree=d,columns=off.shape[1],off_rows=off.shape[0],off_rank=r,
                            rank_with_origin_value=with_value,rank_with_all_origin_jets=with_origin,
                            off_matrix_sha256=hashlib.sha256(off.tobytes()).hexdigest()))
    _,add,mul,neg,inv=field
    sums=np.zeros(len(points),dtype=np.int64)
    for j in range(n):sums=add[sums,points[:,j]]
    coverage=np.count_nonzero(points,axis=1)+(sums!=0)
    assert coverage[0]==0 and np.min(coverage[1:])>=2
    return dict(q=q,n=n,field='GF(3)[a]/(a^2+1)' if q==9 else f'GF({q})',
                predicted_minimum=target,rank_checks=reports,construction_planes=target,
                construction_min_nonzero_coverage=int(np.min(coverage[1:])),origin_coverage=0)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
    cases=[(2,2),(3,1),(3,2),(3,3),(5,2),(9,2)]
    # Largest matrix is 243 x 378; integer table entries are at most 8.
    result={'scope':'Finite exact first-jet rank tests; not the general proof. No floating-point rank.',
            'cases':[run(q,n) for q,n in cases],'passed':True}
    args.out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'passed':True,'cases':len(cases),'report':str(args.out)}))

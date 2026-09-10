"""Exact PC proof checks for core-chain batching with rank-one residuals.
Uses NumPy sparse polynomial arithmetic and process-parallel independent cases.
Test bases are unsatisfiable propagation systems, not PHP. Private residual
variables are zero base axioms in the SOURCE proofs; the absorption certificates
never use these axioms, only previously learned cores and Boolean equations.
"""
from __future__ import annotations
import json, time, os
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import numpy as np
from pc_engine import Context, Poly, Proof, field_derivation, verify_with_output


def substitute(P, vals):
    ctx=P.ctx
    if not P.k.size:return P
    # Vectorize every scalar substitution first. This annihilates most terms
    # before the (few) genuinely affine replacements require expansion.
    scalars=[]; nonlinear_positions=[]
    for i,v in enumerate(vals):
        if v is None:scalars.append(None)
        elif v.degree<=0:scalars.append(0 if not v.k.size else int(v.c[0]))
        else:scalars.append(None);nonlinear_positions.append(i)
    P=P.specialize(scalars)
    if not P.k.size or not nonlinear_positions:return P
    ex=ctx.exponents(P.k).astype(np.int64)
    old=np.ones(len(vals),dtype=bool);old[nonlinear_positions]=False
    powers={}
    out=ctx.zero
    for row,c in zip(ex,P.c):
        key=np.sum(row[old].astype(np.uint64)*ctx.units[old],dtype=np.uint64)
        term=Poly(ctx,[key],[c])
        for v in np.flatnonzero((row>0)&~old):
            k=(int(v),int(row[v]))
            if k not in powers:powers[k]=vals[v]**int(row[v])
            term=term*powers[k]
        out=out+term
    return out


def rank_mod(A,p):
    A=np.array(A,dtype=np.int64,copy=True)%p
    r=0
    for j in range(A.shape[1]):
        nz=np.flatnonzero(A[r:,j])
        if not len(nz):continue
        z=r+int(nz[0]);A[[r,z]]=A[[z,r]]
        A[r]=A[r]*pow(int(A[r,j]),-1,p)%p
        rows=np.flatnonzero(A[:,j]);rows=rows[rows!=r]
        A[rows]=(A[rows]-A[rows,j,None]*A[r,None,:])%p
        r+=1
        if r==A.shape[0]:break
    return r


def make_source(N,h,p,delta,core_degree=None):
    D=1+(2*h-1)*(delta+1)+2*delta
    core_degree=delta if core_degree is None else core_degree
    petal_degree=delta if core_degree<delta else 1
    B=D+(p-1)*core_degree
    ntruth=N if core_degree==1 else 2*N
    nold=ntruth+N*petal_degree
    names=[f'x{i}' for i in range(ntruth)]+[f'w{k}' for k in range(N*petal_degree)]
    rmap={}
    for k in range(1,N+1):
        for u in range(h):
            for j in range(k+1):
                rmap[k,u,j]=len(names);names.append(f'r{k}_{u}_{j}')
    ctx=Context(names,p,B)
    x=[ctx.variable(i) for i in range(ntruth)]
    truth=x if core_degree==1 else [x[2*i]*x[2*i+1] for i in range(N)]
    b=[1-z for z in truth]
    w={}
    for k in range(1,N+1):
        w[k]=ctx.one
        for j in range(petal_degree):w[k]=w[k]*ctx.variable(ntruth+(k-1)*petal_degree+j)
    r={key:ctx.variable(v) for key,v in rmap.items()}
    g={};A={0:ctx.one};U={};Up={};E={}
    for k in range(1,N+1):
        g[k]=[b[0]+w[k]]+b[1:k]+[w[k]]
        pref=ctx.one
        for u in range(h):
            for j in range(k):U[k,j]=U.get((k,j),ctx.zero)+r[k,u,j]*pref
            Up[k]=Up.get(k,ctx.zero)+(r[k,u,k]+r[k,u,0])*pref
            pref=pref*(1-sum((r[k,u,j]*g[k][j] for j in range(k+1)),ctx.zero))
        A[k]=pref
        for j in range(k+1):E[k,j]=g[k][j]*pref
        assert 1-A[k]==sum((U[k,j]*b[j] for j in range(k)),ctx.zero)+Up[k]*w[k]
    old={('base',k):b[k]*(ctx.one if k==0 else truth[k-1]) for k in range(N)}
    old['sink',0]=truth[-1]
    old.update({('petal',k):v for k,v in w.items()})
    old.update({('bool',i):ctx.variable(i)**2-ctx.variable(i) for i in range(nold)})
    axioms=dict(old)
    axioms.update({('ext',k,j):v for (k,j),v in E.items()})
    axioms.update({('newfield',v):ctx.variable(v)**p-ctx.variable(v) for v in rmap.values()})
    src=Proof(ctx,D);ids={label:src.axiom(P,label) for label,P in axioms.items()}
    coreE={}
    for k in range(1,N+1):
        coreE[k,0]=src.lin(ids['ext',k,0],ids['ext',k,k],1,-1)
        for j in range(1,k):coreE[k,j]=ids['ext',k,j]
    summands=[]
    for k in range(1,N+1):
        for j in range(k-1):summands.append(src.multiple(coreE[k-1,j],U[k,j]))
        summands.append(src.multiple(ids['base',k-1],U[k,k-1]*A[k-1]))
        if k>1:summands.append(src.multiple(coreE[k-1,k-2],U[k,k-1]*b[k-1]))
        summands.append(src.multiple(ids['petal',k],Up[k]*A[k-1]))
        for j in range(k-1):summands.append(src.multiple(coreE[k,j],-U[k-1,j]))
        if k>1:summands.append(src.multiple(ids['petal',k-1],-Up[k-1]*A[k]))
    summands.append(src.multiple(ids['sink',0],A[N]));summands.append(coreE[N,N-1])
    end=summands[0]
    for z in summands[1:]:end=src.lin(end,z)
    assert src.polys[end]==ctx.one
    return ctx,src,end,old,axioms,rmap,g,b,w,D,B,nold


def run_case(spec):
    t0=time.perf_counter();N,h,p,delta=spec[:4]
    core_degree=delta if len(spec)==4 else spec[4]
    ctx,src,end,old,axioms,rmap,g,b,w,D,B,nold=make_source(*spec)
    verify_with_output(src,axioms,end)
    out=Proof(ctx,B);oldids={label:out.axiom(P,label) for label,P in old.items()}
    boolids=[oldids['bool',i] for i in range(nold)]
    learned={};absorbed={};permanent=[None]*nold+[ctx.zero]*(len(ctx.names)-nold)
    stats={'reused_absorbed_axioms':0,'selector_field_checks':0,'newfield_checks':0,
           'absorber_certificates':0,'nonzero_core_controls':0,'full_line_images_checked':0}
    def translate(vals,theta,stage):
        mapping=[];cache={}
        def image(P):
            if P.signature not in cache:cache[P.signature]=substitute(P,vals)
            return cache[P.signature]
        for P,rule in zip(src.polys,src.rules):
            if rule[0]=='axiom':
                label=rule[1]
                if label in old:q=out.multiple(oldids[label],theta)
                elif label[0]=='newfield':
                    q=field_derivation(theta*image(P),out,boolids,nold);stats['newfield_checks']+=1
                else:
                    _,a,i=label
                    if stage is None or a<stage:
                        q=out.multiple(absorbed[a,i],theta);stats['reused_absorbed_axioms']+=1
                    else:
                        q=field_derivation(theta*image(P),out,boolids,nold);stats['selector_field_checks']+=1
            elif rule[0]=='lin':
                _,a,z,ca,cz=rule;q=out.lin(mapping[a],mapping[z],ca,cz)
            else:
                _,a,v=rule
                q=out.mulvar(mapping[a],v) if vals[v] is None else out.multiple(mapping[a],vals[v])
            assert out.polys[q]==theta*image(P)
            stats['full_line_images_checked']+=1
            mapping.append(q)
        assert out.polys[mapping[end]]==theta
        return mapping[end]
    max_beta_degree=0
    for k in range(1,N+1):
        j=k-1;fid=[]
        for alpha in range(1,p):
            vals=list(permanent);inv=pow(alpha,-1,p)
            for a in range(k,N+1):
                for u in range(h):
                    for i in range(a+1):vals[rmap[a,u,i]]=ctx.zero
                vals[rmap[a,0,j]]=ctx.constant(inv)
                if j==0:vals[rmap[a,0,a]]=ctx.constant(-inv)
            theta=1-(b[j]-alpha)**(p-1)
            fid.append(out.scale(translate(vals,theta,k),alpha))
        learned[j]=fid[0]
        for q in fid[1:]:learned[j]=out.lin(learned[j],q)
        assert out.polys[learned[j]]==b[j]
        # Absorb rank-one quotient via all nonzero field values, packed into h groups.
        groups=np.array_split(np.arange(1,p,dtype=np.int64),h)
        for u,group in enumerate(groups):
            prefix=ctx.one;beta=ctx.zero
            for alpha in group:
                inv=pow(int(alpha),-1,p)
                beta=beta+prefix*inv
                prefix=prefix*(1-inv*w[k])
            assert beta.degree<=1
            if delta>1:assert len(group)<=1  # nonlinear theorem's scalar regime
            permanent[rmap[k,u,k]]=beta
            max_beta_degree=max(max_beta_degree,beta.degree)
            for i in range(k):permanent[rmap[k,u,i]]=ctx.zero
        Z=1-w[k]**(p-1)
        for i in range(k+1):
            parts=[]
            if i<k:parts.append(out.multiple(learned[i],Z))
            if i==0 or i==k:
                parts.append(field_derivation(w[k]*Z,out,boolids,nold))
            q=parts[0]
            for z in parts[1:]:q=out.lin(q,z)
            target=substitute(axioms['ext',k,i],permanent)
            assert out.polys[q]==target
            absorbed[k,i]=q;stats['absorber_certificates']+=1
            if i<k:
                assert target.bool_normal(nold).k.size>0
                stats['nonzero_core_controls']+=1
        # Negative control: the residual cannot simply be omitted after setting cores to zero.
        assert w[k].bool_normal(nold).k.size>0
    final=translate(permanent,ctx.one,None)
    verify_with_output(out,old,final)
    # Verify genuine pairwise incomparability of all literal polynomial input spans.
    keys=np.unique(np.concatenate([v.k for gs in g.values() for v in gs]))
    def matrix(gs):
        A=np.zeros((len(gs),len(keys)),dtype=np.int64)
        for r,v in enumerate(gs):A[r,np.searchsorted(keys,v.k)]=v.c
        return A
    matrices={a:matrix(gs) for a,gs in g.items()}
    antichain_pairs=0
    for a in range(1,N+1):
        assert rank_mod(matrices[a],p)==a+1
        for z in range(a+1,N+1):
            union=rank_mod(np.vstack([matrices[a],matrices[z]]),p)
            assert union>rank_mod(matrices[a],p) and union>rank_mod(matrices[z],p)
            antichain_pairs+=1
    return {'N':N,'h':h,'p':p,'delta':delta,'core_degree':core_degree,'source_degree_bound':D,'target_degree_bound':B,
            'source_max_degree':src.maxdegree,'output_max_degree':out.maxdegree,
            'source_lines':len(src.polys),'output_lines':len(out.polys),
            'antichain_pairs_checked':antichain_pairs,'max_beta_degree':max_beta_degree,
            **stats,'seconds':time.perf_counter()-t0,'passed':True}


if __name__=='__main__':
    t0=time.perf_counter()
    cases=[(2,1,2,1),(3,1,2,1),(2,2,2,1),(2,1,3,1),
           (2,2,3,1),(2,1,2,2),(2,1,2,2,1)]
    with ProcessPoolExecutor(max_workers=4) as pool:results=list(pool.map(run_case,cases))
    report={'cases':results,'wall_seconds':time.perf_counter()-t0,'max_workers':4,
            'sum_worker_seconds':sum(r['seconds'] for r in results),
            'all_passed':all(r['passed'] for r in results)}
    Path(__file__).with_name('results.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))

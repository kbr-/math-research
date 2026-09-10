"""Exact NumPy sparse-polynomial PC check for nested ENS batches.
All arithmetic is modular integer arithmetic. Independent cases run in processes.
No floating-point ranks or symbolic-equivalence black boxes are used.
"""
from __future__ import annotations
import time, json, math, os
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from pathlib import Path
import numpy as np

class Context:
    def __init__(self, names, p, max_degree):
        self.names=tuple(names); self.p=int(p)
        self.bits=int(max_degree).bit_length()
        self.base=1<<self.bits
        if self.bits*len(names)>63: raise ValueError('Kronecker keys would overflow')
        self.shifts=np.arange(len(names),dtype=np.uint64)*np.uint64(self.bits)
        self.units=np.left_shift(np.uint64(1),self.shifts)
        self.mask=np.uint64(self.base-1)
        self.zero=Poly(self,np.array([],dtype=np.uint64),np.array([],dtype=np.int64),canonical=True)
        self.one=self.constant(1)
    def constant(self,c): return Poly(self,[0],[c])
    def variable(self,i): return Poly(self,[self.units[i]],[1])
    def exponents(self,keys):
        return (np.asarray(keys,dtype=np.uint64)[:,None]>>self.shifts[None,:])&self.mask

class Poly:
    __slots__=('ctx','k','c','degree','signature')
    def __init__(self,ctx,keys,coef,canonical=False):
        self.ctx=ctx
        k=np.asarray(keys,dtype=np.uint64); c=np.asarray(coef,dtype=np.int64)%ctx.p
        if k.size and not canonical:
            order=np.argsort(k,kind='stable'); k=k[order]; c=c[order]
            starts=np.r_[0,np.flatnonzero(k[1:]!=k[:-1])+1]
            c=np.add.reduceat(c,starts)%ctx.p; k=k[starts]
            nonzero=c!=0; k=k[nonzero]; c=c[nonzero]
        self.k=k; self.c=c
        self.degree=int(ctx.exponents(k).sum(axis=1).max()) if k.size else -1
        self.signature=(k.tobytes(),c.tobytes())
    def __eq__(self,o):
        return isinstance(o,Poly) and self.ctx is o.ctx and self.signature==o.signature
    def __add__(self,o):
        if not isinstance(o,Poly):o=self.ctx.constant(o)
        return Poly(self.ctx,np.r_[self.k,o.k],np.r_[self.c,o.c])
    __radd__=__add__
    def __neg__(self):return self.scale(-1)
    def __sub__(self,o):return self+-o
    def __rsub__(self,o):return self.ctx.constant(o)+-self
    def scale(self,a):return Poly(self.ctx,self.k,self.c*int(a))
    def __mul__(self,o):
        if not isinstance(o,Poly):return self.scale(o)
        if not self.k.size or not o.k.size:return self.ctx.zero
        if self.degree+o.degree>=self.ctx.base:
            raise OverflowError('Polynomial product would carry between exponent digits')
        return Poly(self.ctx,(self.k[:,None]+o.k[None,:]).ravel(),(self.c[:,None]*o.c[None,:]).ravel())
    __rmul__=__mul__
    def __pow__(self,e):
        out=self.ctx.one; q=self
        while e:
            if e&1:out=out*q
            e>>=1
            if e:q=q*q
        return out
    def mulvar(self,i):
        if not self.k.size:return self
        return Poly(self.ctx,self.k+self.ctx.units[i],self.c,canonical=True)
    def specialize(self,vals):
        # vals[i] = None retains the variable; otherwise a field scalar.
        if not self.k.size:return self
        ex=self.ctx.exponents(self.k); keep=np.array([v is None for v in vals])
        keys=(ex[:,keep]*self.ctx.units[keep]).sum(axis=1,dtype=np.uint64)
        coeff=self.c.copy()
        for i,v in enumerate(vals):
            if v is None:continue
            powers=np.array([pow(int(v),a,self.ctx.p) for a in range(self.ctx.base)],dtype=np.int64)
            coeff=coeff*powers[ex[:,i].astype(np.int64)]%self.ctx.p
        return Poly(self.ctx,keys,coeff)
    def bool_normal(self,nold):
        if not self.k.size:return self
        ex=self.ctx.exponents(self.k)
        ex[:,:nold]=(ex[:,:nold]>0)
        return Poly(self.ctx,(ex*self.ctx.units).sum(axis=1,dtype=np.uint64),self.c)

class Proof:
    def __init__(self,ctx,degree_bound):
        self.ctx=ctx; self.bound=degree_bound; self.polys=[]; self.rules=[]; self.index={}
        self.maxdegree=-1
    def _add(self,P,rule):
        if P.degree>self.bound:raise AssertionError(('degree overflow',P.degree,self.bound,rule))
        if P.signature in self.index:return self.index[P.signature]
        i=len(self.polys);self.polys.append(P);self.rules.append(rule);self.index[P.signature]=i
        self.maxdegree=max(self.maxdegree,P.degree);return i
    def axiom(self,P,label):return self._add(P,('axiom',label))
    def lin(self,i,j,a=1,b=1):
        return self._add(self.polys[i].scale(a)+self.polys[j].scale(b),('lin',i,j,int(a),int(b)))
    def scale(self,i,a):return self.lin(i,i,a,0)
    def mulvar(self,i,v):return self._add(self.polys[i].mulvar(v),('mul',i,int(v)))
    def zero(self):
        if not self.polys:raise ValueError('need an axiom first')
        return self.lin(0,0,1,-1)
    def multiple(self,i,q):
        if not q.k.size:return self.zero()
        terms=[]
        for key,coeff in zip(q.k,q.c):
            j=i
            ex=self.ctx.exponents(np.array([key],dtype=np.uint64))[0]
            for var in np.flatnonzero(ex):
                for _ in range(int(ex[var])):j=self.mulvar(j,int(var))
            terms.append(self.scale(j,int(coeff)))
        out=terms[0]
        for j in terms[1:]:out=self.lin(out,j)
        return out
    def verify(self,allowed_axioms):
        # Separate replay: reconstruct every primitive inference, not just the final identity.
        for i,(P,rule) in enumerate(zip(self.polys,self.rules)):
            tag=rule[0]
            if tag=='axiom':expected=allowed_axioms[rule[1]]
            elif tag=='lin':
                _,a,b,ca,cb=rule
                assert a<i and b<i
                expected=self.polys[a].scale(ca)+self.polys[b].scale(cb)
            elif tag=='mul':
                _,a,v=rule;assert a<i
                expected=self.polys[a].mulvar(v)
            else:raise AssertionError(tag)
            assert P==expected, ('invalid line',i,rule)
            assert P.degree<=self.bound
        assert self.polys[-1]==self.ctx.one
        return len(self.polys)


def field_derivation(P,out,bool_ids,nold):
    """Divide by old Boolean equations, keeping a checked PC certificate."""
    ctx=P.ctx; rem=P; terms=[]
    for v in range(nold):
        if not rem.k.size:break
        ex=ctx.exponents(rem.k)[:,v].astype(np.int64)
        active=np.flatnonzero(ex>=2)
        if not active.size:continue
        counts=ex[active]-1
        ridx=np.repeat(active,counts)
        starts=np.repeat(np.cumsum(counts)-counts,counts)
        offset=np.arange(int(counts.sum()))-starts
        qkeys=rem.k[ridx]-ex[ridx].astype(np.uint64)*ctx.units[v]+offset.astype(np.uint64)*ctx.units[v]
        Q=Poly(ctx,qkeys,rem.c[ridx])
        terms.append(out.multiple(bool_ids[v],Q))
        reduced=rem.k-np.maximum(ex-1,0).astype(np.uint64)*ctx.units[v]
        rem=Poly(ctx,reduced,rem.c)
    if rem.k.size:raise AssertionError('polynomial is not in old Boolean ideal')
    if not terms:return out.zero()
    z=terms[0]
    for j in terms[1:]:z=out.lin(z,j)
    assert out.polys[z]==P
    return z


def make_source(N,h,p,delta):
    nvars=N+h*N*(N+1)//2
    source_d=(2*h-1)*(delta+1)-delta+2*delta+1  # reset to safe exact ceiling below
    # U has degree 1+(h-1)(delta+1), A has h(delta+1), f at most 2delta.
    source_d=1+(2*h-1)*(delta+1)+2*delta
    target=source_d+(p-1)*delta
    nold=N if delta==1 else 2*N
    names=[f'x{i}' for i in range(nold)]
    rmap={}
    for k in range(1,N+1):
        for u in range(h):
            for j in range(k):
                rmap[(k,u,j)]=len(names);names.append(f'r{k}_{u}_{j}')
    ctx=Context(names,p,target)
    x=[ctx.variable(i) for i in range(nold)]
    truth=x if delta==1 else [x[2*i]*x[2*i+1] for i in range(N)]
    b=[1-z for z in truth]
    r={k:ctx.variable(v) for k,v in rmap.items()}
    A={0:ctx.one};U={};E={}
    for k in range(1,N+1):
        prefix=ctx.one
        for u in range(h):
            for j in range(k):U[(k,j)]=U.get((k,j),ctx.zero)+r[(k,u,j)]*prefix
            factor=1-sum((r[(k,u,j)]*b[j] for j in range(k)),ctx.zero)
            prefix=prefix*factor
        A[k]=prefix
        for j in range(k):E[(k,j)]=b[j]*prefix
        assert 1-A[k]==sum((U[(k,j)]*b[j] for j in range(k)),ctx.zero)
    old={('base',k):b[k]*(ctx.one if k==0 else truth[k-1]) for k in range(N)}
    old[('sink',0)]=truth[-1]
    for i in range(nold):old[('bool',i)]=x[i]**2-x[i]
    allaxioms=dict(old);allaxioms.update({('ext',k,j):v for (k,j),v in E.items()})
    src=Proof(ctx,source_d);ids={k:src.axiom(v,k) for k,v in allaxioms.items()}
    certificate=[]
    for k in range(1,N+1):
        for j in range(k-1):certificate.append((('ext',k-1,j),U[(k,j)]))
        certificate.append((('base',k-1),U[(k,k-1)]*A[k-1]))
        if k>1:certificate.append((('ext',k-1,k-2),U[(k,k-1)]*b[k-1]))
        for j in range(k-1):certificate.append((('ext',k,j),-U[(k-1,j)]))
    certificate.extend([(('sink',0),A[N]),(('ext',N,N-1),ctx.one)])
    summands=[src.multiple(ids[label],q) for label,q in certificate]
    end=summands[0]
    for i in summands[1:]:end=src.lin(end,i)
    assert src.polys[end]==ctx.one
    # Proof deduplication can make the final result an earlier line: retain explicit output ID.
    return ctx,src,end,old,allaxioms,rmap,b,source_d,target,nold


def verify_with_output(proof,axioms,end):
    # replay without assuming its last newly-added node is the designated output
    for i,(P,rule) in enumerate(zip(proof.polys,proof.rules)):
        if rule[0]=='axiom':expected=axioms[rule[1]]
        elif rule[0]=='lin':
            _,a,b,ca,cb=rule;assert a<i and b<i
            expected=proof.polys[a].scale(ca)+proof.polys[b].scale(cb)
        else:
            _,a,v=rule;assert a<i
            expected=proof.polys[a].mulvar(v)
        assert expected==P,(i,rule)
        assert P.degree<=proof.bound
    assert proof.polys[end]==proof.ctx.one


def run_case(spec):
    started=time.perf_counter();N,h,p,delta=spec
    ctx,src,source_end,old,allaxioms,rmap,g,d,B,nold=make_source(N,h,p,delta)
    verify_with_output(src,allaxioms,source_end)
    out=Proof(ctx,B)
    oldids={label:out.axiom(P,label) for label,P in old.items()}
    boolids=[oldids[('bool',i)] for i in range(nold)]
    learned={};norm_checks=0;reused=0
    def translate(vals,theta,stage):
        nonlocal norm_checks,reused
        mapping=[]
        for idx,(P,rule) in enumerate(zip(src.polys,src.rules)):
            kind=rule[0]
            if kind=='axiom':
                label=rule[1]
                if label[0]!='ext':q=out.multiple(oldids[label],theta)
                else:
                    _,a,i=label
                    if stage is None or a<stage:
                        assert i in learned
                        q=out.multiple(learned[i],theta);reused+=1
                    else:
                        image=theta*P.specialize(vals)
                        q=field_derivation(image,out,boolids,nold);norm_checks+=1
            elif kind=='lin':
                _,a,b,ca,cb=rule;q=out.lin(mapping[a],mapping[b],ca,cb)
            elif kind=='mul':
                _,a,v=rule
                q=out.mulvar(mapping[a],v) if vals[v] is None else out.scale(mapping[a],vals[v])
            else:raise AssertionError(kind)
            assert out.polys[q]==theta*P.specialize(vals),('translation mismatch',idx,stage)
            mapping.append(q)
        return mapping[source_end]
    for stage in range(1,N+1):
        j=stage-1; value_terms=[]
        for alpha in range(1,p):
            vals=[None]*nold+[0]*(len(ctx.names)-nold)
            for a in range(stage,N+1):vals[rmap[(a,0,j)]]=pow(alpha,-1,p)
            theta=1-(g[j]-alpha)**(p-1)
            theta_id=translate(vals,theta,stage)
            assert out.polys[theta_id]==theta
            value_terms.append(out.scale(theta_id,alpha))
        r=value_terms[0]
        for v in value_terms[1:]:r=out.lin(r,v)
        assert out.polys[r]==g[j]
        learned[j]=r
    final=translate([None]*nold+[0]*(len(ctx.names)-nold),ctx.one,None)
    verify_with_output(out,old,final)
    # This checks a genuinely invalid replacement: an earlier known input is not a field identity.
    field_control=(g[0]*(1-(g[1]-1)**(p-1))).bool_normal(nold)
    assert field_control.k.size, 'control unexpectedly vanished'
    return {'N_blocks':N,'nold':nold,'h':h,'p':p,'input_degree':delta,'source_bound':d,
            'actual_source_degree':src.maxdegree,'predicted_output_bound':B,
            'actual_output_degree':out.maxdegree,'source_lines_verified':len(src.polys),
            'output_lines_verified':len(out.polys),'field_derivations':norm_checks,
            'learned_input_reuses':reused,'negative_control_rejected':True,
            'wall_s':time.perf_counter()-started,'passed':True}

if __name__=='__main__':
    t=time.perf_counter()
    cases=[(3,1,2,1),(4,1,2,1),(5,1,2,1),
           (3,1,3,1),(4,1,3,1),(5,1,3,1),
           (3,1,5,1),(4,1,5,1),
           (3,2,2,1),(3,2,3,1),(3,2,5,1),
           (3,1,2,2),(3,1,3,2),(3,1,5,2)]
    with ProcessPoolExecutor(max_workers=4) as pool:
        results=list(pool.map(run_case,cases))
    report={'cases':results,'batch_wall_s':time.perf_counter()-t,'max_workers':4,
            'total_output_lines_verified':sum(x['output_lines_verified'] for x in results),
            'scope':'Full PC proof transformations for nested prefix blocks, with g_i=1-x_i (degree 1) or 1-x_{2i}x_{2i+1} (genuinely degree 2 on the Boolean domain); no PHP-wide compression assertion.'}
    dest=Path(__file__).with_name('chain_results.json');dest.write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))

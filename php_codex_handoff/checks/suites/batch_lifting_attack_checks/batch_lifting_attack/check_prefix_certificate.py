#!/usr/bin/env python3
"""Exact checks for an explicit one-level ENS refutation of pebbling axioms.

Small cases: formal sparse polynomial expansion over F_p, with monomials
packed into uint64. Polynomial products/grouping are NumPy-vectorized.
Large cases: batched modular evaluations on arbitrary (not just Boolean)
assignments. Independent cases run in separate processes.

This tests the displayed certificate, not a PHP lower bound, not the
literature pebbling lower bound, and not the separate PC-based lifting lemma.
"""
from __future__ import annotations
import argparse
import json
import math
import os
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from time import perf_counter
import numpy as np

class Ring:
    def __init__(self, nvars: int, p: int, max_degree: int):
        self.nvars = nvars
        self.p = p
        self.bits = max_degree.bit_length()
        if self.nvars * self.bits > 63:
            raise ValueError('Packed exponent space exceeds 63 bits')
        self.mask = (1 << self.bits) - 1
    def poly(self, powers, coeffs):
        powers = np.asarray(powers, dtype=np.uint64).ravel()
        coeffs = np.asarray(coeffs, dtype=np.int64).ravel() % self.p
        if len(powers) != len(coeffs):
            raise ValueError('Different array lengths')
        nz = coeffs != 0
        powers, coeffs = powers[nz], coeffs[nz]
        if not len(powers):
            return Poly(self, powers, coeffs)
        keys, inv = np.unique(powers, return_inverse=True)
        values = np.zeros(len(keys), dtype=np.int64)
        np.add.at(values, inv, coeffs)
        values %= self.p
        nz = values != 0
        return Poly(self, keys[nz], values[nz])
    def const(self, c):
        return self.poly([0], [c])
    def var(self, i):
        return self.poly([np.uint64(1) << np.uint64(self.bits*i)], [1])

class Poly:
    def __init__(self, ring, powers, coeffs):
        self.ring, self.powers, self.coeffs = ring, powers, coeffs
    def coerce(self, other):
        return other if isinstance(other, Poly) else self.ring.const(other)
    def __add__(self, other):
        other = self.coerce(other)
        return self.ring.poly(np.concatenate((self.powers, other.powers)),
                              np.concatenate((self.coeffs, other.coeffs)))
    __radd__ = __add__
    def __neg__(self):
        return self.ring.poly(self.powers, -self.coeffs)
    def __sub__(self, other):
        return self + (-self.coerce(other))
    def __rsub__(self, other):
        return self.coerce(other) - self
    def __mul__(self, other):
        other = self.coerce(other)
        if not len(self.powers) or not len(other.powers):
            return self.ring.const(0)
        powers = (self.powers[:, None] + other.powers[None, :]).ravel()
        coeffs = (self.coeffs[:, None] * other.coeffs[None, :]).ravel()
        return self.ring.poly(powers, coeffs)
    __rmul__ = __mul__
    def equal(self, other):
        other = self.coerce(other)
        return np.array_equal(self.powers, other.powers) and np.array_equal(self.coeffs, other.coeffs)
    def degree(self):
        if not len(self.powers):
            return -1
        shifts = np.arange(self.ring.nvars, dtype=np.uint64)*self.ring.bits
        degrees = ((self.powers[:, None] >> shifts[None, :]) & self.ring.mask).sum(axis=1)
        return int(degrees.max())

def symbolic_case(task):
    p, h, preds = task
    N = len(preds)
    D = 4*h + 2
    ring = Ring(N + h*N*(N+1)//2, p, D)
    one = ring.const(1)
    xs = [ring.var(i) for i in range(N)]
    bs = [one-x for x in xs]
    A = [one]
    U = [[]]
    E = [[]]
    next_var = N
    for k in range(1, N+1):
        r = [[ring.var(next_var+u*k+j) for j in range(k)] for u in range(h)]
        next_var += h*k
        prefix = one
        row = [ring.const(0) for _ in range(k)]
        for u in range(h):
            for j in range(k):
                row[j] = row[j] + r[u][j]*prefix
            prefix = prefix*(one-sum((r[u][j]*bs[j] for j in range(k)), ring.const(0)))
        A.append(prefix)
        U.append(row)
        E.append([bs[j]*prefix for j in range(k)])
        assert (sum((row[j]*bs[j] for j in range(k)), ring.const(0))).equal(one-prefix)
    total = ring.const(0)
    peak_degree = 0
    terms_checked = 0
    source_term = None
    for k in range(1, N+1):
        ps = preds[k-1]
        product = one
        for j in ps:
            product = product*xs[j]
        f = bs[k-1]*product
        terms = [U[k][k-1]*A[k-1]*f]
        if k == 1:
            source_term = terms[0]
        for j in range(k-1):
            terms.append(U[k][j]*E[k-1][j])
            terms.append(-U[k-1][j]*E[k][j])
        preceding = one
        for j in ps:
            terms.append(U[k][k-1]*bs[k-1]*preceding*E[k-1][j])
            preceding = preceding*xs[j]
        step = sum(terms, ring.const(0))
        assert step.equal(A[k-1]-A[k]), (p,h,N,k,'step')
        for t in terms:
            peak_degree = max(peak_degree, t.degree())
            assert t.degree() <= D
        terms_checked += len(terms)
        total = total+step
    sink_term = A[N]*xs[-1]
    total = total+sink_term+E[N][N-1]
    assert total.equal(1), (p,h,N,'certificate')
    # Two negative controls must fail as formal polynomial identities.
    assert not (total-sink_term).equal(1)
    assert not (total-source_term).equal(1)
    return {'kind':'formal_polynomial', 'p':p, 'h':h, 'vertices':N,
            'companions':N*(N+1)//2, 'degree_bound':D,
            'maximum_expanded_summand_degree':peak_degree,
            'summands_checked':terms_checked+2,
            'negative_controls':2, 'passed':True}

def evaluation_case(task):
    p, h, N, batch, seed = task
    rng = np.random.default_rng(seed)
    xs = rng.integers(0, p, size=(batch,N), dtype=np.int64)
    bs = (1-xs)%p
    one = np.ones(batch, dtype=np.int64)
    Aprev = one.copy()
    Uprev = np.empty((batch,0), dtype=np.int64)
    Eprev = np.empty((batch,0), dtype=np.int64)
    total = np.zeros(batch, dtype=np.int64)
    for k in range(1,N+1):
        r = rng.integers(0,p,size=(batch,h,k),dtype=np.int64)
        pref = one.copy()
        U = np.zeros((batch,k), dtype=np.int64)
        for u in range(h):
            U = (U+r[:,u,:]*pref[:,None])%p
            factor = (1-(r[:,u,:]*bs[:,:k]).sum(axis=1))%p
            pref = pref*factor%p
        A = pref
        E = bs[:,:k]*A[:,None]%p
        assert np.all(((U*bs[:,:k]).sum(axis=1)-(1-A))%p == 0)
        # A fan-in-two DAG with a unique sink, last vertex N-1.
        preds = list(range(max(0,k-3),k-1)) if k>1 else []
        f = bs[:,k-1].copy()
        for j in preds:
            f = f*xs[:,j]%p
        step = U[:,k-1]*Aprev%p*f%p
        if k>1:
            step = (step+(U[:,:k-1]*Eprev).sum(axis=1)
                    -(Uprev*E[:,:k-1]).sum(axis=1))%p
        earlier = one.copy()
        for j in preds:
            step = (step+U[:,k-1]*bs[:,k-1]%p*earlier%p*Eprev[:,j])%p
            earlier = earlier*xs[:,j]%p
        assert np.all((step-(Aprev-A))%p == 0)
        total = (total+step)%p
        Aprev,Uprev,Eprev = A,U,E
    total = (total+Aprev*xs[:,-1]+Eprev[:,-1])%p
    assert np.all(total == 1)
    return {'kind':'batched_evaluation','p':p,'h':h,'vertices':N,
            'assignments':batch,'step_identities':batch*N,
            'degree_bound':4*h+2,'nonboolean_old_values_allowed':True,
            'passed':True}

def run_task(task):
    kind, data = task
    return symbolic_case(data) if kind == 'symbolic' else evaluation_case(data)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='results.json')
    ap.add_argument('--workers', type=int, default=4)
    args = ap.parse_args()
    tasks = []
    symbolic_specs = [
        (1,[[],[],[0,1]]),
        (1,[[],[0],[0,1],[1,2],[2,3]]),
        (2,[[],[],[0,1]]),
        (3,[[],[0]]),
    ]
    for p in [2,3,5,7]:
        for h,preds in symbolic_specs:
            tasks.append(('symbolic',(p,h,preds)))
        for h,N in [(1,32),(4,32),(8,64),(16,64)]:
            tasks.append(('evaluation',(p,h,N,512,100000+p*1000+h*10+N)))
    t0 = perf_counter()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(run_task,tasks))
    formal = [r for r in rows if r['kind']=='formal_polynomial']
    numerical = [r for r in rows if r['kind']=='batched_evaluation']
    result = {'scope':'Explicit one-level prefix ENS certificate; not PHP lower bounds or PC lifting.',
              'workers':args.workers,'elapsed_seconds':perf_counter()-t0,
              'formal_cases':len(formal),'evaluation_cases':len(numerical),
              'formal_summands_checked':sum(r['summands_checked'] for r in formal),
              'negative_controls':sum(r['negative_controls'] for r in formal),
              'assignments':sum(r['assignments'] for r in numerical),
              'step_evaluation_checks':sum(r['step_identities'] for r in numerical),
              'all_passed':all(r['passed'] for r in rows),'cases':rows}
    Path(args.out).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2))

if __name__=='__main__':
    main()

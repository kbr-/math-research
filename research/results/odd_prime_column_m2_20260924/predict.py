"""Splitting predictions from saved Hilbert functions (through degree 3): members P, P' split iff
HF(S) = HF(P) HF(P') / HF(A); S splits off from k random forms iff HF(S_rk) = HF(S)/(1+q+q^2)^k.
Also the free prediction for S.  Usage: python3 predict.py RESULT.json"""
import json, sys
r = json.load(open(sys.argv[1])); H = r['HF']
def mul(x, y): return [sum(x[i] * y[k - i] for i in range(k + 1)) for k in range(4)]
def div(x, y):
    q = []
    for k in range(4): q.append((x[k] - sum(q[i] * y[k - i] for i in range(k))) // y[0])
    return q
def divq(base, m):
    inv = [{0: 1, 1: -1, 2: 0}[i % 3] for i in range(4)]; c = [1, 0, 0, 0]
    for _ in range(m): c = [sum(c[i] * inv[s - i] for i in range(s + 1)) for s in range(4)]
    return [sum(base[i] * c[s - i] for i in range(s + 1)) for s in range(4)]
m = len(r['systems']['S']); out = dict(n=r['n'], HF=H)
out['S_free_prediction'] = divq(H['A'], m); out['S_free_excess'] = [x - y for x, y in zip(H['S'], out['S_free_prediction'])]
out['member_split_prediction'] = div(mul(H['P'], H['Pp']), H['A']); out['member_split_excess'] = [x - y for x, y in zip(H['S'], out['member_split_prediction'])]
out['random'] = [dict(k=k, HF=H[f'S_r{k}'], predicted=divq(H['S'], k), excess=[x - y for x, y in zip(H[f'S_r{k}'], divq(H['S'], k))])
                 for k in range(1, 10) if f'S_r{k}' in H]
print(json.dumps({k: v for k, v in out.items() if k != 'HF'}))
json.dump(out, open(sys.argv[1].replace('.json', '_pred.json'), 'w'), indent=1)

"""Independent validation of pure_tops.cpp on its own witness tuples, on the full domain (no quotient basis).

For each case (d, s, M, seed): the tuple is the kernel's (single mode, distinct directions, same sampling as
grid mode).  Checks: (1) rank of the full map sum_a m_a T_{s-4} -> T_s equals the kernel's rank; (2) every
vector of the explicit list (multiples of l_{a1}, l_{a2} in block a's coordinates, and for s = 8 the Koszul
pairs m_b e_a - m_a e_b) maps to zero; (3) (P): the list's rank equals the kernel dimension M dim T_{s-4} - rank.
Ranks by the compiled research/tools/rank_modp.  Usage: validate_p.py OUT.json d,s,M,seed [...] (one run)."""
import itertools, json, subprocess, sys
sys.path.insert(0, 'research/tools')
from rank_modp import rank_mod_p

def mons(d, k): return [e for e in itertools.product(range(3), repeat=d) if sum(e) == k]
def mul(p, l):
    q = {}
    for e, c in p.items():
        for i in [i for i in range(len(l)) if l[i] and e[i] < 2]:
            f = e[:i] + (e[i] + 1,) + e[i + 1:]; q[f] = (q.get(f, 0) + c * l[i]) % 3
    return {e: c for e, c in q.items() if c}
def shift(p, mu):
    q = {}
    for e, c in p.items():
        g = tuple(x + y for x, y in zip(e, mu))
        if max(g) <= 2: q[g] = (q.get(g, 0) + c) % 3
    return q

def case(d, s, M, seed):
    run = subprocess.run(['research/tmp/pure_tops', 'single', str(d), str(s), str(M), str(seed), '0', '1'], capture_output=True, text=True, check=True)
    krank = int(run.stdout.split('\n')[M - 1].split()[1])
    forms = [list(map(int, l.split()[1:])) for l in run.stderr.split('\n') if l.startswith('F')]
    lo, hi, lo1 = mons(d, s - 4), mons(d, s), mons(d, s - 5)
    li, hix = {e: i for i, e in enumerate(lo)}, {e: i for i, e in enumerate(hi)}
    tops = []
    for f in forms:
        m = {tuple([0] * d): 1}
        for l in (f[:d], f[:d], f[d:], f[d:]): m = mul(m, l)
        tops.append(m)
    image = {(a, j): {hix[e]: c for e, c in shift(tops[a], mu).items()} for a in range(M) for j, mu in enumerate(lo)}
    rows = [image[(a, j)] for a in range(M) for j in range(len(lo))]
    rtop = rank_mod_p(rows, len(hi), 3)
    lst = [{a * len(lo) + li[e]: c for e, c in mul({mu: 1}, l).items()} for a, f in enumerate(forms) for l in (f[:d], f[d:]) for mu in lo1]
    if s == 8:
        for a, b in itertools.combinations(range(M), 2):
            v = {a * len(lo) + li[e]: c for e, c in tops[b].items()}
            for e, c in tops[a].items(): k = b * len(lo) + li[e]; v[k] = (v.get(k, 0) - c) % 3
            lst.append({k: c for k, c in v.items() if c})
    in_kernel = True
    for v in lst:
        img = {}
        for k, c in v.items():
            for h, x in rows[k].items(): img[h] = (img.get(h, 0) + c * x) % 3
        in_kernel &= not any(img.values())
    rlist = rank_mod_p(lst, M * len(lo), 3); kernel = M * len(lo) - rtop
    rec = dict(d=d, s=s, M=M, seed=seed, kernel_rank=krank, full_rank=rtop, ranks_agree=krank == rtop,
               list_in_kernel=in_kernel, kernel_dim=kernel, list_rank=rlist, P_holds=rlist == kernel)
    print(json.dumps(rec), flush=True); return rec

res = [case(*map(int, c.split(','))) for c in sys.argv[2:]]
json.dump(dict(cases=res, all_ok=all(r['ranks_agree'] and r['list_in_kernel'] and r['P_holds'] for r in res)), open(sys.argv[1], 'w'), indent=1)
print('all ok' if all(r['ranks_agree'] and r['list_in_kernel'] and r['P_holds'] for r in res) else 'FAILURE')

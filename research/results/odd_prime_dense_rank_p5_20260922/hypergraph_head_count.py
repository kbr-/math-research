"""Finite check of Lemma HDH (hypergraph distinct-head count).

For a family H of q distinct heads (subsets of [s] of sizes 2..delta; the lemma allows 1..delta), let E be the delta-sets
containing some head and theta = |E| / C(s, delta).  Checked exactly on small s:
  (KK)  J_k <= max(0, C(x, k)) where C(x, delta) = C(s, delta) - |E|   (Lovasz form of Kruskal-Katona)
  (HDH) J_k <= C(s, k) exp(k (delta-1)/s - k theta/delta)
  (SUM) J_{<=k} <= sum_{j<delta} C(s, j) + 2.3 C(s, k) exp(k (delta-1)/s - k theta/delta), k <= s/4
        (nonvacuous only when delta <= k <= s/4: the s = 16 boards give k = 4 at delta = 3, 4)
  (MIX) |E| >= q / 2^delta
J_k counts k-subsets containing no head.  Families: uniform random, mixed-size random, split
(all delta-sets meeting a set T), clique-type (all delta-subsets of a set M), sunflower (common core).
"""
import itertools, json, math, random, sys
from math import comb

def genbinom(x, k):
    r = 1.0
    for i in range(k):
        r *= (x - i) / (i + 1)
    return r

def solve_x(target, delta, s):
    lo, hi = delta - 1.0, float(s)
    if target <= 0:
        return None
    for _ in range(200):
        mid = (lo + hi) / 2
        if genbinom(mid, delta) < target:
            lo = mid
        else:
            hi = mid
    return hi

def check(s, delta, heads, kmax):
    heads = [frozenset(h) for h in set(frozenset(h) for h in heads)]
    q = len(heads)
    masks = [sum(1 << v for v in h) for h in heads]
    E = set()
    for D in itertools.combinations(range(s), delta):
        m = sum(1 << v for v in D)
        if any((hm & m) == hm for hm in masks):
            E.add(m)
    theta = len(E) / comb(s, delta)
    x = solve_x(comb(s, delta) - len(E), delta, s)
    res = {"q": q, "E": len(E), "theta": theta, "mix_ok": len(E) >= q / 2 ** delta, "rows": []}
    Jcum = 0
    for k in range(0, kmax + 1):
        Jk = 0
        for K in itertools.combinations(range(s), k):
            m = sum(1 << v for v in K)
            if not any((hm & m) == hm for hm in masks):
                Jk += 1
        Jcum += Jk
        if k < delta:
            continue
        kk = 0.0 if x is None else max(0.0, genbinom(x, k))
        hdh = comb(s, k) * math.exp(k * (delta - 1) / s - k * theta / delta)
        sumb = sum(comb(s, j) for j in range(delta)) + 2.3 * hdh
        res["rows"].append({"k": k, "J_k": Jk, "KK": kk, "HDH": hdh, "J_le_k": Jcum, "SUM": sumb,
                            "ok_KK": Jk <= kk + 1e-9, "ok_HDH": Jk <= hdh + 1e-9,
                            "ok_SUM": (k > s / 4) or Jcum <= sumb + 1e-9})
    return res

def families(s, delta, rng):
    out = []
    allD = list(itertools.combinations(range(s), delta))
    for q in (3, 12, 40, 120):
        if q <= len(allD):
            out.append(("uniform", rng.sample(allD, q)))
    for q in (6, 25, 80):
        hs = []
        for _ in range(q):
            j = rng.randint(2, delta)
            hs.append(tuple(sorted(rng.sample(range(s), j))))
        out.append(("mixed", hs))
    for t in (1, 2, 3):
        T = set(range(t))
        out.append(("split", [D for D in allD if T & set(D)]))
    for m in (delta + 1, delta + 3):
        out.append(("clique", list(itertools.combinations(range(m), delta))))
    core = tuple(range(delta - 1))
    out.append(("sunflower", [core + (v,) for v in range(delta - 1, s)]))
    return out

if __name__ == "__main__":
    rng = random.Random(20260922)
    report = []
    ok = {"KK": True, "HDH": True, "SUM": True, "MIX": True}
    for (s, delta, kmax) in [(12, 2, 6), (12, 3, 6), (13, 4, 7), (14, 4, 6), (14, 3, 6), (16, 4, 5), (16, 3, 5)]:
        for name, hs in families(s, delta, rng):
            r = check(s, delta, hs, kmax)
            r.update({"s": s, "delta": delta, "family": name})
            report.append(r)
            ok["MIX"] &= r["mix_ok"]
            for row in r["rows"]:
                ok["KK"] &= row["ok_KK"]; ok["HDH"] &= row["ok_HDH"]; ok["SUM"] &= row["ok_SUM"]
    json.dump({"all_ok": ok, "instances": report}, open(sys.argv[1], "w"), indent=1)
    print("instances", len(report), "all_ok", ok)
    # tightness summary: max ratio J_k / KK and J_k / HDH over rows with J_k > 0
    rk = max((row["J_k"] / row["KK"]) for r in report for row in r["rows"] if row["KK"] > 0 and row["J_k"] > 0)
    rh = max((row["J_k"] / row["HDH"]) for r in report for row in r["rows"] if row["J_k"] > 0)
    print("max J/KK", round(rk, 4), "max J/HDH", round(rh, 4))

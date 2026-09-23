"""Compare where Koszul-and-Frobenius locality fails with the semi-regular series HS(G)/(1+q+q^2)^M.

dim G_t = dim K_t on the functional board (R rows, N labels); actual dim (G/IG)_t = dim K_t - rank Phi_t,
read from a syzygy_locality2 result.  Usage: python3 semiregular_check.py RESULT.json OUT.json"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
res = json.load(open(sys.argv[1]))['results']; out = []
for r in res:
    dimK = {int(t): v for t, v in r['dimK'].items()}; dimK[0] = 1
    T = max(dimK)
    for M, row in r['by_M'].items():
        M = int(M)
        # series HS(G) * (1-q)^M / (1-q^3)^M truncated at T, over the integers
        s = [dimK[t] for t in range(T + 1)]
        for _ in range(M):                      # divide by 1+q+q^2: c_t = a_t - c_(t-1) - c_(t-2)
            c = []
            for t in range(T + 1):
                c.append(s[t] - (c[t - 1] if t >= 1 else 0) - (c[t - 2] if t >= 2 else 0))
            s = c
        actual = [1] + [dimK[t] - row['degrees'][str(t)]['rank_phi'] for t in range(1, T + 1)]
        local = [True] + [row['degrees'][str(t)]['rank_phi'] == row['degrees'][str(t)]['Lkos'] for t in range(1, T + 1)]
        out.append(dict(R=r['rows'], N=r['labels'], seed=r['seed'], M=M, expected=s, actual=actual, kos_local=local,
                        series_matches=[all(actual[u] == s[u] for u in range(t + 1)) for t in range(T + 1)]))
        print(out[-1])
json.dump(out, open(sys.argv[2], 'w'), indent=1)

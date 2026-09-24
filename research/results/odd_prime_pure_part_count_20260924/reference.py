"""Reference for pure_tops.cpp on small cases: rank of the full map sum_a m_a T_{s-4}(d) -> T_s (all monomials
of T_{s-4}, no quotient basis), m_a = l_{a1}^2 l_{a2}^2, for each prefix of the kernel's forms (read from its
stderr), with exact ranks from research/tools/rank_modp.  Usage: reference.py d,s,Mmax,seed [...] (all cases in one run)"""
import subprocess, sys, itertools
sys.path.insert(0, 'research/tools')
from rank_modp import rank_mod_p
def check(d, s, Mmax, seed):
  run = subprocess.run(['research/tmp/pure_tops', 'single', str(d), str(s), str(Mmax), str(seed), '0', '0'], capture_output=True, text=True, check=True)
  kr = [int(l.split()[1]) for l in run.stdout.split('\n') if l]
  forms = [list(map(int, l.split()[1:])) for l in run.stderr.split('\n') if l.startswith('F')]
  def mons(k):
      return [e for e in itertools.product(range(3), repeat=d) if sum(e) == k]
  def mul(p, l):
      q = {}
      for e, c in p.items():
          for i in range(d):
              if l[i] and e[i] < 2:
                  f = list(e); f[i] += 1; f = tuple(f); q[f] = (q.get(f, 0) + c * l[i]) % 3
      return {e: c for e, c in q.items() if c}
  idx = {e: i for i, e in enumerate(mons(s))}; low = mons(s - 4)
  rows = []; ok = True
  for M, f in enumerate(forms, 1):
      a, b = f[:d], f[d:]
      m = {tuple([0] * d): 1}
      for l in (a, a, b, b): m = mul(m, l)
      for mu in low:
          row = {}
          for e, c in m.items():
              g = tuple(x + y for x, y in zip(e, mu))
              if max(g) <= 2: row[idx[g]] = (row.get(idx[g], 0) + c) % 3
          rows.append({k: v for k, v in row.items() if v})
      r = rank_mod_p(rows, len(idx), 3)
      print(M, r, kr[M - 1], 'OK' if r == kr[M - 1] else 'MISMATCH'); ok &= r == kr[M - 1]
  print('all match' if ok else 'MISMATCH FOUND')
  return ok
results = [check(*map(int, c.split(','))) for c in sys.argv[1:]]
print('all cases match' if all(results) else 'MISMATCH IN SOME CASE')

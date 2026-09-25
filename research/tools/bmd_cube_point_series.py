"""Local zero schemes of the 3-cube's threshold ideal at the double point, with alpha(Z), for a list of
(d, rho), by driving the compiled kernel bmd_cube_point_scheme (with collision lifts) and
bmd_cube_point_alpha.

Statement tested.  lem:cube-threshold-zero-scheme gives l_0(d+1, 4d+rho-1) >= alpha(Z_m) for rho >= 2,
with Z_m supported at the arrangement's multiple points.  The torsion-partition conjecture predicts
l_0 = B(d, rho).  For each (d, rho) this computes the stalk J_{Z,P} at P = (1:1:0) modulo m^K, raising
the truncation N until the colengths for K' <= K agree for two consecutive N (Artin-Rees exactness)
and raising K until the colength is constant in K' over the last two values (then m^K' lies in J_P
by Nakayama).  It then computes dim (I_Z)_l and alpha(Z) assuming Z is supported at the three
double points, and prints B(d, rho) for comparison.  One pass per case; each kernel call is one
elimination that gives every K' <= K at once.

Lower-bound mode (spec d:rho:N:K).  Every truncated solution contains the true local solutions, so
the computed image of W_m modulo m^K contains the true one; the computed dim (I_Z)_l is then an upper
bound and the computed alpha a lower bound for alpha of the double-point part of Z, hence for l_0,
for any N and K and without the stabilization or support assumptions.  This mode runs one kernel
call with the given N, K and reports that lower bound.
Usage: bmd_cube_point_series.py KERNEL p NMAX OUTDIR d:rho[:N:K] [...]
"""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DOUBLE = ['1', '1', '0', '0', '0', '1', '1', '0', '0']  # P = (1:1:0), y2 = 1, y3 = s, y1 = 1 + t
LIFTS = ['3:0', '1:2']


def B(d, rho):
    j = d - rho
    if j == 0:
        return 0
    q = min(rho, j)
    tot = j + q
    parts = [tot // q + (1 if i < tot % q else 0) for i in range(q)]
    return sum(x * x - 1 for x in parts)


def kernel(kern, p, d, m, N, K, rows):
    out = subprocess.run([kern, str(p), str(d), str(m), str(N), str(K)] + DOUBLE + [rows] + LIFTS,
                         capture_output=True, text=True, check=True).stdout
    col = []
    for line in out.splitlines():
        if line.startswith("K'="):
            col.append(int(line.rsplit('=', 1)[1]))
    return col


def main():
    kern, p, nmax, outdir = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    for spec in sys.argv[5:]:
        f = list(map(int, spec.split(':')))
        d, rho = f[0], f[1]
        assert 2 <= rho <= d, 'the zero-scheme lemma needs rho >= 2'
        m = 4 * d + rho - 1
        K, N, prev, done = 6, 10, None, False
        if len(f) == 4:
            N, K = f[2], f[3]
            rows = os.path.join(outdir, f'rows-d{d}-m{m}.txt')
            col = kernel(kern, p, d, m, N, K, rows)
            print(f'd={d} rho={rho} m={m} N={N} K={K} (lower-bound mode): colengths {col}', flush=True)
            done = True
        while not done and N <= nmax:
            rows = os.path.join(outdir, f'rows-d{d}-m{m}.txt')
            col = kernel(kern, p, d, m, N, K, rows)
            print(f'd={d} rho={rho} m={m} N={N} K={K}: colengths {col}', flush=True)
            if prev is not None and prev == col:
                if col[-1] == col[-2]:
                    done = True
                    break
                K += 4
                N = max(N, K + 4)
                prev = None
                continue
            prev = col
            N += 4
            if N < K + 4:
                N = K + 4
        if not done:
            print(f'd={d} rho={rho}: not stable up to N={nmax}; B={B(d, rho)}', flush=True)
            continue
        lmax = B(d, rho) + 2
        a = subprocess.run([sys.executable, os.path.join(HERE, 'bmd_cube_point_alpha.py'), rows, str(lmax), str(p)] + DOUBLE,
                           capture_output=True, text=True, check=True).stdout
        dims = [l.split('=')[-1].strip() for l in a.splitlines() if l.startswith('l=')]
        alpha = a.strip().splitlines()[-1]
        print(f'd={d} rho={rho} m={m}: stalk colength {col[-1]} (K={K}, N={N}); dim (I_Z)_l for l=0..{lmax}: '
              f'{",".join(dims)}; {alpha}; B={B(d, rho)}', flush=True)


if __name__ == '__main__':
    main()

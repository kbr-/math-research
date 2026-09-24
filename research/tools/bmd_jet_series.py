"""Run bmd_jet_orders over a list of (n,k) and compare delta(n,k,l) with a reference.

Tested statement: delta(n,k,l) = n+2k-2-s_2(k-l-1) for n >= floor(log2 k)+2 (per-order formula).
Modes:
  validate BIN OUTDIR TABLEDIR  -- rerun every case of the dense exact table and require equality
                                   wherever the dense kernel recorded a value (control).
  series BIN OUTDIR n:k1-k2 ... -- compute the listed cases and compare with the formula.
Each case is written to OUTDIR as soon as it finishes; a summary line is printed per case.
"""
import glob, json, subprocess, sys
from pathlib import Path


def formula(n, k, l):
    return n + 2 * k - 2 - bin(k - l - 1).count('1')


def base_dim(k):
    return k.bit_length() + 1  # floor(log2 k) + 2


def run(binary, n, k, outdir):
    path = Path(outdir) / f'n{n}-k{k}.json'
    subprocess.run([binary, str(n), str(k), '--out', str(path)], check=True,
                   stdout=subprocess.DEVNULL)
    return json.loads(path.read_text())


def main():
    mode, binary, outdir = sys.argv[1:4]
    Path(outdir).mkdir(parents=True, exist_ok=True)
    if mode == 'validate':
        bad = 0
        for p in sorted(glob.glob(sys.argv[4] + '/n*-k*.json')):
            ref = json.load(open(p))
            n, k = ref['n'], ref['k']
            got = run(binary, n, k, outdir)['delta']
            want = [o['min_degree'] for o in ref['orders']]
            ok = all(w is None or w == g for w, g in zip(want, got))
            bad += not ok
            print(f'validate n={n} k={k}: jet {got} dense {want} {"OK" if ok else "MISMATCH"}', flush=True)
        print(f'validation mismatches: {bad}', flush=True)
        sys.exit(1 if bad else 0)
    for n, k in cases(sys.argv[4:]):
        report(n, k, run(binary, n, k, outdir))


def cases(specs):
    """Expand n:k1-k2 specifications into (n, k) pairs."""
    out = []
    for spec in specs:
        n, ks = spec.split(':')
        lo, hi = (ks.split('-') + [ks])[:2]
        out += [(int(n), k) for k in range(int(lo), int(hi) + 1)]
    return out


def report(n, k, res):
    diff = [l for l in range(k) if res['delta'][l] != formula(n, k, l)]
    tag = 'base' if n == base_dim(k) else ('above' if n > base_dim(k) else 'below')
    print(f'series n={n} k={k} ({tag}, {res["seconds"]:.1f}s): delta {res["delta"]} '
          f'formula-mismatch orders {diff}', flush=True)


if __name__ == '__main__':
    main()

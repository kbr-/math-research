#!/usr/bin/env python3
"""Cycle 218 follow-up: the linear image test of php_relative_image_check.py on the exact forms of the blocks used by
augmented_php_degree.py (same seed and sampling order), with and without the hole axioms.
Usage: block_forms_image_check.py --out FILE"""
import argparse, importlib.util, json, random, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / f'{name}.py'); mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod); return mod
img = load('php_relative_image_check'); aug = load('augmented_php_degree')
ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); a = ap.parse_args()
N = 8; m = N + 1; recs = []
cases = [('3-uniform-seed1', 1, False, 3), ('3-affine-seed1', 1, True, 3), ('3-uniform-seed2', 2, False, 3), ('4-uniform-seed1', 1, False, 4)]
for system in ('A', 'B'):
    board = img.Board(N, system, 3); closures = {d: board.closure(d) for d in (1, 2, 3)}
    for name, seed, affine, rho in cases:
        rng = random.Random(seed)
        forms = [(aug.half_sets(rng, N, m, affine), rng.getrandbits(1)) for _ in range(rho)]
        for s in (1, 2):
            rec = {'N': N, 'system': system, 'block': name, 'rho': rho, 's': s, 'feasible': img.image_test(board, closures, forms, s)}
            print(json.dumps(rec), flush=True); recs.append(rec)
with open(a.out, 'a') as f:
    for r in recs: f.write(json.dumps(r) + '\n')

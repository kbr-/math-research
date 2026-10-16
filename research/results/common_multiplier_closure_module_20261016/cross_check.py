"""Cross-check of tools/pc_closure.py against tools/f2_closure_degree.cpp on closure dimensions.

Statement tested: for the pigeonhole systems with 3 and 4 pigeons (one fewer hole) and eight random
systems on 5 variables, at every degree D up to 3, both tools agree on whether 1 is in the degree-D
closure and, when it is not, on the closure's dimension.
Expected: agreement everywhere (both implement the same closure convention).
Refuted by: any disagreement in properness or dimension at some system and degree.
Possible because: the two tools index monomials differently (the C++ one omits the constant monomial
from its elimination), so a convention difference would show as a dimension offset.
"""
import argparse
import json
import pathlib
import random
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'tools' / 'tests'))
import pc_closure as pc
from test_pc_closure import php


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    systems = [('php3', *php(3, 2)), ('php4', *php(4, 3))]
    rng = random.Random(11)
    for i in range(8):
        n = 5
        polys = [sorted({rng.randrange(1 << n) for _ in range(rng.randint(1, 3))}) for _ in range(rng.randint(1, 5))]
        systems.append((f'random{i}', [set(p) for p in polys if p], n))
    rows = []
    with tempfile.TemporaryDirectory() as tmp:
        binary = str(pathlib.Path(tmp) / 'fcd')
        subprocess.run(['g++', '-O1', '-o', binary, str(ROOT / 'tools' / 'f2_closure_degree.cpp')], check=True)
        for label, axioms, n in systems:
            path = pathlib.Path(tmp) / 'instance.txt'
            path.write_text(f'{n} {len(axioms)}\n' + ''.join(
                f'{len(p)} ' + ' '.join(map(str, sorted(p))) + '\n' for p in axioms))
            ref = json.loads(subprocess.run([binary, str(path), '3'], check=True, capture_output=True,
                                            text=True).stdout)
            ours = {D: pc.Closure(axioms, n, D) for D in range(0, 4)}
            rows.append(dict(system=label, reference=ref,
                             ours={D: (c.dim if c.proper else None) for D, c in ours.items()}))
            for D, c in ours.items():
                if str(D) in ref['dimensions']:
                    assert c.proper and c.dim == ref['dimensions'][str(D)], (label, D)
                elif ref['degree'] is not None and D >= ref['degree']:
                    assert not c.proper, (label, D)
            print(json.dumps(rows[-1]), flush=True)
    with open(args.out, 'w') as handle:
        json.dump(rows, handle, indent=1)
    print('PASS')


if __name__ == '__main__':
    main()

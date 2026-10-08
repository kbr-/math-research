#!/usr/bin/env python3
"""One falsifying test: three disjoint ANDs, two affine coefficient rows.

The conjecture under test is that exact Boolean normalization cannot beat
constant-row count on independent monomial inputs without high-degree pair
witnesses. This single smallest uncovered case tests that conjecture, not a
hard-system or asymptotic lower bound. Python only emits a tiny SAT instance
and verifies a returned witness; CryptoMiniSat performs the search.
"""
import argparse
import itertools
import json
from pathlib import Path
import subprocess
import time

parser = argparse.ArgumentParser()
parser.add_argument('--out', type=Path, required=True)
args = parser.parse_args()
args.out.mkdir(parents=True, exist_ok=True)
points = list(itertools.product((0, 1), repeat=6))
coefficient_count = 2 * 3 * 7
last_var = coefficient_count
clauses = []

def xor_clauses(a, b, c):
    return [[-a, -b, -c], [a, b, -c], [a, -b, c], [-a, b, c]]

for a, b, c in itertools.product((0, 1), repeat=3):
    assignment = {1: a, 2: b, 3: c}
    satisfied = all(any(assignment[abs(lit)] == (lit > 0) for lit in clause)
                    for clause in xor_clauses(1, 2, 3))
    assert satisfied == (c == (a ^ b))

def coeff_id(row, inp, feature):
    return row * 21 + inp * 7 + feature + 1

def parity_variable(variables):
    global last_var
    assert variables
    current = variables[0]
    for other in variables[1:]:
        last_var += 1
        clauses.extend(xor_clauses(current, other, last_var))
        current = last_var
    return current

active = 0
for point in points:
    inputs = [point[2*i] * point[2*i+1] for i in range(3)]
    if not any(inputs):
        continue
    active += 1
    features = (1,) + point
    outputs = []
    for row in range(2):
        variables = [coeff_id(row, i, j) for i, g in enumerate(inputs) if g
                     for j, feature in enumerate(features) if feature]
        outputs.append(parity_variable(variables))
    clauses.append(outputs)
assert active == 37 and last_var < 2000 and len(clauses) < 8000
instance = args.out / 'instance.cnf'
instance.write_text(f'p cnf {last_var} {len(clauses)}\n' +
                    ''.join(' '.join(map(str, c)) + ' 0\n' for c in clauses))
print(json.dumps({'coefficient_bits': coefficient_count, 'active_points': active,
                  'variables': last_var, 'clauses': len(clauses)}), flush=True)
started = time.monotonic()
run = subprocess.run(['cryptominisat5', '--threads', '1', '--maxtime', '45',
                      '--random', '0', '--verb', '1', str(instance)],
                     text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                     timeout=50)
(args.out / 'solver.txt').write_text(run.stdout)
result = {'solver_exit': run.returncode, 'elapsed_seconds': time.monotonic()-started,
          'variables': last_var, 'clauses': len(clauses), 'active_points': active}
if 's SATISFIABLE' in run.stdout:
    model = {}
    for line in run.stdout.splitlines():
        if line.startswith('v '):
            for literal in map(int, line[2:].split()):
                if literal:
                    model[abs(literal)] = int(literal > 0)
    assert all(any(model[abs(lit)] == (lit > 0) for lit in c) for c in clauses)
    coefficients = [[[model[coeff_id(row, i, j)] for j in range(7)]
                     for i in range(3)] for row in range(2)]
    verification = []
    for point in points:
        features = (1,) + point
        inputs = [point[2*i]*point[2*i+1] for i in range(3)]
        maps = [[sum(c*f for c, f in zip(vector, features)) % 2
                 for vector in row] for row in coefficients]
        values = [sum(a*g for a, g in zip(row, inputs)) % 2 for row in maps]
        prefix = (1-values[0])*(1-values[1])
        assert all(g*prefix == 0 for g in inputs)
        verification.append({'point': point, 'inputs': inputs,
                             'coefficient_values': maps, 'rows': values,
                             'prefix': prefix})
    result.update(status='SAT', coefficients=coefficients, verification=verification)
    print('SAT: all 64 old assignments and all CNF clauses independently verified')
    print(json.dumps(coefficients))
elif 's UNSATISFIABLE' in run.stdout:
    result.update(status='UNSAT', scope='native solver verdict; no independent proof checker installed')
    print('UNSAT: native solver verdict, not a universal theorem')
else:
    result.update(status='UNKNOWN')
    print('UNKNOWN: bounded test did not decide')
(args.out / 'result.json').write_text(json.dumps(result, indent=2)+'\n')
assert run.returncode in (0, 10, 20, 15), (run.returncode, run.stdout[-2000:])
print('Completed single test; solver output and result retained')

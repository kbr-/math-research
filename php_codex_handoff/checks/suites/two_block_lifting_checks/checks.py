"""Exact tests for supported-coefficient lifting over F_2.

All polynomials are stored in the Boolean quotient.  Each axiom separately
retains its ORIGINAL ordinary polynomial degree, which determines the allowed
cofactor degree.  Quotient representation does not lower that degree budget.

Linear algebra: NumPy-vectorized exact GF(2) elimination (no floating point).
Independent cases: ProcessPoolExecutor.  Run: python checks.py
"""
from __future__ import annotations
from concurrent.futures import ProcessPoolExecutor
from functools import lru_cache
from itertools import combinations
from pathlib import Path
import json
import time
import numpy as np

@lru_cache(maxsize=None)
def basis(n: int, d: int) -> tuple[int, ...]:
    if d < 0:
        return ()
    return tuple(sum(1 << i for i in ids)
                 for k in range(min(n, d) + 1)
                 for ids in combinations(range(n), k))


def poly(*terms: int) -> np.ndarray:
    if not terms:
        return np.empty(0, dtype=np.int64)
    vals, counts = np.unique(np.asarray(terms, dtype=np.int64), return_counts=True)
    return vals[counts % 2 == 1]


def add(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return poly(*np.concatenate((a, b)).tolist())


def mul(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    if not len(a) or not len(b):
        return np.empty(0, dtype=np.int64)
    vals, counts = np.unique(np.bitwise_or(a[:, None], b[None, :]), return_counts=True)
    return vals[counts % 2 == 1]


def times_mon(a: np.ndarray, q: int) -> np.ndarray:
    vals, counts = np.unique(np.bitwise_or(a, q), return_counts=True)
    return vals[counts % 2 == 1]


def deg(a: np.ndarray) -> int:
    return max((int(v).bit_count() for v in a), default=-1)


def solve_gf2(rows: list[np.ndarray], rhs: list[int], width: int,
              rng: np.random.Generator) -> tuple[np.ndarray, int]:
    """RREF with vectorized XOR row updates, randomized free variables."""
    if not rows:
        return rng.integers(0, 2, size=width, dtype=np.uint8), 0
    a0 = np.stack(rows).astype(np.uint8, copy=False)
    b0 = np.asarray(rhs, dtype=np.uint8)
    mat = np.column_stack((a0, b0))
    pivots = []
    r = 0
    for c in range(width):
        poss = np.flatnonzero(mat[r:, c])
        if not len(poss):
            continue
        j = r + int(poss[0])
        if j != r:
            mat[[r, j]] = mat[[j, r]]
        affected = np.flatnonzero(mat[:, c])
        affected = affected[affected != r]
        mat[affected, c:] ^= mat[r, c:]
        pivots.append(c)
        r += 1
        if r == len(mat):
            break
    if np.any(mat[r:, -1]):
        raise ValueError('inconsistent exact GF(2) moment system')
    x = rng.integers(0, 2, size=width, dtype=np.uint8)
    if pivots:
        piv = np.asarray(pivots, dtype=np.int64)
        x[piv] = 0
        x[piv] = mat[:r, -1] ^ ((mat[:r, :-1].astype(np.uint32) @ x.astype(np.uint32)) & 1).astype(np.uint8)
    assert np.array_equal((a0.astype(np.uint32) @ x.astype(np.uint32)) & 1, b0)
    return x, r


def consequence_rows(n: int, d: int, axioms: list[tuple[np.ndarray, int]],
                     ids: dict[int, int], width: int, offset: int = 0):
    for f, original_degree in axioms:
        for q in basis(n, d - original_degree):
            f_q = times_mon(f, q)
            row = np.zeros(width, dtype=np.uint8)
            for m in f_q:
                row[offset + ids[int(m)]] ^= 1
            yield row


def moment_seed(n: int, d: int, axioms: list[tuple[np.ndarray, int]],
                rng: np.random.Generator) -> np.ndarray:
    bs = basis(n, d)
    ids = {m: i for i, m in enumerate(bs)}
    rows = list(consequence_rows(n, d, axioms, ids, len(bs)))
    rhs = [0] * len(rows)
    root = np.zeros(len(bs), dtype=np.uint8)
    root[ids[0]] = 1
    rows.append(root); rhs.append(1)
    x, _ = solve_gf2(rows, rhs, len(bs), rng)
    values = np.full(1 << n, 255, dtype=np.uint8)
    values[np.asarray(bs, dtype=np.int64)] = x
    return values


def eval_poly(values: np.ndarray, f: np.ndarray) -> int:
    assert np.all(values[f] != 255), 'functional used outside its domain'
    return int(np.bitwise_xor.reduce(values[f], initial=np.uint8(0)))


def inflation(d: int, h: int, delta: int) -> int:
    return max(d, 2 * d - h * (delta + 2))


def lift(n: int, d: int, h: int, inputs: list[np.ndarray],
         old_axioms: list[tuple[np.ndarray, int]], old_values: np.ndarray,
         rng: np.random.Generator):
    """Actual supported-coefficient construction, not just feasibility testing."""
    k = len(inputs)
    delta = max(deg(g) for g in inputs)
    degrees = [deg(g) for g in inputs]
    e = [a + h * (delta + 1) if a >= 0 else 10**9 for a in degrees]
    active = [i for i in range(k) if e[i] <= d]
    mon_spaces = {j: basis(n, d - h + degrees[j]) for j in active}
    ids = {j: {m: i for i, m in enumerate(mon_spaces[j])} for j in active}
    offsets = {}; width = 0
    for j in active:
        offsets[j] = width
        width += len(mon_spaces[j])
    rows = []; rhs = []
    for j in active:
        nj = d - h + degrees[j]
        rr = list(consequence_rows(n, nj, old_axioms, ids[j], width, offsets[j]))
        rows.extend(rr); rhs.extend([0] * len(rr))
    for i in active:
        for q in basis(n, d - e[i]):
            G = times_mon(inputs[i], q)
            row = np.zeros(width, dtype=np.uint8)
            for j in active:
                for mon in mul(G, inputs[j]):
                    row[offsets[j] + ids[j][int(mon)]] ^= 1
            rows.append(row); rhs.append(eval_poly(old_values, G))
    coeffs, rank = solve_gf2(rows, rhs, width, rng)
    components = {}
    for j in active:
        v = np.full(1 << n, 255, dtype=np.uint8)
        v[np.asarray(mon_spaces[j], dtype=np.int64)] = coeffs[offsets[j]:offsets[j] + len(mon_spaces[j])]
        components[j] = v
    total_n = n + h*k
    bs = np.asarray(basis(total_n, d), dtype=np.int64)
    old_mask = (1 << n) - 1
    old_parts = bs & old_mask
    new_parts = bs ^ old_parts
    result = np.full(1 << total_n, 255, dtype=np.uint8)
    vals = np.zeros(len(bs), dtype=np.uint8)
    old_only = new_parts == 0
    vals[old_only] = old_values[old_parts[old_only]]
    assert np.all(vals[old_only] != 255)
    for j in active:
        diagonal = sum(1 << (n + u*k + j) for u in range(h))
        selected = np.flatnonzero(new_parts == diagonal)
        if len(selected):
            terms = np.bitwise_or(old_parts[selected, None], inputs[j][None, :])
            got = components[j][terms]
            assert np.all(got != 255)
            vals[selected] ^= np.bitwise_xor.reduce(got, axis=1)
    result[bs] = vals
    extension_axioms = []
    product = poly(0)
    for u in range(h):
        factor = poly(0)
        for j, g in enumerate(inputs):
            factor = add(factor, times_mon(g, 1 << (n + u*k + j)))
        product = mul(product, factor)
    for i, g in enumerate(inputs):
        if len(g):
            extension_axioms.append((mul(g, product), e[i]))
    return total_n, old_axioms + extension_axioms, result, {
        'component_unknowns': width, 'component_equations': len(rows),
        'component_rank': rank, 'active_companions': len(active),
    }


def validate(n: int, d: int, axioms, values) -> int:
    assert int(values[0]) == 1
    total = 0
    for f, original_degree in axioms:
        qq = basis(n, d - original_degree)
        if not qq:
            continue
        masks = np.bitwise_or(np.asarray(qq, dtype=np.int64)[:, None], f[None, :])
        got = values[masks]
        assert np.all(got != 255)
        checks = np.bitwise_xor.reduce(got, axis=1)
        assert not np.any(checks), f'annihilation failed at degree {original_degree}'
        total += len(qq)
    return total


def make_inputs(n: int, k: int, delta: int, rng):
    inputs = []
    for j in range(k):
        if delta == 0:
            inputs.append(poly(0))
            continue
        terms = rng.choice(np.asarray(basis(n, delta), dtype=np.int64),
                           size=min(5, len(basis(n, delta))), replace=False)
        leading = sum(1 << i for i in range(delta))
        if not any(int(m).bit_count() == delta for m in terms):
            terms = np.append(terms, leading)
        inputs.append(poly(*terms.tolist()))
    return inputs


def case(spec):
    start = time.perf_counter()
    seed, h, delta, k, kind = spec
    rng = np.random.default_rng(seed)
    n = 4 if kind == 'unsatisfiable' else 3
    if kind == 'unsatisfiable':
        # x0=1, xi => x(i+1), x3=0.  Unsatisfiable, with a degree-2 design.
        axioms = [(poly(0, 1), 1), (poly(1 << (n-1)), 1)]
        axioms += [(poly(1 << i, (1 << i) | (1 << (i+1))), 2) for i in range(n-1)]
    else:
        # Satisfiable but nontrivial row-normalization / exclusivity identities.
        axioms = [(poly(0, 1, 2), 1), (poly(3), 2)]
    gA = make_inputs(n, k, delta, rng)
    gB = make_inputs(n, k, delta, rng)
    d = h * (delta + 2) + delta  # first complete-group interaction degree
    if kind == 'unsatisfiable':
        assert h == 1 and delta == 0
        d = 2
    d1 = inflation(d, h, delta)
    b = inflation(d1, h, delta)
    original_values = moment_seed(n, b, axioms, rng)
    n1, f1, v1, stats1 = lift(n, d1, h, gA, axioms, original_values, rng)
    c1 = validate(n1, d1, f1, v1)
    n2, f2, v2, stats2 = lift(n1, d, h, gB, f1, v1, rng)
    c2 = validate(n2, d, f2, v2)
    for mon in basis(n, d):
        assert v2[mon] == original_values[mon], 'old moments changed'
    # Explicit same-block and cross-block full-group cofactors.
    full_group_checks = 0
    for block, offset in enumerate((n, n1)):
        for j in range(k):
            q = sum(1 << (offset + u*k + j) for u in range(h))
            for f, original_degree in f2[len(axioms):]:
                if original_degree + h <= d:
                    assert eval_poly(v2, times_mon(f, q)) == 0
                    full_group_checks += 1
    assignments = np.arange(1 << n, dtype=np.int64)
    satisfies = np.ones(len(assignments), dtype=bool)
    for f, _ in axioms:
        v = ((assignments[:, None] & f[None, :]) == f[None, :]).astype(np.uint8)
        satisfies &= np.bitwise_xor.reduce(v, axis=1) == 0
    if kind == 'unsatisfiable':
        assert not np.any(satisfies), 'base unexpectedly satisfiable'
    return {
        'seed': seed, 'h': h, 'input_degree': delta, 'fan_in_per_block': k,
        'base_kind': kind, 'base_satisfying_assignments': int(satisfies.sum()),
        'target_degree': d, 'intermediate_degree': d1, 'base_degree': b,
        'two_block_expected_first_layer_budget': d + 3*delta,
        'number_of_blocks': 2, 'ordinary_cofactor_checks': c1+c2,
        'explicit_complete_group_checks': full_group_checks,
        'first_lift': stats1, 'second_lift': stats2,
        'passed': True, 'seconds': round(time.perf_counter()-start, 3),
    }


def old_construction_boundary_control():
    # Two constant-input blocks, h=2, in F_2; polynomial R_A E_B.
    # Lambda_old = eval_0 + top_A + top_B omits the mixed correction.
    R_A = poly(0b0011)
    E_B = mul(poly(0, 0b0100), poly(0, 0b1000))
    target = mul(R_A, E_B)
    vals = {0: 1, 0b0011: 1, 0b1100: 1}
    got = sum(vals.get(int(m), 0) for m in target) % 2
    assert got == 1
    return {'old_single_correction_formula_rejected': True,
            'nonzero_value_on_R_A_E_B': got}


def main():
    specs = []
    counter = 0
    for h, delta, k in [(1,1,2), (1,1,3), (1,2,2), (1,2,3), (2,1,2), (2,2,2)]:
        for repeat in range(3):
            counter += 1
            specs.append((5000+counter,h,delta,k,'satisfiable'))
    for repeat in range(4):
        specs.append((6000+repeat,1,0,2,'unsatisfiable'))
    specs.append((7000,2,0,1,'satisfiable'))
    with ProcessPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(case, specs))
    report = {
        'field': 'F_2', 'method': 'vectorized exact GF(2) elimination',
        'parallel_workers': 4, 'cases': len(results),
        'total_cofactor_checks': sum(r['ordinary_cofactor_checks'] for r in results),
        'total_explicit_complete_group_checks': sum(r['explicit_complete_group_checks'] for r in results),
        'unsatisfiable_base_cases': sum(r['base_kind']=='unsatisfiable' for r in results),
        'boundary_control': old_construction_boundary_control(), 'results': results,
    }
    out = Path(__file__).with_name('results.json')
    out.write_text(json.dumps(report, indent=2))
    print(json.dumps({k:v for k,v in report.items() if k!='results'}, indent=2))
    print('All cases passed; report:', out)

if __name__ == '__main__':
    main()

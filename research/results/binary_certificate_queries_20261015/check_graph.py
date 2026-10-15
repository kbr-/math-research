#!/usr/bin/env python3
"""Check the complete used/distinct coefficient-query sequent construction.

Stages: build the symbolic-Q schema and actual run-polynomial formulas at
n=1,3; validate every inference and ancestor; verify the two input-prefix
factors and original input-label occurrence; test changed rule and input
order controls; save complete graphs and the finite query table.
These tiny syntax graphs and free-word supports run in seconds in Python;
there is no numerical rank kernel. The all-n claim has a symbolic proof.
Expected: every accepted graph has exactly 22 used/distinct nodes and the
selected input is node2, preceded by B_z and B_z Q; the actual query table
equals MOD3. The changed-rule graph fails and the valid reordered graph
has zero at the chosen nonempty-word query.
Refuted by: a bad inference, repeated or unused node, wrong prefix, extra
selected input occurrence, wrong query bit, or a control matching the claim.
Possible because: cedent ordering controls which side holds the guard, and
moving the input before the weakened identity removes the Q contribution.
"""
import argparse
import copy
import importlib.util
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location(
    "query_sequent_api", ROOT / "research/results/binary_powered_prefix_20261015/check_graph.py")
OLD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(OLD)
API = OLD.API
ONE = frozenset({()})


def run_formula(f, x0, x1, n):
    zero = f.neg(f.put("or"))

    def binary_sum(args):
        args = tuple(args)
        if len(args) % 2 == 0:
            args += (zero,)
        return f.put("xor", args)

    a, b = f.neg(x0), f.neg(x1)
    zsum = binary_sum(f.put("or", (a,) * j) for j in range(n + 1))
    return binary_sum(f.put("or", (zsum,) + (b, zsum) * (3 * t))
                      for t in range(n // 3 + 1))


def build(n=None):
    f = API.Formulas()
    z = f.put("var", ("z",))  # fixed cedent order puts this before the macro
    if n is None:
        q = f.put("var", ("q",))
        old = (z, q)
        macro = f.neg(q)
    else:
        xs = tuple(f.put("var", (f"x{i}",)) for i in range(n + 1))
        old = (z,) + xs
        macro = run_formula(f, xs[0], xs[1], n)
    nz = f.neg(z)
    p = API.Proof(f, (z, nz) + old[1:])
    identity = p.add("axiom", (z,), (z,), arg=z)
    weakened = p.weak(identity, macro)
    selected = p.add("input", right=(z,), arg=z)
    lifted = p.add("neg", right=(z, macro, nz), premises=(weakened,), arg=z)
    root, _ = OLD.make_or(p, lifted, (z, nz, macro))
    tautology = f.put("or", (z, nz, macro))
    zeta = f.neg(f.put("xor"))
    zr = p.add("empty_parity", right=(zeta,))
    left = p.weak(p.weak(root, zeta), f.neg(zeta))
    right = p.weak(p.weak(zr, f.neg(tautology)), f.neg(zeta))
    joined = p.add("cut", right=(zeta, f.neg(zeta)), premises=(left, right), arg=tautology)
    sr, _ = OLD.make_or(p, joined, (zeta, f.neg(zeta)))
    sigma = f.put("or", (zeta, f.neg(zeta)))
    eta = f.neg(sigma)
    negative = p.add("input", right=(nz,), arg=nz)
    first = p.weak(selected, eta)
    second = p.weak(negative, eta)
    contextual = p.add("cut", right=(eta,), premises=(first, second), arg=z)
    p.add("cut", premises=(sr, contextual), arg=sigma)
    p.validate()
    assert len(p.nodes) == 22 and selected == 2
    assert sum(node["rule"] == "input" and node["arg"] == z for node in p.nodes) == 1
    guard = frozenset({(z,), (z, z)})
    qpoly = f.poly(macro)
    assert all(z not in word for word in qpoly)
    assert p.line_poly(0) == guard
    assert p.line_poly(1) == f.mul(guard, qpoly)
    prefix = f.mul(ONE ^ p.line_poly(0), ONE ^ p.line_poly(1))
    assert f.poly(zeta) == frozenset() and f.poly(sigma) == frozenset()
    assert f.poly(eta) == ONE and p.line_poly(len(p.nodes) - 1) == ONE

    # A malformed rule must be rejected independently of the target polynomial.
    bad = copy.copy(p); bad.nodes = copy.deepcopy(p.nodes)
    bad.nodes[-1]["arg"] = z
    assert not bad.valid_rule(len(bad.nodes) - 1)

    # This is a legal different ordering, not a malformed graph. Its selected
    # input prefix lacks Q, so the query changes even though the proof still works.
    order = [0, 2, 1] + list(range(3, len(p.nodes)))
    remap = {before: after for after, before in enumerate(order)}
    alternate = copy.copy(p)
    alternate.nodes = [dict(p.nodes[i], premises=tuple(remap[j] for j in p.nodes[i]["premises"]))
                       for i in order]
    alternate.validate()
    alternate_prefix = ONE ^ alternate.line_poly(0)
    if n is None:
        control_word = (old[1],)
        queries = [(control_word, 1)]
    else:
        control_word = (old[1],) * n
        queries = [(tuple(old[1 + bit] for bit in bits), int(sum(bits) % 3 == 0))
                   for bits in itertools.product((0, 1), repeat=n)]
    assert (z,) + control_word in prefix and (z,) + control_word not in alternate_prefix
    table = []
    for word, expected in queries:
        actual = int((z,) + word in prefix)
        assert actual == expected
        table.append({"word": list(word), "expected": expected, "actual": actual})
    return {"n": n, "nodes": p.nodes, "formulas": f.rows, "inputs": p.inputs,
            "old_variables": old, "selected_input_node": selected,
            "node_count": len(p.nodes), "symbols": p.symbols(), "depth": p.depth(),
            "original_clause_labels": len(p.inputs), "boolean_labels": len(old),
            "commutator_labels": len(old) * (len(old) - 1) // 2,
            "prefix_words": sorted(prefix), "query_table": table,
            "reordered_nodes": alternate.nodes,
            "controls": {"changed_cut_rejected": True, "valid_order_changes_query": True}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    rows = [build(), build(1), build(3)]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(rows, indent=2) + "\n")
    for row in rows:
        print(json.dumps({key: row[key] for key in ("n", "node_count", "symbols", "depth",
              "original_clause_labels", "boolean_labels", "commutator_labels", "controls")}))
    count = sum(len(row["query_table"]) for row in rows)
    assert count == 11
    print(f"PASS: {len(rows)} complete graphs, {sum(row['node_count'] for row in rows)} checked nodes, "
          f"{count} query checks, {2 * len(rows)} negative controls")


if __name__ == "__main__":
    main()

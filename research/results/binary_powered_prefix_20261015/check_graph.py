#!/usr/bin/env python3
"""Check the new powered-seed/zero-context graph construction in full.

Stages: build two existing small source fixtures (not their old transforms),
build the new graph at q4/8, validate every rule, ancestry and distinct cedent,
check every powered/zero line and all old reference prefixes; save full graphs.
The old immutable checker supplies the syntax API; its run() is never invoked.
Python controls small graphs and tiny free-word polynomials: each powered
line is a one-variable B^j with j<=7, not a large polynomial/rank kernel.
Expected: every new graph/property passes; three changed controls fail.
Refuted by: Any invalid rule, repeated or unused node, wrong power, nonzero
bridge line, missing preceding mask or changed original contextual polynomial.
Possible because: Bridge contexts and old reference indices can lose a premise,
and a logically valid excluded middle need not have literal-zero translation.
"""
import argparse
import copy
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "research/results/binary_used_tag_image_20261012/check_graph.py"
SPEC = importlib.util.spec_from_file_location("old_graph_syntax", SOURCE)
API = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(API)


def excluded_middle(p, a):
    f, empty = p.f, p.f.put("or")
    na = f.neg(a)
    ids = [p.add("axiom", (a,), (a,), arg=a)]
    ids.append(p.add("neg", right=(na, a), premises=(ids[-1],), arg=a))
    ids.append(p.weak(ids[-1], empty))
    ids.append(p.add("or_right", right=(na, f.put("or", (a,))),
                     premises=(ids[-1],), arg=(a,)))
    tag = f.put("or", (na, a))
    ids.append(p.add("or_right", right=(tag,), premises=(ids[-1],), arg=(na, a)))
    return ids[-1], tag, ids


def make_or(p, parent, args):
    """Group an existing flat right list by the actual tail OR-right rule."""
    f = p.f
    current = p.weak(parent, f.put("or"))
    ids = [current]
    for j in reversed(range(len(args))):
        tail = f.put("or", args[j:])
        right = list(p.nodes[current]["right"])
        right.remove(args[j])
        right.remove(f.put("or", args[j + 1:]))
        current = p.add("or_right", right=right + [tail], premises=(current,), arg=args[j:])
        ids.append(current)
    return current, ids


def transform(old, q):
    f, size = old.f, old.symbols()
    p = API.Proof(f, old.inputs)
    variables = [i for i, (op, _) in enumerate(f.rows) if op == "var"]
    e = q - 1
    assert q in (4, 8) and e <= 7
    roots, tags, etas, powered, zero_nodes, mask_roots = [], [], [], [], [], []
    for j, x in enumerate(variables):
        parity = f.put("xor", (variables[0],) * (2 * (size + q + len(variables) + j + 1)))
        zr, zeta, zids = excluded_middle(p, parity)
        zero_nodes.extend(zids)
        # New syntax larger than every old formula, but t(a)=t(x).
        a = f.put("or", (x, f.neg(zeta)))
        assert f.size(a) > size and f.poly(a) == f.poly(x)
        pr, inner, pids = excluded_middle(p, a)
        powered.extend((i, x, 1) for i in pids)
        for k in range(2, e + 1):
            pr = p.weak(pr, inner)
            powered.append((pr, x, k))
        pr, pids = make_or(p, pr, (inner,) * e)
        powered.extend((i, x, e) for i in pids)
        tau = f.put("or", (inner,) * e)
        mask_roots.append(pr)
        # Consume the powered root in a literally zero context, without
        # repeating the already proved cedent ->zeta.
        left = p.weak(pr, zeta)
        left = p.weak(left, f.neg(zeta))
        right = p.weak(zr, f.neg(tau))
        right = p.weak(right, f.neg(zeta))
        cut = p.add("cut", right=(zeta, f.neg(zeta)), premises=(left, right), arg=tau)
        zero_nodes.extend((left - 1, left, right - 1, right, cut))
        root, zids = make_or(p, cut, (zeta, f.neg(zeta)))
        zero_nodes.extend(zids)
        sigma = f.put("or", (zeta, f.neg(zeta)))
        roots.append(root)
        tags.append(sigma)
        etas.append(f.neg(sigma))
    seed_end = len(p.nodes)
    mapping = {}
    inputs = [i for i, n in enumerate(old.nodes) if n["rule"] == "input"]
    for i in inputs:
        a = old.nodes[i]["arg"]
        mapping[i] = p.add("input", right=(a,), arg=a)
    round_ends = [len(p.nodes)]
    for eta in etas:
        for i in inputs:
            mapping[i] = p.weak(mapping[i], eta)
        round_ends.append(len(p.nodes))
    prefix_end = len(p.nodes)
    for i, n in enumerate(old.nodes):
        if n["rule"] == "input":
            continue
        if not n["premises"]:
            current = p.add(n["rule"], n["left"], n["right"], arg=n["arg"])
            for eta in etas:
                current = p.weak(current, eta)
        else:
            current = p.add(n["rule"], n["left"], n["right"] + tuple(etas),
                            tuple(mapping[j] for j in n["premises"]), n["arg"])
        mapping[i] = current
    final = mapping[len(old.nodes) - 1]
    current = final
    for j in reversed(range(len(tags))):
        root = roots[j]
        for eta in etas[:j]:
            root = p.weak(root, eta)
        current = p.add("cut", right=etas[:j], premises=(root, current), arg=tags[j])
    p.validate()
    one = frozenset({()})
    for i, x, k in powered:
        b = frozenset({(x,), (x, x)})
        value = one
        for _ in range(k):
            value = f.mul(value, b)
        assert p.line_poly(i) == value
    assert all(p.line_poly(i) == frozenset() for i in zero_nodes)
    assert all(f.poly(tag) == frozenset() for tag in tags)
    assert all(p.line_poly(mapping[i]) == old.line_poly(i) for i in range(len(old.nodes)))
    assert p.line_poly(final) == one
    for i in range(final + 1, len(p.nodes)):
        expected = one if p.nodes[i]["rule"] == "cut" else frozenset()
        assert p.line_poly(i) == expected
    for i in range(prefix_end, final + 1):
        for parent in p.nodes[i]["premises"]:
            assert parent >= seed_end
            assert sum(end <= parent for end in round_ends) >= len(etas)
    assert p.depth() <= max(old.depth(), 9)
    return p, {"q": q, "e": e, "S": size, "seed_end": seed_end,
               "prefix_end": prefix_end, "contextual_final": final,
               "round_ends": round_ends, "mask_roots": mask_roots,
               "powered_lines": powered, "zero_nodes": zero_nodes}


def run(out):
    cases, controls = [], []
    for kind in ("units", "or_cut"):
        for q in (4, 8):
            old, x = API.original(kind)
            p, meta = transform(old, q)
            bad = copy.copy(p)
            bad.nodes = copy.deepcopy(p.nodes)
            assert bad.nodes[-1]["arg"] != x
            bad.nodes[-1]["arg"] = x
            API.must_fail(bad.validate)
            bad = copy.copy(p)
            bad.nodes = copy.deepcopy(p.nodes)
            fresh = p.f.put("xor", (x,) * (2 * (meta["S"] + q + 100)))
            extra = {"rule": "axiom", "left": (fresh,), "right": (fresh,),
                     "premises": (), "arg": fresh}
            bad.nodes.insert(len(bad.nodes) - 1, extra)
            assert bad.valid_rule(len(bad.nodes) - 2)
            API.must_fail(bad.validate)
            odd = p.f.put("xor", (x,) * (2 * (meta["S"] + q + 200) + 1))
            zeta = p.f.put("or", (p.f.neg(odd), odd))
            sigma = p.f.put("or", (zeta, p.f.neg(zeta)))
            assert p.f.poly(sigma) != frozenset()
            controls.append({"kind": kind, "q": q, "bad_cut": True,
                             "valid_unused_node": True, "nonzero_bridge_tag": True})
            cases.append({"kind": kind, **meta, "nodes": len(p.nodes),
                          "symbols": p.symbols(), "depth": p.depth(),
                          "original_nodes": old.nodes, "inputs": p.inputs,
                          "formulas": p.f.rows, "proof": p.nodes})
    result = {"passed": True, "case_count": len(cases), "cases": cases,
              "control_count": 3 * len(controls), "controls": controls}
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"passed": True, "cases": len(cases),
                      "negative_controls": result["control_count"],
                      "nodes_checked": sum(c["nodes"] for c in cases),
                      "sizes": [{k: c[k] for k in ("kind", "q", "nodes", "symbols", "depth")}
                                for c in cases]}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    run(parser.parse_args().out)

#!/usr/bin/env python3
"""Check the actual commutativity-square block in the audited sequent rules.

Stages: build three fixed order/grouping variants; prune unused construction
nodes; validate every rule and ancestry; check the free root polynomial;
integrate fresh paired blocks into two complete source fixtures; save full
graphs and GAP data for independent algebra/prefix checks.
Small syntax graphs and degree-at-most-four word polynomials run in seconds;
this is not a numerical matrix kernel. No old computation series is rerun.
Expected: all three blocks prove a root of falsity (XY+YX)^2, with all nodes
used; both integrated refutations preserve the original translations and full
preceding masks. Altered parity and cut rules are rejected.
Matrix expectations are in check.g; its unchanged local grid is not rerun.
Refuted by: any wrong rule, unused node, different free root or accepted bad parity.
Possible because: parity-tail syntax includes an empty XOR and cannot be
identified with its argument without actual inference nodes.
"""
import argparse
import copy
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location(
    "powered_syntax", ROOT / "research/results/binary_powered_prefix_20261015/check_graph.py")
OLD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(OLD)
API = OLD.API


class Block(API.Proof):
    def add(self, rule, left=(), right=(), premises=(), arg=None):
        key = API.seq(left, right)
        if key in self.seen:
            return next(i for i, node in enumerate(self.nodes)
                        if API.seq(node["left"], node["right"]) == key)
        return super().add(rule, left, right, premises, arg)

    def left_weak(self, parent, a):
        node = self.nodes[parent]
        return self.add("left_weak", node["left"] + (a,), node["right"], (parent,), a)

    def valid_rule(self, i):
        node, f = self.nodes[i], self.f
        if any(j >= i or j < 0 for j in node["premises"]):
            return False
        ps = [self.nodes[j] for j in node["premises"]]
        rule, a = node["rule"], node["arg"]
        out = API.seq(node["left"], node["right"])
        if rule == "left_weak":
            return len(ps) == 1 and out == API.seq(ps[0]["left"] + (a,), ps[0]["right"])
        if rule == "neg_left":
            if len(ps) != 1 or a not in ps[0]["right"]:
                return False
            right = list(ps[0]["right"]); right.remove(a)
            return out == API.seq(ps[0]["left"] + (f.neg(a),), right)
        if rule in ("parity_left", "parity_right"):
            if len(ps) != 2 or not a:
                return False
            first, tail = a[0], f.put("xor", a[1:])
            lefts = [list(p["left"]) for p in ps]
            rights = [list(p["right"]) for p in ps]
            try:
                if rule == "parity_left":
                    lefts[0].remove(first); lefts[0].remove(f.neg(tail))
                    lefts[1].remove(tail); rights[1].remove(first)
                    expected = API.seq(lefts[0] + [f.put("xor", a)], rights[0])
                else:
                    lefts[0].remove(first); rights[0].remove(f.neg(tail))
                    rights[1].remove(first); rights[1].remove(tail)
                    expected = API.seq(lefts[0], rights[0] + [f.put("xor", a)])
            except ValueError:
                return False
            return (API.seq(lefts[0], rights[0]) == API.seq(lefts[1], rights[1])
                    and out == expected)
        return super().valid_rule(i)

    def prune(self, root):
        used, todo = set(), [root]
        while todo:
            i = todo.pop()
            if i not in used:
                used.add(i); todo.extend(self.nodes[i]["premises"])
        order = sorted(used)
        remap = {old: new for new, old in enumerate(order)}
        self.nodes = [dict(self.nodes[i], premises=tuple(remap[j] for j in self.nodes[i]["premises"]))
                      for i in order]
        self.seen = {API.seq(n["left"], n["right"]) for n in self.nodes}
        assert remap[root] == len(self.nodes) - 1
        return remap

    def validate_block(self, root_formula):
        assert API.seq(self.nodes[-1]["left"], self.nodes[-1]["right"]) == API.seq((), (root_formula,))
        assert len(self.seen) == len(self.nodes)
        assert all(self.valid_rule(i) for i in range(len(self.nodes)))
        reached, todo = set(), [len(self.nodes) - 1]
        while todo:
            i = todo.pop()
            if i not in reached:
                reached.add(i); todo.extend(self.nodes[i]["premises"])
        assert len(reached) == len(self.nodes)


def make_or_context(p, parent, args):
    """Tail grouping with both contexts preserved; the older helper was one-sided."""
    current = p.weak(parent, p.f.put("or"))
    ids = [current]
    for j in reversed(range(len(args))):
        node = p.nodes[current]
        right = list(node["right"])
        right.remove(args[j]); right.remove(p.f.put("or", args[j + 1:]))
        current = p.add("or_right", left=node["left"],
                        right=right + [p.f.put("or", args[j:])],
                        premises=(current,), arg=args[j:])
        ids.append(current)
    return current, ids


def or_implication(p, source, target):
    f, empty = p.f, p.f.put("or")
    target_formula = f.put("or", target)
    leaves = []
    for literal in source:
        current = p.add("axiom", (literal,), (literal,), arg=literal)
        remaining = list(target); remaining.remove(literal)
        for other in remaining:
            current = p.weak(current, other)
        current, _ = make_or_context(p, current, target)
        leaves.append(current)
    current = p.add("false", (empty,))
    current = p.weak(current, target_formula)
    for k in reversed(range(len(source))):
        args = source[k:]
        current = p.add("or_left", (f.put("or", args),), (target_formula,),
                        (leaves[k], current), args)
    return current


def append_block(p, u, v, variant="forward_order"):
    f = p.f
    a, b, q = f.put("or", (u, v)), f.put("or", (v, u)), f.put("xor")
    if variant == "reverse_order":
        ba = or_implication(p, (v, u), (u, v))
        ab = or_implication(p, (u, v), (v, u))
    else:
        ab = or_implication(p, (u, v), (v, u))
        ba = or_implication(p, (v, u), (u, v))
    tail = f.put("xor", (b,))
    # A -> XOR(B), Q, by the source's unary parity-right rule.
    z = p.add("empty_parity", right=(f.neg(q),))
    z = p.left_weak(p.left_weak(z, b), a)
    z = p.weak(z, q)
    w = p.weak(p.weak(ab, q), q)
    forward = p.add("parity_right", (a,), (tail, q), (z, w), (b,))
    # XOR(B) -> A, Q. Keeping the false Q in the right context avoids
    # assuming a syntactic unary-XOR or double-negation simplification.
    z = p.weak(p.left_weak(ba, f.neg(q)), q)
    w = p.add("axiom", (q,), (q,), arg=q)
    w = p.weak(p.weak(w, a), b)
    backward = p.add("parity_left", (tail,), (a, q), (z, w), (b,))
    z = p.add("neg_left", (a, f.neg(tail)), (q,), (forward,), tail)
    parity = f.put("xor", (a, b))
    z = p.add("parity_left", (parity,), (q,), (z, backward), (a, b))
    z = p.add("neg", right=(f.neg(parity), q), premises=(z,), arg=parity)
    args = (q, f.neg(parity)) if variant == "reverse_group" else (f.neg(parity), q)
    z, _ = make_or_context(p, z, args)
    root = f.put("or", args)
    z = p.weak(z, root)
    z, _ = make_or_context(p, z, (root, root))
    square = f.put("or", (root, root))
    return z, square


def build(variant):
    f = API.Formulas()
    x, y = f.put("var", ("x",)), f.put("var", ("y",))
    p = Block(f, ())
    z, square = append_block(p, f.neg(x), f.neg(y), variant)
    p.prune(z)
    p.validate_block(square)
    comm = frozenset({(x, y), (y, x)})
    assert p.line_poly(len(p.nodes)-1) == f.mul(comm, comm)
    assert len(p.nodes) <= 100 and p.depth() <= 8
    bad = copy.copy(p); bad.nodes = copy.deepcopy(p.nodes)
    at = next(i for i, n in enumerate(bad.nodes) if n["rule"] == "parity_left" and len(n["arg"]) == 2)
    a = bad.nodes[at]["arg"][0]
    bad.nodes[at]["arg"] = (a, a)
    assert not bad.valid_rule(at)
    return p, square, (x, y)


def substitute_zero_second(words, value, f):
    out = frozenset()
    for word in words:
        if 1 in word:
            continue
        term = frozenset({()})
        for _ in word:
            term = f.mul(term, value)
        out ^= term
    return out


def integrate(kind, prototype):
    old, x = API.original(kind)
    f, size = old.f, old.symbols()
    y = next(i for i, (op, args) in enumerate(f.rows) if op == "var" and i != x)
    p = Block(f, old.inputs)
    one, zero = f.put("or"), f.neg(f.put("or"))
    xp, yp = f.neg(x), f.neg(y)
    basis = (one, xp, yp, f.put("or", (xp, yp)))
    templates = []
    for bits in range(16):
        terms = [basis[k] for k in range(4) if (bits >> k) & 1]
        templates.append(f.neg(f.put("xor", tuple(terms + [zero] * (4-len(terms))))))
    roots, tags, etas, blocks = [], [], [], []
    for term in templates:
        for repeat in range(2):
            j = len(blocks)
            start = len(p.nodes)
            parity = f.put("xor", (x,) * (2*(size+100+j)))
            zr, zeta, _ = OLD.excluded_middle(p, parity)
            u, v = f.put("or", (term, f.neg(zeta))), zeta
            assert f.poly(u) == f.poly(term) and not f.poly(v)
            block_start = len(p.nodes)
            tr, square = append_block(p, u, v)
            actual = [p.line_poly(i) for i in range(block_start, len(p.nodes)) if p.line_poly(i)]
            expected = [substitute_zero_second(row, f.poly(term), f) for row in prototype]
            assert actual == [value for value in expected if value]
            a = p.weak(p.weak(tr, zeta), f.neg(zeta))
            b = p.weak(p.weak(zr, f.neg(square)), f.neg(zeta))
            c = p.add("cut", right=(zeta,f.neg(zeta)), premises=(a,b), arg=square)
            root, _ = make_or_context(p,c,(zeta,f.neg(zeta)))
            sigma = f.put("or",(zeta,f.neg(zeta)))
            roots.append(root); tags.append(sigma); etas.append(f.neg(sigma))
            blocks.append({"start":start,"end":len(p.nodes),"term":term,"repeat":repeat})
    seed_end = len(p.nodes)
    mapping = {}
    inputs = [i for i,n in enumerate(old.nodes) if n["rule"]=="input"]
    for i in inputs:
        a = old.nodes[i]["arg"]
        mapping[i] = p.add("input",right=(a,),arg=a)
    ends = [len(p.nodes)]
    for eta in etas:
        for i in inputs: mapping[i] = p.weak(mapping[i],eta)
        ends.append(len(p.nodes))
    old_start = len(p.nodes)
    for i,n in enumerate(old.nodes):
        if n["rule"]=="input": continue
        if not n["premises"]:
            z = p.add(n["rule"],n["left"],n["right"],arg=n["arg"])
            for eta in etas: z = p.weak(z,eta)
        else:
            z = p.add(n["rule"],n["left"],n["right"]+tuple(etas),
                      tuple(mapping[j] for j in n["premises"]),n["arg"])
        mapping[i] = z
    final = mapping[len(old.nodes)-1]
    current = final
    for j in reversed(range(len(tags))):
        z = roots[j]
        for eta in etas[:j]: z = p.weak(z,eta)
        current = p.add("cut",right=etas[:j],premises=(z,current),arg=tags[j])
    for i in range(old_start,final+1):
        for parent in p.nodes[i]["premises"]:
            if parent < seed_end:
                assert not p.line_poly(parent)  # shared constant primitive axioms
            else:
                assert sum(end <= parent for end in ends) >= len(etas)
    assert all(p.line_poly(mapping[i]) == old.line_poly(i) for i in range(len(old.nodes)))
    assert p.line_poly(final) == frozenset({()})
    remap = p.prune(current)
    API.Proof.validate(p)
    assert p.depth() <= max(old.depth(),12)
    bad = copy.copy(p); bad.nodes = copy.deepcopy(p.nodes)
    bad.nodes[-1]["arg"] = x
    API.must_fail(bad.validate)
    return {"kind":kind,"nodes":len(p.nodes),"symbols":p.symbols(),"depth":p.depth(),
            "block_count":len(blocks),"input_rounds":len(ends),
            "precut":sum(i<old_start for i in remap),
            "formulas":f.rows,"proof":p.nodes,"inputs":p.inputs,
            "blocks_before_zero_node_reuse":blocks,
            "all_nonzero_block_sequences_match":True}


def run(out, gap_data):
    records, gap_rows = [], []
    for variant in ("forward_order", "reverse_order", "reverse_group"):
        p, root, variables = build(variant)
        words = [[list(word) for word in sorted(p.line_poly(i))] for i in range(len(p.nodes))]
        assert max((len(word) for row in words for word in row), default=0) <= 4
        records.append({"variant": variant, "nodes": len(p.nodes), "symbols": p.symbols(),
                        "depth": p.depth(), "root": root, "formulas": p.f.rows,
                        "proof": p.nodes, "line_words": words, "variables": variables})
        gap_rows.append(words)
    integrated = [integrate(kind, records[0]["line_words"]) for kind in ("units","or_cut")]
    data = {"passed": True, "case_count": len(records), "cases": records,
            "integrated_cases":integrated,
            "nodes_checked": sum(c["nodes"] for c in records+integrated),
            "negative_controls": len(records)+len(integrated)}
    out.write_text(json.dumps(data, indent=2) + "\n")
    # This file contains only exact nested-list data, not a generated algorithm.
    gap_data.write_text("commutatorBlockWords := " + repr(gap_rows) + ";\n")
    print(json.dumps({"passed": True, "case_count": len(records),
                      "nodes_checked": data["nodes_checked"], "negative_controls": data["negative_controls"],
                      "sizes": [{k: c[k] for k in ("variant", "nodes", "symbols", "depth")} for c in records],
                      "integrated":[{k:c[k] for k in ("kind","nodes","symbols","depth","block_count","input_rounds")} for c in integrated]}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--gap-data", type=Path, required=True)
    args = parser.parse_args()
    run(args.out, args.gap_data)

#!/usr/bin/env python3
"""Check the used-node construction, not a numerical lower bound.

Stages: build two normalized input refutations; transform each at orders 1,2;
check every inference, unique cedents, ancestry, literal tag translations,
old translated lines and complete preceding rounds; apply three distinct
negative controls; save all formula tables and accepted proof graphs.
Python is used for small syntax graphs and tiny exact free-word polynomials,
not a linear-algebra kernel. No CAS offers this presentation's graph checker.
Expected: all constructed graphs pass; each altered graph/property fails.
Refuted by: a bad inference, repeated or unused node, nonzero tag translation,
or missing input rounds in any constructed graph.
Possible because: contextual copying and discharge can change premise scopes,
and an odd parity tag keeps a nonzero formal Boolean defect.
"""
import argparse
import copy
import json
from pathlib import Path
from functools import lru_cache


class Formulas:
    def __init__(self):
        self.rows, self.ids = [], {}

    def put(self, op, args=()):
        key = (op, tuple(args))
        if key not in self.ids:
            self.ids[key] = len(self.rows)
            self.rows.append(key)
        return self.ids[key]

    def neg(self, a):
        return self.put("not", (a,))

    @lru_cache(None)
    def size(self, a):
        op, args = self.rows[a]
        return 1 if op == "var" else 1 + sum(self.size(b) for b in args)

    @lru_cache(None)
    def depth(self, a):
        op, args = self.rows[a]
        return 0 if op == "var" else 1 + max((self.depth(b) for b in args), default=-1)

    @staticmethod
    def mul(a, b):
        out = set()
        for u in a:
            for v in b:
                w = u + v
                if w in out:
                    out.remove(w)
                else:
                    out.add(w)
        return frozenset(out)

    @lru_cache(None)
    def poly(self, a):
        op, args = self.rows[a]
        one = frozenset({()})
        if op == "var":
            return one ^ frozenset({(a,)})
        if op == "not":
            return one ^ self.poly(args[0])
        if op == "xor":
            out = one if (1 + len(args)) % 2 else frozenset()
            for b in args:
                out ^= self.poly(b)
            return out
        out = one
        for b in args:
            out = self.mul(out, self.poly(b))
        return out


def seq(left=(), right=()):
    return tuple(sorted(left)), tuple(sorted(right))


class Proof:
    def __init__(self, f, inputs):
        self.f, self.inputs, self.nodes = f, tuple(inputs), []
        self.seen = set()

    def add(self, rule, left=(), right=(), premises=(), arg=None):
        cedent = seq(left, right)
        assert cedent not in self.seen, ("duplicate at construction", rule, cedent)
        node = {"rule": rule, "left": cedent[0], "right": cedent[1],
                "premises": tuple(premises), "arg": arg}
        self.nodes.append(node)
        self.seen.add(cedent)
        assert self.valid_rule(len(self.nodes) - 1)
        return len(self.nodes) - 1

    def weak(self, parent, a):
        n = self.nodes[parent]
        return self.add("weak", n["left"], n["right"] + (a,), (parent,), a)

    def valid_rule(self, i):
        n, f = self.nodes[i], self.f
        if any(j >= i or j < 0 for j in n["premises"]):
            return False
        ps = [self.nodes[j] for j in n["premises"]]
        out = seq(n["left"], n["right"])
        a, rule = n["arg"], n["rule"]
        if rule == "input":
            return not ps and a in self.inputs and out == seq((), (a,))
        if rule == "axiom":
            return not ps and out == seq((a,), (a,))
        if rule == "false":
            return not ps and out == seq((f.put("or"),), ())
        if rule == "empty_parity":
            return not ps and out == seq((), (f.neg(f.put("xor")),))
        if rule == "weak":
            return len(ps) == 1 and out == seq(ps[0]["left"], ps[0]["right"] + (a,))
        if rule == "neg":
            if len(ps) != 1 or a not in ps[0]["left"]:
                return False
            left = list(ps[0]["left"])
            left.remove(a)
            return out == seq(left, ps[0]["right"] + (f.neg(a),))
        if rule == "or_right":
            args = tuple(a)
            if len(ps) != 1 or not args:
                return False
            right = list(ps[0]["right"])
            for b in (args[0], f.put("or", args[1:])):
                if b not in right:
                    return False
                right.remove(b)
            return out == seq(ps[0]["left"], right + [f.put("or", args)])
        if rule == "or_left":
            args = tuple(a)
            if len(ps) != 2 or not args or ps[0]["right"] != ps[1]["right"]:
                return False
            lefts = [list(p["left"]) for p in ps]
            for left, b in zip(lefts, (args[0], f.put("or", args[1:]))):
                if b not in left:
                    return False
                left.remove(b)
            return sorted(lefts[0]) == sorted(lefts[1]) and out == seq(
                lefts[0] + [f.put("or", args)], ps[0]["right"])
        if rule == "cut":
            if len(ps) != 2 or any(p["left"] for p in ps):
                return False
            rights = [list(p["right"]) for p in ps]
            for right, b in zip(rights, (a, f.neg(a))):
                if b not in right:
                    return False
                right.remove(b)
            return sorted(rights[0]) == sorted(rights[1]) and out == seq((), rights[0])
        raise AssertionError(rule)

    def validate(self):
        assert self.nodes and seq(self.nodes[-1]["left"], self.nodes[-1]["right"]) == seq()
        assert len({seq(n["left"], n["right"]) for n in self.nodes}) == len(self.nodes)
        assert all(self.valid_rule(i) for i in range(len(self.nodes)))
        used, todo = set(), [len(self.nodes) - 1]
        while todo:
            i = todo.pop()
            if i not in used:
                used.add(i)
                todo.extend(self.nodes[i]["premises"])
        assert len(used) == len(self.nodes), "unused node"

    def symbols(self):
        return sum(1 + sum(self.f.size(a) for a in n["left"] + n["right"])
                   for n in self.nodes)

    def depth(self):
        return max(max([self.f.depth(a) + 1 for a in n["left"]] +
                       [self.f.depth(a) for a in n["right"]] + [0])
                   for n in self.nodes)

    def line_poly(self, i):
        n, out = self.nodes[i], frozenset({()})
        for a in n["left"]:
            out = self.f.mul(out, frozenset({()}) ^ self.f.poly(a))
        for a in n["right"]:
            out = self.f.mul(out, self.f.poly(a))
        return out


def original(kind):
    f = Formulas()
    x, y = f.put("var", ("x",)), f.put("var", ("y",))
    nx, ny = f.neg(x), f.neg(y)
    if kind == "units":
        p = Proof(f, (x, nx))
        a = p.add("input", right=(x,), arg=x)
        b = p.add("input", right=(nx,), arg=nx)
        p.add("cut", premises=(a, b), arg=x)
    else:
        c, empty = f.put("or", (x, y)), f.put("or")
        p = Proof(f, (c, nx, ny))
        a = p.add("input", right=(c,), arg=c)
        b = p.add("input", right=(nx,), arg=nx)
        z = p.add("input", right=(ny,), arg=ny)
        ax = p.add("axiom", (x,), (x,), arg=x)
        ax = p.weak(ax, y)
        ay = p.add("axiom", (y,), (y,), arg=y)
        ay = p.weak(ay, x)
        ef = p.add("false", (empty,))
        ef = p.weak(p.weak(ef, x), y)
        oy = p.add("or_left", (f.put("or", (y,)),), (x, y), (ay, ef), (y,))
        oc = p.add("or_left", (c,), (x, y), (ax, oy), (x, y))
        nc = p.add("neg", right=(f.neg(c), x, y), premises=(oc,), arg=c)
        ac = p.weak(p.weak(a, x), y)
        xy = p.add("cut", right=(x, y), premises=(ac, nc), arg=c)
        by = p.weak(b, y)
        yy = p.add("cut", right=(y,), premises=(xy, by), arg=x)
        p.add("cut", premises=(yy, z), arg=y)
    p.validate()
    return p, x


def transform(old, x, t, odd=False):
    f, S = old.f, old.symbols()
    p = Proof(f, old.inputs)
    roots, tags, false_tags = [], [], []
    for j in range(1, t + 1):
        a = f.put("xor", (x,) * (2 * (S + j) + int(odd)))
        na, empty = f.neg(a), f.put("or")
        tag = f.put("or", (na, a))
        u = p.add("axiom", (a,), (a,), arg=a)
        u = p.add("neg", right=(na, a), premises=(u,), arg=a)
        u = p.weak(u, empty)
        u = p.add("or_right", right=(na, f.put("or", (a,))),
                  premises=(u,), arg=(a,))
        u = p.add("or_right", right=(tag,), premises=(u,), arg=(na, a))
        roots.append(u)
        tags.append(tag)
        false_tags.append(f.neg(tag))
    tag_end = len(p.nodes)
    mapping = {}
    input_old = [i for i, n in enumerate(old.nodes) if n["rule"] == "input"]
    for i in input_old:
        a = old.nodes[i]["arg"]
        mapping[i] = p.add("input", right=(a,), arg=a)
    round_ends = [len(p.nodes)]
    for eta in false_tags:
        for i in input_old:
            mapping[i] = p.weak(mapping[i], eta)
        round_ends.append(len(p.nodes))
    prefix_end = len(p.nodes)
    old_start = prefix_end
    for i, n in enumerate(old.nodes):
        if n["rule"] == "input":
            continue
        if not n["premises"]:
            u = p.add(n["rule"], n["left"], n["right"], arg=n["arg"])
            for eta in false_tags:
                u = p.weak(u, eta)
        else:
            u = p.add(n["rule"], n["left"], n["right"] + tuple(false_tags),
                      tuple(mapping[j] for j in n["premises"]), n["arg"])
        mapping[i] = u
    contextual_final = mapping[len(old.nodes) - 1]
    current = contextual_final
    for j in reversed(range(t)):
        u = roots[j]
        for eta in false_tags[:j]:
            u = p.weak(u, eta)
        current = p.add("cut", right=false_tags[:j], premises=(u, current), arg=tags[j])
    p.validate()
    if not odd:
        assert all(f.poly(a) == frozenset() for a in tags)
        assert all(p.line_poly(i) == frozenset() for i in range(tag_end))
        assert all(p.line_poly(mapping[i]) == old.line_poly(i) for i in range(len(old.nodes)))
        assert p.line_poly(contextual_final) == frozenset({()})
        for i in range(old_start, contextual_final + 1):
            for parent in p.nodes[i]["premises"]:
                assert sum(end <= parent for end in round_ends) >= t
        assert p.depth() <= max(old.depth(), 4)
    return p, {"S": S, "t": t, "tag_end": tag_end, "prefix_end": prefix_end,
               "contextual_final": contextual_final, "round_ends": round_ends}


def must_fail(fn):
    try:
        fn()
    except AssertionError:
        return True
    raise AssertionError("negative control survived")


def run(out):
    cases, controls = [], []
    for kind in ("units", "or_cut"):
        for t in (1, 2):
            old, x = original(kind)
            p, meta = transform(old, x, t)
            # One-sided cut with a wrong principal formula.
            bad = copy.copy(p)
            bad.nodes = copy.deepcopy(p.nodes)
            assert bad.nodes[-1]["arg"] != x
            bad.nodes[-1]["arg"] = x
            assert must_fail(bad.validate)
            # A new, valid logical axiom, uniquely placed before the final cut,
            # but not used by it; retain the final inference with shifted references.
            bad = copy.copy(p)
            bad.nodes = copy.deepcopy(p.nodes)
            a = p.f.put("xor", (x,) * (2 * (meta["S"] + t + 100)))
            extra = {"rule": "axiom", "left": (a,), "right": (a,), "premises": (), "arg": a}
            bad.nodes.insert(len(bad.nodes) - 1, extra)
            assert bad.valid_rule(len(bad.nodes) - 2)
            assert must_fail(bad.validate)
            # Odd parity keeps the syntactic graph valid but loses formal zero tags.
            odd_old, odd_x = original(kind)
            odd, odd_meta = transform(odd_old, odd_x, t, odd=True)
            assert odd.line_poly(0) != frozenset()
            controls.append({"kind": kind, "t": t, "bad_cut_rejected": True,
                             "valid_unused_axiom_rejected": True,
                             "odd_tag_formal_defect_detected": True})
            cases.append({"kind": kind, **meta, "nodes": len(p.nodes),
                          "symbols": p.symbols(), "depth": p.depth(),
                          "original_nodes": old.nodes, "inputs": p.inputs,
                          "formulas": p.f.rows, "proof": p.nodes})
    result = {"cases": cases, "controls": controls,
              "case_count": len(cases), "control_count": 3 * len(controls),
              "passed": True}
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"passed": True, "cases": len(cases),
                      "negative_controls": result["control_count"],
                      "nodes_checked": sum(c["nodes"] for c in cases),
                      "sizes": [{k: c[k] for k in ("kind", "t", "nodes", "symbols", "depth")}
                                for c in cases]}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    run(parser.parse_args().out)

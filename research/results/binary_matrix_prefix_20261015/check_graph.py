#!/usr/bin/env python3
"""Check the repeated excluded-middle/bridge graph on two source fixtures.

Stages: two degree-at-most-two word-sum templates, two fresh copies each;
complete transformed graphs, all rules/ancestry/distinctness, every seed/zero
line, complete input rounds and three changed controls. Full graphs saved.
Small Python syntax and tiny degree-four free polynomials run in seconds;
this is not a matrix arithmetic or linear-algebra implementation.
Expected: both complete graphs pass and each changed property fails.
Refuted by: Any wrong line, inference, ancestry, duplicate cedent or prefix
scope in either constructed graph, or a negative control accepted as valid.
Possible because: Repeated seed syntax can collide, a zero bridge can lose its
premise, and a single copy does not implement the paired prefix.
The full asymptotic seed family is not enumerated by this schema check.
"""
import argparse
import copy
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location(
    "powered_schema", ROOT / "research/results/binary_powered_prefix_20261015/check_graph.py")
OLD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(OLD)
API = OLD.API


def transform(old):
    f, size = old.f, old.symbols()
    p = API.Proof(f, old.inputs)
    xs = [i for i, (op, _) in enumerate(f.rows) if op == "var"]
    x, y = xs[:2]
    one, zero = f.put("or"), f.neg(f.put("or"))
    xp, yp = f.neg(x), f.neg(y)
    templates = [f.neg(f.put("xor", (xp, yp, zero, zero))),
                 f.neg(f.put("xor", (f.put("or", (xp, yp)), xp, one, zero)))]
    roots, tags, etas, seed_lines, zeros, blocks = [], [], [], [], [], []
    for k, term in enumerate(templates):
        pair = []
        for repeat in range(2):
            j = 2*k + repeat
            start = len(p.nodes)
            parity = f.put("xor", (x,) * (2*(size + 20 + j)))
            zr, zeta, ids = OLD.excluded_middle(p, parity)
            zeros.extend(ids)
            inflated = f.put("or", (term, f.neg(zeta)))
            assert f.poly(inflated) == f.poly(term) and f.size(inflated) > size
            tr, theta, ids = OLD.excluded_middle(p, inflated)
            seed_lines.extend((i, term) for i in ids)
            pair.append(ids)
            a = p.weak(p.weak(tr, zeta), f.neg(zeta))
            b = p.weak(p.weak(zr, f.neg(theta)), f.neg(zeta))
            c = p.add("cut", right=(zeta, f.neg(zeta)), premises=(a,b), arg=theta)
            zeros.extend((a-1,a,b-1,b,c))
            root, ids = OLD.make_or(p,c,(zeta,f.neg(zeta)))
            zeros.extend(ids)
            sigma = f.put("or", (zeta,f.neg(zeta)))
            roots.append(root); tags.append(sigma); etas.append(f.neg(sigma))
            blocks.append({"start":start,"end":len(p.nodes),"term":term,
                           "repeat":repeat,"powered_nodes":pair[-1]})
    seed_end = len(p.nodes)
    mapping = {}
    inputs = [i for i,n in enumerate(old.nodes) if n["rule"] == "input"]
    for i in inputs:
        a = old.nodes[i]["arg"]
        mapping[i] = p.add("input",right=(a,),arg=a)
    ends = [len(p.nodes)]
    for eta in etas:
        for i in inputs: mapping[i] = p.weak(mapping[i],eta)
        ends.append(len(p.nodes))
    old_start = len(p.nodes)
    for i,n in enumerate(old.nodes):
        if n["rule"] == "input": continue
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
    p.validate()
    for i,term in seed_lines:
        value = f.poly(term)
        assert p.line_poly(i) == f.mul(value,value)^value
    assert all(not p.line_poly(i) for i in zeros)
    assert all(p.line_poly(mapping[i]) == old.line_poly(i) for i in range(len(old.nodes)))
    assert p.line_poly(final) == frozenset({()})
    for i in range(old_start,final+1):
        for parent in p.nodes[i]["premises"]:
            assert parent >= seed_end and sum(end <= parent for end in ends) >= len(etas)
    for i in range(final+1,len(p.nodes)):
        assert p.line_poly(i) == (frozenset({()}) if p.nodes[i]["rule"] == "cut" else frozenset())
    assert p.depth() <= max(old.depth(),9)
    return p,{"blocks":blocks,"seed_end":seed_end,"old_start":old_start,
              "contextual_final":final,"round_ends":ends,"original_size":size}


def run(out):
    cases = []
    for kind in ("units","or_cut"):
        old,x = API.original(kind)
        p,meta = transform(old)
        bad = copy.copy(p); bad.nodes = copy.deepcopy(p.nodes)
        assert bad.nodes[-1]["arg"] != x
        bad.nodes[-1]["arg"] = x
        API.must_fail(bad.validate)
        bad = copy.copy(p); bad.nodes = copy.deepcopy(p.nodes)
        fresh = p.f.put("xor",(x,)*(2*(meta["original_size"]+100)))
        bad.nodes.insert(len(bad.nodes)-1,{"rule":"axiom","left":(fresh,),"right":(fresh,),
                         "premises":(),"arg":fresh})
        assert bad.valid_rule(len(bad.nodes)-2)
        API.must_fail(bad.validate)
        odd = p.f.put("xor",(x,)*(2*(meta["original_size"]+200)+1))
        zeta = p.f.put("or",(p.f.neg(odd),odd))
        sigma = p.f.put("or",(zeta,p.f.neg(zeta)))
        assert p.f.poly(sigma) != frozenset()
        cases.append({"kind":kind,**meta,"nodes":len(p.nodes),"symbols":p.symbols(),
                      "depth":p.depth(),"inputs":p.inputs,"formulas":p.f.rows,"proof":p.nodes,
                      "controls":{"bad_cut":True,"unused_valid_axiom":True,
                                  "nonzero_valid_tag_detected":True}})
    data = {"passed":True,"cases":cases,"case_count":len(cases),
            "nodes_checked":sum(c["nodes"] for c in cases),"control_count":3*len(cases)}
    out.write_text(json.dumps(data,indent=2)+"\n")
    print(json.dumps({"passed":True,"case_count":len(cases),"nodes_checked":data["nodes_checked"],
                      "control_count":data["control_count"],
                      "sizes":[{k:c[k] for k in ("kind","nodes","symbols","depth")} for c in cases]}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("--out",type=Path,required=True)
    run(parser.parse_args().out)

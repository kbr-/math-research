#!/usr/bin/env python3
"""Summarize the outputs of bmd_cube_spine_chain_weights.gp (cycle bmd-20261001-l).

For each type: number of vertex assemblies, how many have a zero of multiplicity >= 2 or >= 3 off the special
points (deg gcd(S,S') > 0, resp. deg of the mult>=3 part > 0), whether every interpolation passed its check points,
the number of pencils, and how many have a member with a zero of order >= 3 off the special points (deg gcd of the
2x2 jet minors > 0) or a common root.
"""
import argparse
import re


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    lines = []
    for path in a.inputs:
        cur = None
        stats = {}
        for line in open(path):
            if line.startswith("type "):
                cur = line.split(" mu=")[0][5:]
                stats[cur] = dict(head=line.strip(), v=0, v2=0, v3=0, bad=0, p=0, p3=0, pb=0)
            elif "alphas" in line:
                s = stats[cur]
                s["v"] += 1
                g = int(re.search(r"deg gcd\(S,S'\) (\d+)", line).group(1))
                g3 = int(re.search(r"mult>=3 part (\d+)", line).group(1))
                s["v2"] += g > 0
                s["v3"] += g3 > 0
                s["bad"] += " checks 1;" not in line
            elif "pencil neck" in line:
                s = stats[cur]
                s["p"] += 1
                m = re.search(r"minors (\d+), deg common roots (\d+)", line)
                s["p3"] += int(m.group(1)) > 0
                s["pb"] += int(m.group(2)) > 0
        for k, s in stats.items():
            lines.append(f"{path}: {s['head']}")
            lines.append(f"  vertex assemblies {s['v']}: with a double zero off specials {s['v2']}, with a zero of "
                         f"multiplicity >= 3 {s['v3']}, failed check points {s['bad']}; pencils {s['p']}: with a member "
                         f"having a zero of order >= 3 {s['p3']}, with common roots {s['pb']}")
    open(a.out, "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()

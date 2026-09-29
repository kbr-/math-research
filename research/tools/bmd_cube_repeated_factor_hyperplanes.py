"""Is the six-root repeated factor a hyperplane arrangement? (30 September 2026; cycle bmd-20260930-r.)

The line certificate bmd_cube_wronskian_discriminant.c finds, at N = 6, an exponent-four factor of degree 45 of the
non-collision discriminant D_nc on every random line a(u) = alpha + u beta over F_p, p = 2^61 - 1, with the same
splitting pattern (16 linear, 4 quadratic, 7 cubic factors) on two lines. A fixed pattern on random lines is what a union
of hyperplanes defined over number fields gives, and not what a geometrically irreducible component of degree > 1 gives.

Tested statement: the 16 F_p-rational roots on each line are the intersections with 16 hyperplanes c.a = 0 (c in F_p^6,
through the origin since Delta_W is homogeneous). The test fixes c from one rational root on each of lines 1..k and asks
whether the remaining lines meet {c.a = 0} at one of their rational roots:
  stage T: translation-invariant hyperplanes (c.1 = 0), k = 4, 16^4 candidates;
  stage G: general hyperplanes through the origin, k = 5, 16^5 candidates.
A chance confirmation on one further line has probability about 16/p. Controls: the collision parameters u_ij must give
exactly the 15 hyperplanes a_i = a_j in both stages; 16 random parameters per line must give none.

This script runs the certificate binary once per seed (orchestration only) and passes the data to
bmd_cube_repeated_factor_hyperplanes.gp, which does the matching.
Usage: python3 bmd_cube_repeated_factor_hyperplanes.py BINARY WORKDIR OUT SEED...
"""
import json
import os
import subprocess
import sys


def main():
    binary, work, out = sys.argv[1], sys.argv[2], sys.argv[3]
    seeds = sys.argv[4:]
    os.makedirs(work, exist_ok=True)
    lines = []
    for s in seeds:
        path = os.path.join(work, "wronskian-disc-N6-seed%s.json" % s)
        subprocess.run([binary, "6", s, path], check=True, stdout=subprocess.DEVNULL)
        d = json.load(open(path))
        reps = [f for f in d["squarefree_decomposition"] if f["exponent"] == 4]
        if len(reps) != 1 or reps[0]["degree"] != 45:
            raise SystemExit("seed %s: unexpected decomposition %s" % (s, d["squarefree_decomposition"]))
        lines.append((d["line_alpha"], d["line_beta"], reps[0]["monic_coefficients_low_to_high"]))
    data = os.path.join(work, "data.gp")
    with open(data, "w") as f:
        f.write("SEEDS = [%s];\n" % ",".join(seeds))
        f.write("A = [%s];\n" % ";".join(",".join(l[0]) for l in lines))
        f.write("B = [%s];\n" % ";".join(",".join(l[1]) for l in lines))
        f.write("G = [%s];\n" % ",".join("Polrev([%s],'u)" % ",".join(l[2]) for l in lines))
    gp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bmd_cube_repeated_factor_hyperplanes.gp")
    subprocess.run(["gp", "-q", "--default", "nbthreads=12", data, gp],
                   check=True, env=dict(os.environ, OUT=out))


if __name__ == "__main__":
    main()

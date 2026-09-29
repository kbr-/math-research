"""Splitting pattern over F_p of the repeated factors of the six-root Wronskian discriminant on several random lines
(29 September 2026; route review bmd-20260929-zzc, Lead 3). For a geometrically irreducible hypersurface G = 0, a random
F_p-line section behaves like a random polynomial with large Galois group, with about one F_p-rational root on average;
the number of F_p-rational roots on a random line estimates the number of geometrically irreducible components of G
defined over F_p. Reads the certificate JSON files (bmd_cube_wronskian_discriminant.c output), extracts every repeated
factor's monic coefficients, and factors them over F_p with PARI/GP (called once for all inputs).
Usage: python3 bmd_cube_repeated_factor_split.py OUT JSON...
"""
import json
import os
import subprocess
import sys


def main():
    out, files = sys.argv[1], sys.argv[2:]
    rows = []
    for f in files:
        d = json.load(open(f))
        for part in d["squarefree_decomposition"]:
            if part["exponent"] > 1:
                rows.append((f, d["seed"], int(d["p"]), part["exponent"], part["monic_coefficients_low_to_high"]))
    script = []
    for f, seed, p, e, co in rows:
        script.append("P = Mod(1, %d) * Polrev([%s]); F = factor(P); "
                      "print(\"seed %s exponent %d degree \", poldegree(P), \": factor degrees \", "
                      "vecsort(apply(poldegree, F[,1]~)), \"; F_p-rational roots \", #[g | g <- F[,1]~, poldegree(g) == 1]);"
                      % (p, ",".join(co), seed, e))
    res = subprocess.run(["gp", "-q", "-s", "1G"], input="\n".join(script) + "\n", capture_output=True, text=True, check=True)
    lines = [ln for ln in res.stdout.splitlines() if ln.strip()]
    with open(out, "w") as fo:
        fo.write("# inputs: " + " ".join(os.path.basename(f) for f in files) + "\n")
        for ln in lines:
            fo.write(ln + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()

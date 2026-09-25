"""The initial-segment determinant of the cube's Catalan root curve, computed and factored exactly.

Statement studied.  With z_i = sum_{j>=1} (-1)^j C_{j-1} (y_i T)^j and the basis T^Q z^r
(r in {0,1}^n, 2Q + |r| <= d) of polynomials of degree <= d in z (sharpness lemma), the orders of
degree <= d form the initial segment {0, ..., N_{2,n}(d)-1} if and only if the square matrix of
coefficients of T^1, ..., T^{N-1} in the non-constant basis elements is nonsingular.  Its determinant
Delta_{n,d} lies in Z[y_1..y_n]; the conjecture over F says Delta_{n,d} != 0 in F[y].  The script
builds the entries with sympy and computes and factors Delta_{n,d} in Singular.
Prints the integer content of Delta (its prime factors are the characteristics where the
law fails identically) and each irreducible factor's degree, size, multiplicity and content.
With --lead it skips the factorization and prints the coefficients of the lex-leading and
lex-trailing monomials of Delta (orders lp and rp), whose gcd with the content bounds the content.
Usage: bmd_cube_order_determinant.py n d [OUT] [--lead]
"""
import itertools, subprocess, sys
import sympy as sp


def main():
    n, d = int(sys.argv[1]), int(sys.argv[2])
    ys = sp.symbols(f'y1:{n + 1}')
    basis = [(Q, r) for Q in range(d // 2 + 1) for r in itertools.product([0, 1], repeat=n)
             if 2 * Q + sum(r) <= d and (Q, r) != (0, (0,) * n)]
    Nd = len(basis) + 1
    M = Nd  # need coefficients T^1 .. T^(N-1)
    cat = [sp.catalan(j) for j in range(M + 1)]
    z = [[0] + [(-1) ** j * cat[j - 1] * y ** j for j in range(1, M)] for y in ys]

    def mul(a, b):
        c = [0] * M
        for i, ai in enumerate(a):
            if ai != 0:
                for j in range(M - i):
                    if b[j] != 0:
                        c[i + j] += ai * b[j]
        return [sp.expand(x) for x in c]

    cols = []
    for Q, r in basis:
        s = [0] * M
        s[Q] = 1
        for i in range(n):
            if r[i]:
                s = mul(s, z[i])
        cols.append(s[1:M])
    size = len(basis)
    print(f'n={n} d={d}: N={Nd}, matrix {size}x{size}', flush=True)
    # determinant and factorization in Singular (fast multivariate arithmetic over QQ)
    names = ','.join(str(y) for y in ys)
    entries = ','.join(str(sp.expand(cols[j][i])).replace('**', '^') for i in range(size) for j in range(size))
    lead = '--lead' in sys.argv
    argv = [a for a in sys.argv if a != '--lead']
    script = (f'LIB "polylib.lib";\nring R = 0, ({names}), dp;\nmatrix A[{size}][{size}] = {entries};\n'
              'poly D = det(A);\nprint("CONTENT " + string(content(D)));\n')
    if lead:
        script += (f'ring R1 = 0, ({names}), lp;\npoly D1 = imap(R, D);\n'
                   'print("LEX-LEADING " + string(leadcoef(D1)) + " * " + string(leadmonom(D1)));\n'
                   f'ring R2 = 0, ({names}), rp;\npoly D2 = imap(R, D);\n'
                   'print("REVLEX-LEADING " + string(leadcoef(D2)) + " * " + string(leadmonom(D2)));\n'
                   'print("TERMS " + string(size(D2)));\nquit;\n')
    else:
        script += ('list L = factorize(D);\nint i;\n'
                   'for (i = 1; i <= size(L[1]); i++) { poly f = L[1][i]; '
                   'string sf = "(large)"; if (size(f) <= 4) { sf = string(f); } '
                   'print("FACTOR deg=" + string(deg(f)) + " terms=" + string(size(f)) + " mult=" + string(L[2][i]) '
                   '+ " content=" + string(content(f)) + " " + sf); kill f; kill sf; }\n'
                   'quit;\n')
    res = subprocess.run(['Singular', '-q'], input=script, capture_output=True, text=True, check=True)
    out = f'n={n} d={d}: N={Nd}, matrix {size}x{size}\n' + res.stdout.strip() + '\n'
    print(out, end='', flush=True)
    if len(argv) > 3:
        open(argv[3], 'w').write(out)


if __name__ == '__main__':
    main()

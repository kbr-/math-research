#!/usr/bin/env python3
"""Does the joint filtration number of a system depend on the basis of linear forms?  Three clauses on F_2^3.

Statement tested: for the rows a|b, b|c, a|c on the free variables a, b, c over F_2 (each row forbids its two
forms being both zero), and a basis B of the linear forms, let rho2(B) be the largest size of a set S of forms
of B such that for every join of one or two rows the trace monomial of S (the product of the forms of S on
which the join's allowed set depends, in B-coordinates) is not equal on the allowed set to a polynomial of
lower degree.  Then rho2 is not the same for every basis.

Expected before the run, from a hand computation: rho2 = 1 for the basis {a, b, c} (each pair of variables is
reduced by the row containing it, or by a join of two rows through a shared variable), and rho2 = 2 for the
basis {a+b, a+c, a}, by S = {a+b, a+c}, whose product has quadratic part ab+ac+bc, the one quadric that is
affine on none of the three joins.  If rho2 came out equal for all 28 bases, the hand computation or the
reading of the definition would be wrong.  No basis can give 3: n = 3 and the rows are not full.
Control independent of the reduction code: for the basis {a, b, c} the script also checks directly that
ab = a+b+1 on the allowed set of the first row.
"""
import argparse
import itertools

N = 3
POINTS = list(itertools.product((0, 1), repeat=N))
ROWS = {"a|b": lambda p: p[0] | p[1], "b|c": lambda p: p[1] | p[2], "a|c": lambda p: p[0] | p[2]}


def form_value(form, p):
    return sum(f & x for f, x in zip(form, p)) & 1


def rank_mod2(rows):
    rows = [int("".join(map(str, r)), 2) for r in rows]
    rank = 0
    for bit in reversed(range(max((r.bit_length() for r in rows), default=0))):
        pivot = next((i for i, r in enumerate(rows) if i >= rank and r >> bit & 1), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        rows = [r ^ rows[rank] if i != rank and r >> bit & 1 else r for i, r in enumerate(rows)]
        rank += 1
    return rank


def has_lower_representative(func, allowed, degree):
    """Whether func, a 0/1 vector on the allowed points, is a polynomial of degree < degree on them."""
    monomials = [s for k in range(degree) for s in itertools.combinations(range(N), k)]
    columns = [[int(all(p[i] for i in s)) for p in allowed] for s in monomials]
    return rank_mod2(columns) == rank_mod2(columns + [func]) if columns else not any(func)


def rho2(basis):
    coords = lambda p: tuple(form_value(f, p) for f in basis)            # the point in B-coordinates
    best = 0
    names = list(ROWS)
    joins = [(r,) for r in names] + list(itertools.combinations(names, 2))
    for size in range(len(basis), 0, -1):
        for chosen in itertools.combinations(range(len(basis)), size):
            ok = True
            for join in joins:
                allowed = [p for p in POINTS if all(ROWS[r](p) for r in join)]
                image = {coords(p) for p in allowed}
                scope = [i for i in range(N) if any(tuple(c ^ (j == i) for j, c in enumerate(q)) not in image
                                                    for q in image)]
                trace = [i for i in chosen if i in scope]
                func = [int(all(form_value(basis[i], p) for i in trace)) for p in allowed]
                if has_lower_representative(func, allowed, len(trace)):
                    ok = False
                    break
            if ok:
                return size
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    forms = [f for f in POINTS if any(f)]
    bases = [b for b in itertools.combinations(forms, N) if rank_mod2(b) == N]
    row1 = [p for p in POINTS if ROWS["a|b"](p)]
    assert all((p[0] & p[1]) == (p[0] ^ p[1] ^ 1) for p in row1)       # the independent control
    name = lambda f: "+".join(v for v, bit in zip("abc", f) if bit)
    with open(args.out, "w") as fh:
        fh.write(f"bases={len(bases)} control_ab_equals_a+b+1_on_first_row=True\n")
        for basis in bases:
            fh.write(f"basis={{{', '.join(name(f) for f in basis)}}} rho2={rho2(basis)}\n")
    print("done")


if __name__ == "__main__":
    main()

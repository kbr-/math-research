-- Threshold ideals of {0,1}^4 against the S_5 invariants of the branch points (bmd-r116, route review 17).
--
-- Statement tested.  With branch points (r_0, ..., r_4) = (0, y_1, ..., y_4) and centred power sums
-- p_k = sum_i (r_i - rbar)^k, Springer's theory of regular elements says V(p_2, p_3, p_4) in P^3 is the S_5-orbit
-- of the eigenlines of 5-cycles, the pentagon configurations r_i = zeta^i, a complete intersection of degree 24.
-- For each (m, LIMIT) the script computes the top coordinates of the kernel generators of A_m of excess <= LIMIT
-- (the part of I^{(d+1)}_m in degrees <= LIMIT) and reports, for each generator:
--   whether it lies in (p_2, p_3, p_4), in (p_2, p_3, p_4)^2, and its vanishing order at the pentagon point
--   (along a random line through it) and at the square point r = (0, 1, i, -1, -i) (eigenline of a 4-cycle);
-- and whether the ideal of all of them equals (p_2, p_3, p_4).
-- Usage: M2 --script THIS n d m1:LIMIT1,m2:LIMIT2,...
kk = ZZ/32003;
Cj = j -> lift((product(toList(0..j-1), i -> (1/2 - i))) / (j!) * 4^j, ZZ);
n = value scriptCommandLine#1; d = value scriptCommandLine#2;
jobs = apply(separate(",", scriptCommandLine#3), s -> apply(separate(":", s), value));
assert(n == 4);
R = kk[y_1..y_n];
S = R[T];
rows = flatten apply(toList(0..d//2), Q -> flatten apply(subsets(n), s0 -> if 2*Q + #s0 <= d then {(Q, s0)} else {}));
rs = {0_R} | toList(y_1..y_n);
rbar = (1/5) * sum rs;
pk = k -> sum(rs, r -> (r - rbar)^k);
P234 = ideal(pk 2, pk 3, pk 4);
-- the other Springer eigen-orbits: 4-cycles (squares, 30 points) V(p2,p3,p5); 3-cycles (40 points) V(p2,p4,p5)
P235 = ideal(pk 2, pk 3, pk 5);
P245 = ideal(pk 2, pk 4, pk 5);
<< "(p2,p3,p4): codim " << codim P234 << ", degree " << degree P234 << endl << flush;
-- vanishing order along a random line through a point given over a finite extension
setRandomSeed 116;
vv = apply(n, i -> random kk);
ordAt = (f, E, pt) -> (
    Et := E[tt];
    g := sub(f, apply(n, i -> R_i => sub(pt#i, Et) + (vv#i) * tt));
    if g == 0 then infinity else min apply(terms g, x -> first degree x));
E5 = kk[z] / ideal(z^4 + z^3 + z^2 + z + 1);
pent = apply(4, i -> z^(i+1) - 1);
E4 = kk[j] / ideal(j^2 + 1);
sq = {1_E4, j, -1_E4, -j};
for job in jobs do (
    m := job#0; lim := job#1;
    t0 := cpuTime();
    ws := apply(n, i -> sum(toList(0..m), jj -> (Cj jj) * (sub(R_i, S))^jj * T^jj));
    A := matrix apply(rows, rw -> (
        f := T^(rw#0) * product(rw#1, i -> ws#i);
        apply(toList(0..m), cc -> sub(coefficient(T^cc, f + 0*T^(m+1)), R))));
    f0 := map(R^(apply(rows, rw -> -(rw#0))), R^(apply(toList(0..m), c -> -c)), A);
    G := syz(f0, DegreeLimit => m + lim);
    tops := select(apply(numcols G, jj -> G_(m, jj)), x -> x != 0);
    J := ideal mingens ideal tops;
    << "m=" << m << " (excess <= " << lim << "): " << numgens J << " top-coordinate generators, degrees "
       << toString apply(first entries gens J, x -> first degree x) << "  cpu=" << cpuTime() - t0 << endl << flush;
    for g in first entries gens J do
        << "   deg " << first degree g << ": in (p2,p3,p4) " << (g % P234 == 0) << ", in (p2,p3,p4)^2 "
           << (g % (P234^2) == 0) << ", order at pentagon " << ordAt(g, E5, pent) << ", order at square "
           << ordAt(g, E4, sq) << ", in (p2,p3,p5) " << (g % P235 == 0) << ", in (p2,p3,p5)^2 " << (g % (P235^2) == 0)
           << ", in (p2,p4,p5) " << (g % P245 == 0) << endl << flush;
    << "   J == (p2,p3,p4): " << (J == P234) << "; J in (p2,p3,p4): " << isSubset(J, P234) << endl << flush);

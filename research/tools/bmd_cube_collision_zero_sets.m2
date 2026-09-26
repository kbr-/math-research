-- Zero sets of the collision-regime threshold ideals on {0,1}^n (bmd-r115).
--
-- Statement tested.  thm:cube-collision-regime-torsion puts V(I^{(d+1)}_m) inside the 25 lines where two collision
-- hyperplanes of P^3 meet, for n = 4 and m >= 8d+1.  Question: is V(I_m) empty there (I_m primary to the irrelevant
-- ideal), or does it contain points of the lines?  The script computes the generators of Sol_m = ker A_m of excess
-- <= LIMIT, the ideal J of their top coordinates (J is contained in I_m, so V(I_m) is contained in V(J)), and
-- reports the projective dimension and degree of V(J), its minimal primes with their degrees, whether each lies on a
-- triple line {y_a = y_b = y_c} or a double-double line (in the S_5 coordinates: collision forms y_i and y_i - y_j),
-- and whether the S_5-invariant quadric Q = sum y_i^2 - (1/2) sum_{i<j} y_i y_j lies in it.
-- Usage: M2 --script THIS n d LIMIT m1,m2,...
kk = ZZ/32003;
Cj = j -> lift((product(toList(0..j-1), i -> (1/2 - i))) / (j!) * 4^j, ZZ);
n = value scriptCommandLine#1; d = value scriptCommandLine#2; lim = value scriptCommandLine#3;
ms = apply(separate(",", scriptCommandLine#4), value);
R = kk[y_1..y_n];
S = R[T];
rows = flatten apply(toList(0..d//2), Q -> flatten apply(subsets(n), s0 -> if 2*Q + #s0 <= d then {(Q, s0)} else {}));
N = #rows;
-- collision forms in the S_{n+1} coordinates (r_0, ..., r_n) = (0, y_1, ..., y_n): r_0 = r_i is y_i = 0, r_i = r_j is y_i = y_j
forms = apply(n, i -> y_(i+1)) | apply(subsets(n, 2), p -> y_(p#0 + 1) - y_(p#1 + 1));
Qf = sum(n, i -> y_(i+1)^2) - (1/2) * sum(subsets(n, 2), p -> y_(p#0 + 1) * y_(p#1 + 1));
for m in ms do (
    t0 := cpuTime();
    ws := apply(n, i -> sum(toList(0..m), j -> (Cj j) * (sub(R_i, S))^j * T^j));
    A := matrix apply(rows, rw -> (
        f := T^(rw#0) * product(rw#1, i -> ws#i);
        apply(toList(0..m), cc -> sub(coefficient(T^cc, f + 0*T^(m+1)), R))));
    f0 := map(R^(apply(rows, rw -> -(rw#0))), R^(apply(toList(0..m), c -> -c)), A);
    G := syz(f0, DegreeLimit => m + lim);
    tops := select(apply(numcols G, j -> G_(m, j)), x -> x != 0);
    J := ideal mingens ideal tops; Jlast = J;
    << "m=" << m << " N=" << N << " kernel generators (excess <= " << lim << "): " << numcols G
       << "; top-coordinate generator degrees " << toString sort apply(first entries gens J, x -> first degree x)
       << "  cpu=" << cpuTime() - t0 << endl << flush;
    if J == 0 then continue;
    Js := saturate J;
    << "  V(J): projective dim " << dim Js - 1 << ", degree " << degree Js << ", J saturated: " << (J == Js) << endl << flush;
    if dim Js >= 1 then (
        for P in decompose Js do (
            onForms := select(forms, f -> f % P == 0);
            << "    component: proj dim " << dim P - 1 << ", degree " << degree P << ", collision forms vanishing: "
               << #onForms << ", Q in it: " << (Qf % P == 0) << ", generators " << toString first entries gens P << endl << flush));
    << "  cpu=" << cpuTime() - t0 << endl << flush);
-- Pentagon check (n = 4): the point with branch points r_i = zeta^i (i = 0..4), zeta a primitive 5th root of unity,
-- is y_i = zeta^i - 1 in the coordinates (r_0, ..., r_4) = (0, y_1, ..., y_4).  Its S_5-orbit has 120/5 = 24 points.
-- Report whether the top coordinates of the last m vanish there.
if n == 4 then (
    E := kk[z] / ideal(z^4 + z^3 + z^2 + z + 1);
    pent := map(E, R, apply(4, i -> z^(i+1) - 1));
    << "pentagon point (zeta^i - 1): all top-coordinate generators of the last m vanish there: "
       << (all(first entries gens Jlast, g -> pent g == 0)) << "; Q vanishes: " << (pent Qf == 0) << endl << flush);

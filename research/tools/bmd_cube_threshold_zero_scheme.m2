-- Zero scheme of the threshold ideal one step past the boundary, cut by a random plane (bmd-r111).
--
-- Statement tested (prop:cube-first-step-saturated, conj:cube-first-step-rank-drop).  On {0,1}^n with d = h-1,
-- N = N_{2,n}(d), m = N+1: compute generators of Sol = ker A_m up to excess LIMIT, the threshold ideal I of top
-- coordinates, and restrict I and the rank-drop ideal (maximal minors of A_N, saturated by the collision forms) to a
-- random plane (seed 111).  Report the projective dimension and degree of V(I) on the plane, with and without
-- saturating by the collision forms, and compare with the rank-drop points.  If deg V(I|plane) equals the degree of
-- the collision-saturated rank-drop section, the zero scheme of I has no component inside the collision hyperplanes
-- (for this plane).  Usage: M2 --script THIS n d LIMIT
kk = ZZ/32003;
Cj = j -> lift((product(toList(0..j-1), i -> (1/2 - i))) / (j!) * 4^j, ZZ);
n = value scriptCommandLine#1; d = value scriptCommandLine#2; lim = value scriptCommandLine#3;
setRandomSeed 111;
R = kk[y_1..y_n];
S = R[T];
rows = flatten apply(toList(0..d//2), Q -> flatten apply(subsets(n), s0 -> if 2*Q + #s0 <= d then {(Q, s0)} else {}));
N = #rows; m = N + 1;
ws = apply(n, i -> sum(toList(0..m), j -> (Cj j) * (sub(R_i, S))^j * T^j));
A = matrix apply(rows, rw -> (
    f := T^(rw#0) * product(rw#1, i -> ws#i);
    apply(toList(0..m), cc -> sub(coefficient(T^cc, f + 0*T^(m+1)), R))));
f0 = map(R^(apply(rows, rw -> -(rw#0))), R^(apply(toList(0..m), c -> -c)), A);
t0 = cpuTime();
G = syz(f0, DegreeLimit => m + lim);
tops = select(apply(numcols G, j -> G_(m, j)), x -> x != 0);
I = ideal tops;
I = ideal mingens I;
<< "n=" << n << " d=" << d << " m=" << m << " threshold ideal generator degrees (excess <= " << lim << "): "
   << toString sort apply(first entries gens I, x -> first degree x) << " cpu=" << cpuTime() - t0 << endl << flush;
P = kk[x_1..x_(n-1)];
cs = apply(n-1, i -> random kk);
phi = map(P, R, toList(x_1..x_(n-1)) | {sum(n-1, i -> cs#i * x_(i+1))});
coll = product(n, i -> phi(y_(i+1))) * product(subsets(n, 2), p -> phi(y_(p#0 + 1) - y_(p#1 + 1)));
Ip = phi I;
Ips = saturate(Ip);
<< "V(I) on plane: dim(proj) " << dim Ips - 1 << " degree " << degree Ips << endl << flush;
Ic = saturate(Ip, coll);
<< "V(I) on plane, collisions removed: dim(proj) " << dim Ic - 1 << " degree " << degree Ic << endl << flush;
J = saturate(minors(N, phi submatrix(A, , toList(0..N))), coll);
<< "rank-drop points (collisions removed): degree " << degree J << "   equal to V(I) off collisions: " << (J == Ic) << endl << flush;
<< "cpu=" << cpuTime() - t0 << endl << flush;

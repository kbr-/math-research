-- Plane section of the rank-drop locus of the boundary matrix, and membership of a threshold generator (bmd-r111).
--
-- Statement tested (prop:cube-middle-threshold-height, lem:cube-residue-duality-all-n).  On {0,1}^n with d = h-1 and
-- N = N_{2,n}(d), let A_N be the N x (N+1) matrix of coefficients of T^0..T^N in the rows T^Q w^r (2Q+|r| <= d).
-- Z = {rank A_N < N} minus the collision hyperplanes is where h^0(d H_inf - (N+1) p_0) >= 1 on the fibre curve.  The
-- claim tested: the threshold ideal I^{(d+1)}_{N+1} vanishes on Z, i.e. its generator F (read from a saved
-- bmd_cube_thresholds_m2 output) lies in the radical of the saturated ideal of Z.  The script restricts to a random
-- plane y_n = sum_{i<n} c_i y_i, computes J = maximal minors of A_N, saturates by the collision forms, and reports
-- dim, degree, the least degree of a generator of the saturated ideal, whether it is radical, and whether F|plane
-- lies in it or in its radical.  Usage: M2 --script THIS n d TOPFILE
kk = ZZ/32003;
Cj = j -> lift((product(toList(0..j-1), i -> (1/2 - i))) / (j!) * 4^j, ZZ);
n = value scriptCommandLine#1; d = value scriptCommandLine#2; topfile = scriptCommandLine#3;
setRandomSeed 111;
R = kk[y_1..y_n];
S = R[T];
rows = flatten apply(toList(0..d//2), Q -> flatten apply(subsets(n), s0 -> if 2*Q + #s0 <= d then {(Q, s0)} else {}));
N = #rows;
ws = apply(n, i -> sum(toList(0..N), j -> (Cj j) * (sub(R_i, S))^j * T^j));
A = matrix apply(rows, rw -> (
    f := T^(rw#0) * product(rw#1, i -> ws#i);
    apply(toList(0..N), cc -> sub(coefficient(T^cc, f + 0*T^(N+1)), R))));
<< "n=" << n << " d=" << d << " N=" << N << " matrix " << numrows A << "x" << numcols A << endl << flush;
-- the threshold generator
txt = get topfile;
ln = select(lines txt, l -> match("top 0: ", l));
s = replace("^ *top 0: ", "", ln#0);
s = replace("\\)\\*\\(-?[0-9]+\\)$", ")", s);
F = value s;
<< "F degree " << first degree F << endl << flush;
-- random plane y_n = sum c_i y_i
P = kk[x_1..x_(n-1)];
cs = apply(n-1, i -> random kk);
phi = map(P, R, toList(x_1..x_(n-1)) | {sum(n-1, i -> cs#i * x_(i+1))});
Ap = phi A;
t0 = cpuTime();
J = minors(N, Ap);
<< "minors done cpu=" << cpuTime() - t0 << endl << flush;
coll = product(n, i -> phi(y_(i+1))) * product(subsets(n, 2), p -> phi(y_(p#0 + 1) - y_(p#1 + 1)));
Js = saturate(J, coll);
<< "saturated cpu=" << cpuTime() - t0 << endl << flush;
<< "dim(proj) " << dim Js - 1 << " degree " << degree Js << " generator degrees " << toString sort flatten degrees mingens Js << endl << flush;
rad = radical Js;
<< "radical: " << (rad == Js) << " radical degree " << degree rad << " radical generator degrees " << toString sort flatten degrees mingens rad << endl << flush;
Fp = phi F;
<< "F in saturated ideal: " << (Fp % Js == 0) << "   F in radical: " << (Fp % rad == 0) << endl << flush;

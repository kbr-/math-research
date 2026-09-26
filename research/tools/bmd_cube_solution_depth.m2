-- Depth test for the solution modules of the threshold system on {0,1}^n, degree by degree (bmd-r128).
--
-- Statement tested.  lem:cube-zero-free-criterion: if V(I_m) is empty and the order-zero system is not solvable at
-- m, then depth K_{m-1} = 2.  On {0,1}^4 at d = 2 over F_32003, V(I_17) = V(I_18) = empty
-- (check:cube-collision-regime-empty-d2) and order zero fails at m = 17, 18, so the lemma predicts
-- depth K_16 = depth K_17 = 2.  By lem:cube-restriction-exactness (Parts 1 and 3), for a hyperplane L = V(lambda)
-- avoiding the associated primes of C other than the irrelevant ideal,
--     defect(l) := dim (K_L)_l - dim K_l + dim K_{l-1} = dim (0 :_C lambda)_{l-1},
-- and depth K >= 3 iff every defect vanishes.  The script computes these dimensions by ranks of the degree-l parts of
-- A_m and of its restriction to a random hyperplane (all linear algebra over F_32003, no Groebner bases), for
-- l = LMIN..LMAX, and prints the defects.  A nonzero defect certifies depth K = 2 only if the random hyperplane
-- avoids those associated primes; a zero defect in a degree is a statement about that degree only.
-- Grading: source column c has generator degree c - m (W_c of degree l + m - c in degree l), rows (Q, r) degree Q - m.
-- Usage: M2 --script THIS n d m1,m2,... LMIN LMAX
kk = ZZ/32003;
Cj = j -> lift((product(toList(0..j-1), i -> (1/2 - i))) / (j!) * 4^j, ZZ);
n = value scriptCommandLine#1; d = value scriptCommandLine#2;
ms = apply(separate(",", scriptCommandLine#3), value);
lmin = value scriptCommandLine#4; lmax = value scriptCommandLine#5;
R = kk[y_1..y_n];
RL = kk[x_1..x_(n-1)];
setRandomSeed 128;
restr = map(RL, R, apply(n, i -> sum(n-1, a -> random(kk) * x_(a+1))));
S = R[T];
rows = flatten apply(toList(0..d//2), Q -> flatten apply(subsets(n), s0 -> if 2*Q + #s0 <= d then {(Q, s0)} else {}));
-- dimension of the degree-l part of ker f: the columns of B span the degree-l part of the source; the image of each
-- column is written in the monomial basis of the degree-l part of each target summand, and the rows are stacked
kerdim = (f, l) -> (
    B := basis(l, source f);
    if numcols B == 0 then return 0;
    F := f * B;
    tdeg := apply(degrees target f, first);
    blocks := select(apply(numrows F, i -> (
        mons := basis(l - tdeg#i, ring f);
        if numcols mons == 0 then null else sub(last coefficients(F^{i}, Monomials => mons), coefficientRing ring f))),
        x -> x =!= null);
    if #blocks == 0 then return numcols B;
    M := fold((a, b) -> a || b, blocks);
    numcols B - rank M);
for m in ms do (
    t0 := cpuTime();
    ws := apply(n, i -> sum(toList(0..m), j -> (Cj j) * (sub(R_i, S))^j * T^j));
    A := matrix apply(rows, rw -> (
        f := T^(rw#0) * product(rw#1, i -> ws#i);
        apply(toList(0..m), cc -> sub(coefficient(T^cc, f + 0*T^(m+1)), R))));
    f0 := map(R^(apply(rows, rw -> m - rw#0)), R^(apply(toList(0..m), c -> m - c)), A);
    assert isHomogeneous f0;
    fL := map(RL^(apply(rows, rw -> m - rw#0)), RL^(apply(toList(0..m), c -> m - c)), restr A);
    assert isHomogeneous fL;
    prev := kerdim(f0, lmin - 1);
    for l from lmin to lmax do (
        kl := kerdim(f0, l); kLl := kerdim(fL, l);
        << "n=" << n << " d=" << d << " m=" << m << " l=" << l << ": dim K_l = " << kl << ", dim (K_L)_l = " << kLl
           << ", defect = " << kLl - kl + prev << "  cpu=" << cpuTime() - t0 << endl << flush;
        prev = kl));

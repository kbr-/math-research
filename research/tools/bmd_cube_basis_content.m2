-- Certificate for the diagonal theorem's hypotheses in every odd characteristic (entry-2026-09-26-cube-diagonal-certificate).
--
-- Statement tested.  For (d, rho) in {(2,2), (3,2), (3,3)} on {0,1}^3, m = 4d+rho-1, the solution module
-- K = ker A_m is free on rho homogeneous generators whose excesses sum to N(d,rho) = d^2-1-C(rho,2):
--   over QQ, with minimal generators scaled to primitive integral vectors; the content c (gcd of the integer
--   coefficients of their rho x rho minors) is printed.  For an odd prime p not dividing c the reductions are rho
--   independent solutions over F_p with excess sum N, hence a basis (basis criterion, characteristic != 2);
--   over ZZ/p for the odd primes listed (those dividing some content, and 7 as a control): minimal generators are
--   computed directly, and rho generators of a rank-rho module with excess sum N form a basis.
--
-- A_m: rows T^Q w^r (r in {0,1}^3, 2Q+|r| <= d), columns c = 0..m, entry = coefficient of T^c, with
-- w_i = sum_j C_j y_i^j T^j, C_j = binom(1/2,j) 4^j (integers).  Entry (r, c) is homogeneous of degree c - Q, so the
-- map is graded with source degrees c and target degrees Q.  A component W_c of a solution of excess l has degree
-- l + m - c, so l = deg W_c + c - m for any nonzero component.
Cj = j -> lift((product(toList(0..j-1), i -> (1/2 - i))) / (j!) * 4^j, ZZ);
run1 = (kk, d, rho) -> (
    R := kk[y_1..y_3];
    S := R[T];
    m := 4*d + rho - 1;
    ws := apply(3, i -> sum(toList(0..m), j -> (Cj j) * (sub(R_i, S))^j * T^j));
    rows := flatten flatten flatten flatten apply(toList(0..d//2), Q -> apply(2, a -> apply(2, b -> apply(2, c ->
        if 2*Q + a + b + c <= d then {(Q, a, b, c)} else {}))));
    A := matrix apply(rows, rw -> (
        f := T^(rw#0) * (ws#0)^(rw#1) * (ws#1)^(rw#2) * (ws#2)^(rw#3);
        apply(toList(0..m), cc -> sub(coefficient(T^cc, f + 0*T^(m+1)), R))));
    f0 := map(R^(apply(rows, rw -> -(rw#0))), R^(apply(toList(0..m), c -> -c)), A);
    assert isHomogeneous f0;
    K := mingens kernel f0;
    exc := apply(numcols K, j -> (
        col := K_{j};
        cc := first select(toList(0..m), c -> col_(c,0) != 0);
        first degree col_(cc,0) + cc - m));
    << "  " << toString kk << " (d,rho)=(" << d << "," << rho << ") m=" << m << ": " << numcols K
       << " generators, excesses " << toString exc << ", sum " << sum exc << ", N = " << d^2 - 1 - binomial(rho,2);
    if kk === QQ then (
        cols := apply(numcols K, j -> (
            col := K_{j};
            cs := apply(flatten apply(toList(0..m), c -> flatten entries last coefficients col_(c,0)), x -> lift(x, QQ));
            den := lcm apply(cs, x -> denominator x);
            num := gcd apply(cs, x -> numerator (x * den));
            col * (den / num)));
        M := fold((a, b) -> a | b, cols);
        mins := flatten entries gens minors(numcols M, M);
        allc := apply(flatten apply(mins, f -> flatten entries last coefficients f), x -> lift(x, QQ));
        cont := gcd apply(allc, x -> numerator x);
        << ", content of the " << numcols M << "x" << numcols M << " minors " << cont << " = " << toString factor cont;
    );
    << endl;
    );
for dr in {(2,2), (3,2), (3,3)} do run1(QQ, dr#0, dr#1);
for p in {3, 5, 7} do for dr in {(2,2), (3,2), (3,3)} do run1(ZZ/p, dr#0, dr#1);
exit 0;

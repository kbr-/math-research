-- Reduced triple window (8 October 2026; cycle bmd-20261008-w).  Three roots c1, c2, 1 on a level over a caterpillar of
-- m roots, lambda = 3/2, d = binom(m,2).  With rho_k = k! / prod_(j<k) (j + lambda - m + 1) (a nonzero multiple of
-- Gamma(k+1)/Gamma(k+lambda-m+1)) and p_i the coefficients of ((1+c1 T)(1+c2 T)(1+T))^m, the functionals
-- f_M(e) = sum_(i<=3m) p_i rho_(M-i) e_(M-i), M = d+3m..d+3m+4, kill the 3m single rows T^n (1+aT)^(-3/2) and span
-- their kernel on the columns d..d+3m+4.  So the triple window W3 has full rank iff the 3 x 5 matrix
-- U = (f_M(pair row ab)) has rank 3.  Arguments (optional): a list of m (default {2, 3, 4}) and a prime p (default:
-- compute over QQ); the recorded run used {2,3,4,5} 32003.  Prints, for each m: a sanity check (rank W3 = 3m + rank U, and f_M kills
-- the single rows, at a random rational point), and whether the ideal of 3 x 3 minors of U, saturated by
-- c1 c2 (c1-1)(c2-1)(c1-c2), is the unit ideal over the chosen field.
-- second optional argument: a prime p to compute over ZZ/p instead of QQ
KF = if #scriptCommandLine > 2 then ZZ/(value scriptCommandLine#2) else QQ;
R = KF[c1, c2];
lam = 3/2;
bin = (k) -> (p := 1_R; for i from 0 to k - 1 do p = p * (-lam - i) / (i + 1); p);
single = (a, n, k) -> if k < n then 0_R else bin(k - n) * a^(k - n);
pair = (a, b, k) -> sum(0..k, i -> bin(i) * bin(k - i) * a^i * b^(k - i));
MS = if #scriptCommandLine > 1 then value scriptCommandLine#1 else {2, 3, 4};
for m in MS do (
    d := binomial(m, 2);
    rho := k -> (r := 1_R; for j from 0 to k - 1 do r = r * (j + 1) / (j + lam - m + 1); r);
    T := symbol T;
    S := R[T];
    P := ((1 + c1 * T) * (1 + c2 * T) * (1 + T))^m;
    pc := apply(3 * m + 1, i -> sub(coefficient(T^i, P), R));
    f := (seqf, M) -> sum(0..3 * m, i -> pc#i * rho(M - i) * seqf(M - i));
    prs := {(c1, c2), (c1, 1_R), (c2, 1_R)};
    U := matrix apply(prs, ab -> apply(5, s -> f(k -> pair(ab#0, ab#1, k), d + 3 * m + s)));
    -- sanity at a random point
    pt := map(KF, R, {2/7, -5/3});
    tops := {c1, c2, 1_R};
    singles := flatten apply(tops, a -> apply(m, n -> apply(3 * m + 5, j -> single(a, n, d + j))));
    W := matrix(singles | apply(prs, ab -> apply(3 * m + 5, j -> pair(ab#0, ab#1, d + j))));
    killed := all(flatten flatten apply(tops, a -> apply(m, n -> apply(5, s -> pt f(k -> single(a, n, k), d + 3 * m + s) == 0))), x -> x);
    print("m = " | toString m | ": sanity at (2/7, -5/3): functionals kill single rows " | toString killed
        | ", rank W3 = " | toString rank pt W | ", 3m + rank U = " | toString(3 * m + rank pt U));
    F := c1 * c2 * (c1 - 1) * (c2 - 1) * (c1 - c2);
    I := minors(3, U);
    Sat := saturate(I, F);
    print("m = " | toString m | ": saturated 3 x 3 minor ideal of U is the unit ideal: " | toString(Sat == ideal 1_R)
        | "; degrees of U entries " | toString apply(flatten entries U, e -> if e == 0 then -1 else first degree e));
    );
exit 0

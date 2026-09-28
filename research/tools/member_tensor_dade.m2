-- Member-tensor graded Dade test (odd-prime-truncated-green).
--
-- Statement tested.  Members b = 1..s, each with h value coordinates and a random excluded set
-- E_b in F_3^h (value set V_b = complement); J_b = top ideal of V_b in T(E_b) = F_3[w]/(w^3);
-- M = tensor of the M_b = T(E_b)/J_b = T(E)/(sum J_b).  For an acting space K' spanned by r random
-- linear forms, compute: (a) the degree through which M is free over T(K') (minimal cover count
-- HF(M/K'M) against HF(M)), (b) the degree through which the free prediction HF(M)/(1+t+t^2)^r is
-- nonnegative (the counting margin), and (c) the least, over the nonzero F_3-points kappa of K',
-- of the degree through which M is free along kappa alone.  The member form of
-- conj:graded-dade-margin predicts (a) = min((b), (c)) under a margin; a gap (a) < min((b),(c))
-- is a member-tensor analogue of ex:truncated-dade-special-position.
-- Output: one line per trial.  Usage: M2 --script member_tensor_dade.m2 (parameters below).

kk = ZZ/3;
setRandomSeed 20260928;

-- top ideal of a value set V (list of points of F_3^h) as an ideal of T = kk[w]/(w^3)
topIdeal = (T, h, V) -> (
    mons := select(flatten entries basis(T), m -> true);
    mons = sort(mons, m -> first degree m);
    vals := apply(V, p -> apply(mons, m -> (e := first exponents m; product(h, i -> (p#i)^(e#i)))));
    A := matrix(kk, vals);                    -- |V| x #mons evaluation matrix
    ker0 := gens ker A;                       -- columns: coefficient vectors of vanishing polys
    tops := {};
    maxd := max apply(mons, m -> first degree m);
    for d from 0 to maxd do (
        idxLE := positions(mons, m -> first degree m <= d);
        idxEQ := positions(mons, m -> first degree m == d);
        -- vanishing polys of degree <= d: kernel of A restricted to columns idxLE
        Kd := gens ker A_idxLE;
        if numColumns Kd > 0 then (
            -- top parts in degree d: rows of Kd corresponding to degree-d monomials
            posEQ := apply(idxEQ, i -> position(idxLE, j -> j == i));
            topM := Kd^posEQ;
            for c from 0 to numColumns topM - 1 do (
                f := sum(#idxEQ, k -> topM_(k,c) * mons#(idxEQ#k));
                if f != 0 then tops = append(tops, f)));
    );
    if #tops == 0 then ideal(0_T) else ideal tops
);

ZU = ZZ[u];
powCoeffs = (r, dmax) -> (P := (1 + u + u^2)^r; apply(dmax + 2, j -> coefficient(u^j, P)));

freeThrough = (Mring, forms, r, dmax) -> (
    -- largest j0 such that the minimal free cover over T(K') (K' spanned by forms, r of them)
    -- is bijective in all degrees <= j0: HF(M)_j = sum_i HF(M/K'M)_i [(1+t+t^2)^r]_{j-i}
    hfM := apply(dmax + 2, d -> numColumns basis(d, Mring));
    Q := Mring / ideal apply(forms, f -> promote(f, Mring));
    hfQ := apply(dmax + 2, d -> numColumns basis(d, Q));
    cz := powCoeffs(r, dmax);
    last1 := -1;
    for j from 0 to dmax + 1 do (
        pred := sum(j + 1, i -> hfQ#i * cz#(j - i));
        if pred == hfM#j then last1 = j else break);
    last1
);

predictThrough = (Mring, r, dmax) -> (
    -- largest j0 through which the series HF(M)/(1+t+t^2)^r has nonnegative coefficients
    hfM := apply(dmax + 2, d -> numColumns basis(d, Mring));
    cz := powCoeffs(r, dmax);
    q := {};
    for j from 0 to dmax + 1 do (
        v := hfM#j - sum(j, i -> q#i * cz#(j - i));
        q = append(q, v));
    last1 := -1;
    for j from 0 to dmax + 1 do (if q#j >= 0 then last1 = j else break);
    last1
);

runTrial = (s, h, exSize, r, dmax) -> (
    n := s * h;
    A := kk[w_1..w_n];
    T := A / ideal apply(gens A, v -> v^3);
    wT := gens T;
    Ab := kk[x_1..x_h];
    Tb := Ab / ideal apply(gens Ab, v -> v^3);
    Js := {};
    for b from 0 to s - 1 do (
        pts := apply(3^h, c -> apply(h, i -> (c // 3^i) % 3));
        ex := take(shuffle pts, exSize);
        V := select(pts, p -> not member(p, ex));
        Jb := topIdeal(Tb, h, apply(V, p -> apply(p, a -> a_kk)));
        phi := map(T, Tb, apply(h, i -> wT#(b*h + i)));
        Js = append(Js, phi Jb));
    Mring := T / (sum Js);
    forms := apply(r, i -> sum(n, j -> random(kk) * wT#j));
    a := freeThrough(Mring, forms, r, dmax);
    bb := predictThrough(Mring, r, dmax);
    -- single directions over F_3 points of K'
    coeffs := select(apply(3^r, c -> apply(r, i -> ((c // 3^i) % 3))), v -> any(v, x -> x != 0));
    coeffs = select(coeffs, v -> (first select(v, x -> x != 0)) == 1);  -- projective representatives
    single := min apply(coeffs, v -> (
        k := sum(r, i -> (v#i)_kk * forms#i);
        freeThrough(Mring, {k}, 1, dmax)));
    (a, bb, single)
);

out = "research/results/odd-prime-truncated-green/member_tensor_dade.txt";
f = openOut out;
f << "# s members x h coords, exSize excluded points each, r random acting forms; columns: s h exSize r trial multi_free predicted_positive min_single_free" << endl;
for params in {{3,3,2,3},{3,3,2,4},{3,3,3,4},{3,3,2,5},{4,2,1,3},{4,2,2,4}} do (
    for trial from 1 to 4 do (
        res := runTrial(params#0, params#1, params#2, params#3, 12);
        f << params#0 << " " << params#1 << " " << params#2 << " " << params#3 << " " << trial << " " << res#0 << " " << res#1 << " " << res#2 << endl;
        f << flush));
f << close;

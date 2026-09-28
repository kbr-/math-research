-- Two-direction member tensors (odd-prime-member-pencils).
--
-- Statement tested.  For r = 2 acting forms on random member tensors, the unit-loss conjecture predicts
-- freeness through min(counting, pointwise) - 1; the one-row pencil theorem has no loss.  Every
-- trial also computes the least single-direction freeness degree over the projective F_9-points of
-- K'.  The selection set and the -99 marker are kept from member_tensor_dade_f9.m2 (from which this
-- file was adapted); here every trial is selected, so -99 never occurs.
-- Output: research/results/odd-prime-member-pencils/member_tensor_pencils.txt.
-- Usage: M2 --script member_tensor_pencils.m2  (comment-only edits after the recorded run)

kk = ZZ/3;
setRandomSeed 20260928;

topIdeal = (T, h, V) -> (
    mons := select(flatten entries basis(T), m -> true);
    mons = sort(mons, m -> first degree m);
    vals := apply(V, p -> apply(mons, m -> (e := first exponents m; product(h, i -> (p#i)^(e#i)))));
    A := matrix(kk, vals);
    tops := {};
    maxd := max apply(mons, m -> first degree m);
    for d from 0 to maxd do (
        idxLE := positions(mons, m -> first degree m <= d);
        idxEQ := positions(mons, m -> first degree m == d);
        Kd := gens ker A_idxLE;
        if numColumns Kd > 0 then (
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

-- single direction, stopping after degree cap + 1 (enough to decide whether the value is <= cap)
freeThroughCap = (Mring, hfM, form, cap) -> (
    Q := Mring / ideal {form};
    cz := powCoeffs(1, cap + 1);
    hfQ := {};
    last1 := -1;
    for j from 0 to cap + 1 do (
        hfQ = append(hfQ, numColumns basis(j, Q));
        pred := sum(j + 1, i -> hfQ#i * cz#(j - i));
        if pred == hfM#j then last1 = j else break);
    last1
);

predictThrough = (Mring, r, dmax) -> (
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

k9 = GF(9, Variable => aa);
els9 = {0_k9} | apply(8, i -> aa^i);

runTrial = (s, h, exSize, r, dmax, doF9) -> (
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
    coeffs := select(apply(3^r, c -> apply(r, i -> ((c // 3^i) % 3))), v -> any(v, x -> x != 0));
    coeffs = select(coeffs, v -> (first select(v, x -> x != 0)) == 1);
    single := min apply(coeffs, v -> (
        k := sum(r, i -> (v#i)_kk * forms#i);
        freeThrough(Mring, {k}, 1, dmax)));
    f9 := -99;
    if doF9 then (
        A9 := k9[z_1..z_n];
        T9 := A9 / ideal apply(gens A9, v -> v^3);
        psi := map(T9, T, gens T9);
        M9 := T9 / psi(sum Js);
        forms9 := apply(forms, f -> promote(psi f, M9));
        hfM9 := apply(dmax + 2, d -> numColumns basis(d, M9));
        best := single;
        for c from 0 to 9^r - 1 do (
            v := apply(r, i -> els9#((c // 9^i) % 9));
            nz := select(v, x -> x != 0);
            if #nz > 0 and first nz == 1 then (
                k := sum(r, i -> v#i * forms9#i);
                val := freeThroughCap(M9, hfM9, k, best);
                if val < best then best = val));
        f9 = best);
    (a, bb, single, f9)
);

out = "research/results/odd-prime-member-pencils/member_tensor_pencils.txt";
selected = set flatten apply(8, ci -> apply(4, t -> (ci, t+1)));
f = openOut out;
f << "# columns: s h exSize r trial multi_free predicted_positive min_single_F3 min_single_F9 (-99 = not computed)" << endl;
cfgs = {{3,3,2,2},{3,3,3,2},{4,2,1,2},{4,2,2,2},{2,4,4,2},{2,4,6,2},{3,2,1,2},{5,2,1,2}};
for ci from 0 to #cfgs - 1 do (
    params := cfgs#ci;
    for trial from 1 to 4 do (
        res := runTrial(params#0, params#1, params#2, params#3, 12, member((ci, trial), selected));
        f << params#0 << " " << params#1 << " " << params#2 << " " << params#3 << " " << trial << " " << res#0 << " " << res#1 << " " << res#2 << " " << res#3 << endl;
        f << flush));
f << close;

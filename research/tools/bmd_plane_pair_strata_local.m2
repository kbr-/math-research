-- Local structure of the polar colon at the two-pair collision strata on a random plane (cycle bmd-20261009-kaq).
-- Input: plane files of research/tools/bmd_plane_minors.cpp (minorList, extraK, collisionForms ordered a_1..a_4,
-- then a_i - a_j for i < j). The two-pair strata {a_i = 0, a_j = a_k} and {a_i = a_j, a_k = a_l} meet the plane at the
-- intersection of their two collision lines. Question (Kapranov boundary lead): what are F, m1, k locally there, and
-- what are the local lengths of L = (F, m1) : k (= T_d on the plane, lem:cube-taylor-colon-formula) and of
-- CI = (F, m1)?  Printed per stratum point: the orders of F, m1, k (lowest degree in coordinates centred at the
-- point), the factorization of the lowest-degree form of each in the two collision line forms, and the local
-- lengths, computed as degree I - degree saturate(I, m_p).
-- Usage: M2 --script bmd_plane_pair_strata_local.m2 IN1.m2 P1 [IN2.m2 P2 ...]   (one series run)
args = drop(scriptCommandLine, 1);
for i from 0 to #args // 2 - 1 do (
    file := args#(2*i); p := value args#(2*i+1);
    R := ZZ/p[x, y];
    use R;
    load file;
    N := #minorList - 1;
    F := minorList#N; m1 := minorList#(N-1); k := extraK;
    CI := ideal(F, m1);
    L := CI : k;
    print(file | ": degrees " | toString {first degree F, first degree m1, first degree k} | ", lengths CI "
          | toString degree CI | ", L " | toString degree L);
    -- strata: a_i and a_j - a_k with i, j, k distinct (forms t and 4 + pair index), and disjoint pairs
    pairs := {{0,1},{0,2},{0,3},{1,2},{1,3},{2,3}};
    strata := flatten for t from 0 to 3 list for q from 0 to 5 list (
        if member(t, pairs#q) then continue else {t, 4 + q});
    strata = strata | flatten for q from 0 to 5 list for q2 from q + 1 to 5 list (
        if #(set(pairs#q) * set(pairs#q2)) > 0 then continue else {4 + q, 4 + q2});
    for st in strata do (
        l1 := collisionForms#(st#0); l2 := collisionForms#(st#1);
        mp := ideal(l1, l2);
        -- coordinates centred at the point: u = l1, v = l2 (an affine change of coordinates)
        S := ZZ/p[u, v];
        co := g -> {sub(coefficient(x, g), ZZ/p), sub(coefficient(y, g), ZZ/p), sub(sub(g, {x => 0, y => 0}), ZZ/p)};
        (c1, c2, c0) := toSequence co l1; (e1, e2, e0) := toSequence co l2;
        det0 := c1 * e2 - c2 * e1;
        -- x, y from l1 = u, l2 = v by Cramer's rule
        inv := det0^-1;
        phi := map(S, R, {inv * (e2 * (S_0 - c0) - c2 * (S_1 - e0)), inv * (c1 * (S_1 - e0) - e1 * (S_0 - c0))});
        local1 := g -> (h := phi g; low := min apply(terms h, first @@ degree); (low, factor sum select(terms h, s -> first degree s == low)));
        lenAt := I -> degree I - degree saturate(I, mp);
        (oF, cF) := local1 F; (oM, cM) := local1 m1; (oK, cK) := local1 k;
        print("  " | toString st | ": orders F " | toString oF | ", m1 " | toString oM | ", k " | toString oK
              | "; lengths L " | toString lenAt L | ", CI " | toString lenAt CI);
        print("     cones F " | toString cF | " | m1 " | toString cM | " | k " | toString cK);
        ));

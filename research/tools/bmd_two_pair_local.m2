-- Local structure of the first-step forms at the collision points of a random plane (cycle bmd-20261009-kgu).
-- Input: files written by research/tools/bmd_plane_minors.cpp (F = minorList#N, m1 = minorList#(N-1), k = extraK,
-- collisionForms = a_1..a_4, then a_i - a_k, i < k).  Collision form j corresponds to a pair of the five points
-- 0, a_1, ..., a_4: {0, i} for a_i, {i, k} for a_i - a_k.  Two forms meet at a two-pair point when their pairs are
-- disjoint (15 points, one orbit of the five-point symmetry S_5) and at a triple point otherwise (10 points, one
-- orbit).  So one point of each type suffices: forms (0, 9) (pairs {0,1}, {3,4}) and (0, 1) (pairs {0,1}, {0,2}).
-- In local coordinates u = l1, v = l2 (the two collision forms through the point) it prints, for F, m1 and k: the
-- order at the point and the lowest homogeneous part (tangent cone), factored.  With LEN=1 it also prints the local
-- lengths of (F, m1) and (F, m1) : k at the point (length of I + m^NN, NN = 60), feasible at small degree only.
-- Usage: M2 --script bmd_two_pair_local.m2 IN1.m2 P1 LEN1 [IN2.m2 P2 LEN2 ...]   (one series run)
args = drop(scriptCommandLine, 1);
for i from 0 to #args // 3 - 1 do (
    file := args#(3*i); p := value args#(3*i+1); withLen := value args#(3*i+2);
    R := ZZ/p[x, y];
    use R;
    load file;
    kk := coefficientRing R;
    N := #minorList - 1;
    F := minorList#N; m1 := minorList#(N-1); k := extraK;
    print(file | ": degrees F " | toString first degree F | ", m1 " | toString first degree m1 | ", k " | toString first degree k);
    for jj in {(0, 9, "two-pair"), (0, 1, "triple")} do (
        l1 := collisionForms#(jj#0); l2 := collisionForms#(jj#1);
        cf := l -> apply({x, y, 1_R}, mo -> lift(coefficient(mo, l), kk));
        c1 := cf l1; c2 := cf l2;
        A := matrix{{c1#0, c1#1}, {c2#0, c2#1}}; c := matrix{{c1#2}, {c2#2}};
        -- work modulo (u, v)^TRUNC: only the lowest homogeneous part is needed, and the full expansion of a
        -- degree-115 form under a translation is what made the d = 4 run slow
        S0 := kk[u, v]; TRUNC := 16;
        S := S0 / (ideal(u, v))^TRUNC;
        xy := (inverse A) * (matrix{{u}, {v}} - sub(c, S));
        toUV := map(S, R, {xy_(0,0), xy_(1,0)});
        cone := f -> (g := lift(toUV f, S0);
                      if g == 0 then error("order at least " | toString TRUNC);
                      o := min apply(terms g, t -> first degree t);
                      (o, sum select(terms g, t -> first degree t == o)));
        print("  " | jj#2 | " point (forms " | toString jj#0 | "," | toString jj#1 | "), local coordinates u, v = the two collision forms:");
        for fm in {("F", F), ("m1", m1), ("k", k)} do (
            (o, t) := cone fm#1;
            print("    " | fm#0 | ": order " | toString o | ", tangent cone factors " | toString toList factor t);
            );
        if withLen == 1 then (
            P := first entries transpose ((inverse A) * (-c));
            mP := ideal(x - P#0, y - P#1);
            CI := ideal(F, m1);
            print("    local lengths: (F, m1) " | toString degree(CI + mP^60) | ", colon " | toString degree((CI : k) + mP^60));
            );
        );
    );

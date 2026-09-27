-- Pair defects by relation type among the free parts (entry-2026-09-27-pair-relations).
--
-- Statement tested.  In a Jordan block of the one-row algebra for a pair of tops tau1 = A^2 B, tau2 = C^2 E whose
-- free parts satisfy one linear relation mu (a nonzero vector in F_3^4, up to scalars), the block is
-- T3 (x) N with T3 = F_3[x1,x2,x3]/(x_i^3) carrying the four forms as the images of the basis of F_3^4/<mu>, and N the
-- non-free part, on which the relation's combination acts (prop:free-part-criterion's proof).  Two cases of N:
-- "pure", N = F_3 (the groups of the relation contribute J_1 blocks, on which it acts as 0), and "j2", N =
-- F_3[u]/(u^2) with the relation's combination equal to u (one J_2 block).  For every mu the script computes the
-- pair's Taylor defect, dim Syz_e - dim (Frobenius syzygies + Koszul pairs)_e, in every multiplier degree e.
-- Usage: M2 --script pair_relation_types.m2 OUT
out := scriptCommandLine#1;
f := openOut out;
kk := ZZ/3;
mus := select(toList((0,0,0,0)..(2,2,2,2)), m -> m != (0,0,0,0) and (first select(toList m, c -> c != 0)) == 1);
for mode in {"pure", "j2"} do for mu in mus do (
    -- rows of M: a basis of the vectors orthogonal to mu, so that M mu = 0 and rank M = 3
    Mfull := matrix{toList mu};
    K := gens ker (map(kk^1, kk^4, sub(Mfull, kk)));
    Mt := transpose K; -- 3 x 4, kernel mu
    R := if mode == "pure" then kk[x1,x2,x3,Degrees=>{1,1,1}] else kk[x1,x2,x3,u];
    I := if mode == "pure" then ideal(x1^3, x2^3, x3^3) else ideal(x1^3, x2^3, x3^3, u^2);
    Q := R / I;
    xs := {x1, x2, x3};
    L := apply(4, j -> sum(3, i -> sub(Mt_(i, j), Q) * sub(xs#i, Q)));
    -- in mode j2 the relation's combination sum mu_j L_j must equal u: add u times a correction to one form with mu_j != 0
    if mode == "j2" then (
        j0 := first select(4, j -> mu#j != 0);
        c := sub(lift(1/(sub(mu#j0, kk)), kk), Q);
        L = apply(4, j -> if j == j0 then L#j + c * sub(u, Q) else L#j);
    );
    A := L#0; B := L#1; C := L#2; E := L#3;
    t1 := A^2 * B; t2 := C^2 * E;
    G := matrix{{t1, t2}};
    S := ker map(Q^1, Q^{-3,-3}, G);
    T := image map(Q^{-3,-3}, , matrix{{A, B^2, 0, 0, t2}, {0, 0, C, E^2, -t1}});
    top := if mode == "pure" then 6 else 7;
    defs := apply(toList(3..(top+3)), d -> numcols basis(d, S) - numcols basis(d, T));
    zero := (t1 == 0 or t2 == 0);
    f << "{\"mode\": \"" << mode << "\", \"mu\": [" << concatenate between(", ", apply(toList mu, toString))
      << "], \"weight\": " << #select(toList mu, c -> c != 0) << ", \"top_zero\": " << (if zero then "true" else "false")
      << ", \"defect_by_multiplier_degree\": [" << concatenate between(", ", apply(defs, toString)) << "]}" << endl;
    );
close f;

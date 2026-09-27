-- Block types of a single top A^2 B (entry-2026-09-27-single-top-blocks).
--
-- Statement tested.  On one row over F_3, scaling cells puts two forms in the shape A = u1 + u3 + u4,
-- B = u2 + u3 + 2 u4, with u_k the sum of the cells of group k (A only, B only, A + B, A + 2B).  The square-free
-- algebra is a sum of shifted cyclic modules P_r = F_3[u1..u4]/(u_k^{r_k}), r in {1,2,3}^4 (Jordan blocks of each
-- group's algebra over F_3[u_k]/(u_k^3)), so the single top's Taylor defect is a sum over the blocks that occur of
-- the defect of P_r: dim [ann_{P_r}(A^2 B) / (A, B^2) P_r] in each degree.  This script computes that defect for
-- all 81 types r, degree by degree.
-- Usage: M2 --script single_top_block_types.m2 OUT
out := scriptCommandLine#1;
f := openOut out;
kk := ZZ/3;
for r in toList((1,1,1,1)..(3,3,3,3)) do (
    R := kk[u1,u2,u3,u4];
    P := R / ideal(u1^(r#0), u2^(r#1), u3^(r#2), u4^(r#3));
    A := sub(u1 + u3 + u4, P); B := sub(u2 + u3 + 2*u4, P);
    tau := A^2 * B;
    ann := ideal(0_P) : ideal(tau);
    T := ideal(A, B^2);
    top := sum toList r - 4;
    defs := apply(toList(0..top), d -> numcols basis(d, ann) - numcols basis(d, T));
    f << "{\"r\": [" << concatenate between(", ", apply(toList r, toString)) << "], \"defect_by_degree\": ["
      << concatenate between(", ", apply(defs, toString)) << "]}" << endl;
    );
close f;

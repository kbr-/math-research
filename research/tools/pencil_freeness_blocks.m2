-- Freeness failure of pencil blocks (entry-2026-09-27-pencil-graded-dade).
--
-- Statement tested.  On one row over F_3, two forms A = u1 + u3 + u4, B = u2 + u3 + 2 u4 (u_k the sum of group k)
-- act on each Jordan block P_r = F_3[u1..u4]/(u_k^{r_k}), r in {1,2,3}^4.  For every type r the script computes the
-- first degree d at which dim(P_r/(A,B)P_r)_d differs from the free prediction, the coefficient of q^d in
-- HS(P_r)/(1+q+q^2)^2 (prop:syzygies-as-tor's test over T = F_3[A,B]/(A^3,B^3)), or reports the block free.
-- Usage: M2 --script pencil_freeness_blocks.m2 OUT
out := scriptCommandLine#1;
f := openOut out;
kk := ZZ/3;
for r in toList((1,1,1,1)..(3,3,3,3)) do (
    R := kk[u1,u2,u3,u4];
    P := R / ideal(u1^(r#0), u2^(r#1), u3^(r#2), u4^(r#3));
    A := sub(u1 + u3 + u4, P); B := sub(u2 + u3 + 2*u4, P);
    top := sum toList r - 4;
    hs := apply(toList(0..top+3), d -> numcols basis(d, P));
    -- free prediction: hs / (1+q+q^2)^2, coefficientwise
    w := hs;
    for rep from 1 to 2 do (
        q := new MutableList from apply(#w, i -> 0);
        for d from 0 to #w - 1 do (
            v := w#d; if d >= 1 then v = v - q#(d-1); if d >= 2 then v = v - q#(d-2); q#d = v);
        w = toList q);
    Q := P / ideal(A, B);
    quo := apply(toList(0..top+3), d -> numcols basis(d, Q));
    diff := select(toList(0..top+3), d -> quo#d != w#d);
    first := if #diff == 0 then -1 else min diff;
    f << "{\"r\": [" << concatenate between(", ", apply(toList r, toString)) << "], \"first_failure\": " << first << "}" << endl;
    );
close f;

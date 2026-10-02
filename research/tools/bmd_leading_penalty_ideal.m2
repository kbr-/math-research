-- Leading Hankel penalty test (8 October 2026; cycle bmd-20261008-zv).
-- Tested statement (conj:cube-leading-hankel-penalty): for 1 <= p <= M - 1, k = M - p, and every set Lambda+ of
-- 2M - p nonnegative integers, D = det of the rows i in Lambda+: (h_(t+i-M+1)(y))_(t<M), (h_(t+i-M+2)(y)/(i+1))_(t<k)
-- lies in I_k = ideal(Vand(y_S)^2 : |S| = k + 1). (By lem:cube-cross-leading-coefficient, D is the leading
-- coefficient of every cross coordinate with p negative indices, divided by Vand(y)^2 and a constant.)
-- All Lambda+ inside [0, R]. Prints per (M, p) the number of nonzero D and of violations.
out = "research/results/bmd-20261008-zv/leading-penalty-ideal.txt";
f = openOut out;
emit = s -> (print s; f << s << endl);
vand = l -> product(subsets(l, 2), p -> p_0 - p_1);
for M from 3 to 5 do (
  Y := QQ[y_1..y_M];
  R := 2*M + 1;
  hh := new MutableHashTable;
  hc := n -> if n < 0 then 0_Y else (if not hh#?n then hh#n = sum(compositions(M, n), a -> product(M, i -> Y_i^(a_i))); hh#n);
  for p from 1 to M - 1 do (
    k := M - p;
    G := gb ideal apply(subsets(gens Y, k + 1), T -> (vand T)^2);
    cnt := 0; bad := 0;
    scan(subsets(toList(0..R), 2*M - p), Lp -> (
      D := det matrix apply(Lp, i -> apply(toList(0..M-1), t -> hc(t + i - M + 1)) | apply(toList(0..k-1), t -> (1/(i+1)) * hc(t + i - M + 2)));
      if D != 0 then (cnt = cnt + 1; if D % G != 0 then (bad = bad + 1; emit("  violation M=" | toString M | " Lambda+=" | toString Lp)))));
    emit("M = " | toString M | ", p = " | toString p | ", k = " | toString k | ": " | toString cnt | " nonzero D; violations: " | toString bad);
  );
);
close f;

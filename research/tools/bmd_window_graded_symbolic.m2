-- Window graded coefficients (9 October 2026; cycle bmd-20261009-b).
-- Computes, for M = 3 and each window Lambda_p = [-p, 2M-1-p] (1 <= p <= M), the u^(B_p+t) coefficients of the
-- cherry cross coordinate (x = 1, eps = u, lambda = 3/2), t = 0..T, divides by Vand(y)^2, and reports for each:
-- the largest k' with membership in I_k' = (Vand(y_S)^2 : |S| = k'+1), and the factorization of the quotient.
-- Question: is there a closed form (a graded Hankel form) for the windows' higher coefficients?
M = value(getenv "MM"); TT = value(getenv "TT");
out = "research/results/bmd-20261009-b/window-graded-M" | toString M | ".txt";
f = openOut out;
emit = s -> (print s; f << s << endl);
c = n -> product(toList(0..n-1), i -> (-3/2 - i)/(i + 1));
vand = l -> product(subsets(l, 2), p -> p_0 - p_1);
for p from 1 to M do (
  k := M - p; B := p^2 - p + M; K := B + TT;
  S := QQ[u, y_1..y_M]; R := S / ideal(u^(K + 1));
  cols := toList(-p..2*M-1-p);
  Vr := s -> apply(cols, t -> if t >= 0 then sub(c(t), R) * (R_s)^t else 0_R);
  Qr := s -> apply(cols, t -> sum(toList(max(1, -t)..K), m -> sub(c(m) * c(t + m), R) * (R_0)^m * (R_s)^(t + m)));
  D := lift(det matrix(apply(toList(1..M), s -> Vr s) | apply(toList(1..M), s -> Qr s)), S);
  Y := QQ[y_1..y_M]; toY := map(Y, S, {0_Y} | gens Y);
  V2 := (vand gens Y)^2;
  for t from 0 to TT do (
    g := toY(sub(diff(S_0^(B+t), D), {S_0 => 0}) / ((B+t)!));
    if g == 0 then (emit("p = " | toString p | ", t = " | toString t | ": zero"); continue);
    q := g // V2;
    if q * V2 != g then (emit("p = " | toString p | ", t = " | toString t | ": NOT divisible by Vand^2"); continue);
    kk := 0; scan(toList(1..M-1), k2 -> if (q % ideal apply(subsets(gens Y, k2 + 1), T -> (vand T)^2)) == 0 then kk = k2);
    emit("p = " | toString p | ", k = " | toString k | ", t = " | toString t | ": deg " | toString((degree q)_0) |
      ", in I_" | toString kk | "; factors: " | toString(factor q));
  );
);
close f;

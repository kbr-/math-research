-- Exact Hankel form of the cherry window coefficients at M = 4 (8 October 2026; cycle bmd-20261008-zn).
-- Tested statement (conj:cube-cherry-hankel-coefficient at M = 4, j = 2, 3; j = 1, 4 are controls): with lambda = 3/2, c_n = binom(-3/2, n),
-- rows V_s = sum c_t y_s^t w^t and Q_s = (U_u - 1) V_s, U_u = (1 + u/w)^(-lambda) (thm:cube-cherry-lattice-splitting, at
-- x = 1, eps = u), the coefficient of u^(B_j), B_j = j^2 - j + 4, in the Pluecker coordinate on the window
-- Lambda_j = [-j, 7-j] equals c * Vand(y)^2 * Hank_(4-j)(y), Hank_k = sum over (k+1)-subsets of Vand^2, c a nonzero rational.
-- Computed exactly in QQ[u, y_1..y_4]/(u^(B_j + 1)); prints the quotient and whether the division is exact.
-- Controls: j = 1 (L_1 proportional to Vand^2, proved) and j = 4 (L_4 constant, proved).
c = n -> product(toList(0..n-1), i -> (-3/2 - i)/(i + 1));
out = "research/results/bmd-20261008-zn/hankel-form-m4.txt";
f = openOut out;
emit = s -> (print s; f << s << endl);
for j in {1, 2, 3, 4} do (
  B := j^2 - j + 4;
  S := QQ[u, y_1..y_4];
  R := S / ideal(u^(B + 1));
  cols := toList(-j..7-j);
  Vr := s -> apply(cols, t -> if t >= 0 then sub(c(t), R) * (R_s)^t else 0_R);
  Qr := s -> apply(cols, t -> sum(toList(max(1, -t)..B), m -> sub(c(m) * c(t + m), R) * (R_0)^m * (R_s)^(t + m)));
  Mx := matrix(apply(toList(1..4), s -> Vr s) | apply(toList(1..4), s -> Qr s));
  D := lift(det Mx, S);
  L := sub(contract(S_0^B, D), {S_0 => 0});
  yy := toList(1..4) / (i -> S_i);
  vand := l -> product(subsets(l, 2), p -> p_0 - p_1);
  k := 4 - j;
  hank := sum(subsets(yy, k + 1), T -> (vand T)^2);
  target := (vand yy)^2 * hank;
  q := L // target;
  emit("j = " | toString j | ", k = " | toString k | ", B = " | toString B | ": L Vand^2 nonzero: " | toString(L != 0) |
       "; exact division by Vand^2 Hank_k: " | toString(L % target == 0) | "; quotient " | toString q);
);
close f;

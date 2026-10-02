-- Hankel penalty ideal test (8 October 2026; cycle bmd-20261008-zv).
-- Tested statement (conjecture): in the cherry cross block (lambda = 3/2, c_n = binom(-3/2, n), x = 1, eps = u;
-- rows V_s = sum c_t y_s^t w^t, Q_s = (U_u - 1) V_s), for every coordinate set Lambda of 2M columns with p negative
-- indices, every u-coefficient of P_Lambda is Vand(y)^2 G with
--   G in I_k = ideal(Vand(y_S)^2 : |S| = k + 1), k = M - p, when p >= 1;
--   G in ideal(e_M(y)^2) when p = 0.
-- Exact in QQ[u, y]/(u^(K+1)); Q-entries truncated at u^K, exact for coefficients up to u^K.
-- Prints, per p, the number of nonzero sets and the number of sets violating the membership.
M = value(getenv "MM");
K = value(getenv "KK");
T0 = value(getenv "T0"); T1 = value(getenv "T1");
out = "research/results/bmd-20261008-zv/hankel-penalty-ideal-M" | toString M | ".txt";
f = openOut out;
emit = s -> (print s; f << s << endl);
c = n -> product(toList(0..n-1), i -> (-3/2 - i)/(i + 1));
S = QQ[u, y_1..y_M];
R = S / ideal(u^(K + 1));
cols = toList(T0..T1);
Vr = s -> apply(cols, t -> if t >= 0 then sub(c(t), R) * (R_s)^t else 0_R);
Qr = s -> apply(cols, t -> sum(toList(max(1, -t)..K), m -> sub(c(m) * c(t + m), R) * (R_0)^m * (R_s)^(t + m)));
Mx = matrix(apply(toList(1..M), s -> Vr s) | apply(toList(1..M), s -> Qr s));
yy = toList(1..M) / (i -> S_i);
vand = l -> product(subsets(l, 2), p -> p_0 - p_1);
V2 = (vand yy)^2;
Y = QQ[y_1..y_M];
toY = map(Y, S, {0_Y} | gens Y);
Ik = k -> if k >= M then ideal(0_Y) else ideal apply(subsets(gens Y, k + 1), T -> (vand T)^2);
I0 = ideal((product gens Y)^2);
ideals = hashTable apply(toList(0..M), p -> p => if p == 0 then I0 else Ik(M - p));
gbs = hashTable apply(keys ideals, p -> p => gb ideals#p);
cnt = new MutableHashTable; bad = new MutableHashTable; TAL = new MutableHashTable;
scan(subsets(#cols, 2*M), Sset -> (
  L := Sset / (i -> cols_i);
  p := #select(L, t -> t < 0);
  if p <= M then (
    D := lift(det Mx_Sset, S);
    if D != 0 then (
      cnt#p = (if cnt#?p then cnt#p else 0) + 1;
      ok := true; first := -1; firstbad := -1;
      cfs := apply(toList(0..K), n -> toY(sub(diff(S_0^n, D), {S_0 => 0}) / (n!)));
      scan(#cfs, n -> (g := cfs_n; if g != 0 then (
        if first < 0 then first = n;
        q := g // toY(V2);
        kk := -1;
        if q * toY(V2) == g then (kk = 0; scan(toList(1..M-1), k2 -> if (q % gb Ik(k2)) == 0 then kk = k2));
        key := (p, n - first, kk);
        TAL#key = (if TAL#?key then TAL#key else 0) + 1)));
    ))));
scan(sort keys TAL, key -> emit("p, t = n - leading, largest k with G in I_k: " | toString key | ": " | toString TAL#key | " coefficients"));
scan(sort keys cnt, p -> emit("M = " | toString M | ", p = " | toString p | ": " | toString cnt#p | " nonzero sets; violations: " | toString(if bad#?p then bad#p else 0)));
close f;

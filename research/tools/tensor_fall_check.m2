-- Does the tensor dependency give a cross-member fall modulo closed members? Model: the base is all of F_3^r (the
-- forms' value space), functions are elements of Q = F_3[y_1..y_r]/(y^3 - y). A member b has affine prefix forms
-- P_1..P_{c-1} and a non-prefix form L; its clause C_b = (1 - L^2) prod P_i^2 is the indicator of its excluded set
-- E_b = {L = 0, P_i != 0}; its closed member's elements of degree <= d are the functions of degree <= d supported on
-- E_b (they vanish on the allowed set). For a family whose clause tops cancel (sum of tops = 0), the clause sum
-- F = sum_b C_b has degree <= d = 2c - 1. Question: is F in the sum over b of the closed members' degree-<= d parts?
-- If not, the dependency is a cross-member fall that closed members do not absorb.
-- Families: (a) the tensor family w (x) F_3^2, w in PG(2,3) (13 members, c = 2, r = 6); (b) the lifted pencil
-- Z + <w . x>, w in PG(1,3) (4 members, c = 2, r = 3); (c) the lifted tensor family Z + w (x) F_3^2, w in PG(2,3)
-- (13 members, c = 3, r = 7). Random constants and random prefix combinations (seeded); each prefix combination
-- has a nonzero coefficient on a form independent of L, so each top is minus the omega of the member's span.
kk = ZZ/3;
projPts = m -> (L := {}; scan(3^m, t -> (v := apply(m, i -> (t // 3^i) % 3);
  nz := select(m, i -> v#i != 0); if #nz > 0 and v#(first nz) == 1 then L = append(L, v))); L);
fallTest = (name, r, c, members) -> (
  R := kk[y_1..y_r];
  Q := R/ideal(apply(gens R, v -> v^3 - v));
  d := 2 * c - 1;
  mons := flatten apply(toList(0..d), e -> flatten entries basis(e, R));
  mons = select(mons, mm -> all(first exponents mm, a -> a <= 2));
  toQ := p -> sub(p, Q);
  allMons := select(flatten entries basis(0, 2 * r, R), mm -> all(first exponents mm, a -> a <= 2));
  coeffs := (f, ml) -> lift(last coefficients(matrix{{lift(f, R)}}, Monomials => ml), kk);
  mems := apply(members, mb -> apply(mb, p -> toQ(p(R))));
  clauses := apply(mems, mb -> (1 - (last mb)^2) * product(drop(mb, -1), p -> p^2));
  F := sum clauses;
  degF := if F == 0 then -1 else first degree lift(F, R);
  allB := apply(#mems, b -> (
    off := 1 - clauses#b;
    img := lift(last coefficients(matrix{apply(mons, mm -> lift(toQ(mm) * off, R))}, Monomials => allMons), kk);
    gens ker img));
  V := fold(allB, (a, b) -> a | b);
  rV := rank V;
  inSpan := if degF > d then "n/a (degree too high)" else toString(rank(V | coeffs(F, mons)) == rV);
  print(name | ": members=" | toString(#mems) | " deg(clause sum)=" | toString degF | " (d=" | toString d |
    ") dims of closed members' parts=" | toString unique apply(allB, numColumns) | " rank of their sum=" | toString rV |
    " clause sum absorbed: " | inSpan));
randNZ = () -> (x := 0_kk; while x == 0 do x = random kk; x);
-- (a) tensor family c = 2, m = 3: forms f1 = w . y_{1..3} + a1, f2 = w . y_{4..6} + a2; prefix P = s f1 + t f2 (s != 0); L = f2
famA = () -> apply(projPts 3, w -> (a1 := random kk; a2 := random kk; s := randNZ(); t := random kk;
  {R -> (f1 := sum(3, i -> w#i * R_i) + a1; f2 := sum(3, i -> w#i * R_(3 + i)) + a2; s * f1 + t * f2),
   R -> sum(3, i -> w#i * R_(3 + i)) + a2}));
-- (b) lifted pencil c = 2: forms g = y_1 + b0 (the Z form, with a member constant), f = w . (y_2, y_3) + a
famB = () -> apply(projPts 2, w -> (b0 := random kk; a := random kk; s := randNZ(); t := random kk;
  {R -> s * (R_0 + b0) + t * (w#0 * R_1 + w#1 * R_2 + a), R -> w#0 * R_1 + w#1 * R_2 + a}));
-- (c) lifted tensor c = 3: forms g = y_1 + b0, f1 = w . y_{2..4} + a1, f2 = w . y_{5..7} + a2; prefixes: two random
-- combinations whose coefficient matrix on (g, f1) is invertible; L = f2
famC = () -> apply(projPts 3, w -> (b0 := random kk; a1 := random kk; a2 := random kk;
  M := random(kk^2, kk^3); while rank M_{0, 1} < 2 do M = random(kk^2, kk^3);
  forms := R -> {R_0 + b0, sum(3, i -> w#i * R_(1 + i)) + a1, sum(3, i -> w#i * R_(4 + i)) + a2};
  {R -> sum(3, j -> M_(0, j) * (forms R)#j), R -> sum(3, j -> M_(1, j) * (forms R)#j), R -> (forms R)#2}));
scan({1, 2}, s -> (setRandomSeed s; fallTest("(a) tensor c=2 m=3, seed " | toString s, 6, 2, famA())));
scan({1, 2}, s -> (setRandomSeed s; fallTest("(b) lifted pencil c=2, seed " | toString s, 3, 2, famB())));
scan({1}, s -> (setRandomSeed s; fallTest("(c) lifted tensor c=3 m=3, seed " | toString s, 7, 3, famC())));
exit 0

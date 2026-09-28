-- Cube-model test of conj:span-local-generation on tensor families (families and model as in tensor_fall_check.m2:
-- base = value space F_3^r of the forms, functions in Q = F_3[y]/(y^3 - y), clause C_b = (1 - L^2) prod P_i^2, the
-- indicator of the excluded set E_b). The tensor clause sum F has degree <= 2c - 1; it is tested against the closed
-- members of clause sets S of smaller span (see below).
kk = ZZ/3;
projPts = m -> (L := {}; scan(3^m, t -> (v := apply(m, i -> (t // 3^i) % 3);
  nz := select(m, i -> v#i != 0); if #nz > 0 and v#(first nz) == 1 then L = append(L, v))); L);
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
-- Span-local generation test (conj:span-local-generation, cube model). For the tensor families of
-- tensor_fall_check.m2, the clause sum F (degree <= d = 2c-1) is tested against the sum, over clause sets S, of the
-- closed members' degree-<= d parts: functions of degree <= d vanishing on the intersection of the allowed sets of S,
-- i.e. killed by prod_{b in S} (1 - C_b). The sets S are the members w on a line of PG(2,3), the largest subfamilies
-- inside a proper subspace of the family's span (a hyperplane contains the members of one line or a single member).
-- Control: S = the whole family absorbs F (F vanishes where all clauses hold).
setTest = (name, r, c, members, sets) -> (
  R := kk[y_1..y_r];
  Q := R/ideal(apply(gens R, v -> v^3 - v));
  d := 2 * c - 1;
  mons := select(flatten apply(toList(0..d), e -> flatten entries basis(e, R)), mm -> all(first exponents mm, a -> a <= 2));
  allMons := select(flatten entries basis(0, 2 * r, R), mm -> all(first exponents mm, a -> a <= 2));
  toQ := p -> sub(p, Q);
  mems := apply(members, mb -> apply(mb, p -> toQ(p(R))));
  clauses := apply(mems, mb -> (1 - (last mb)^2) * product(drop(mb, -1), p -> p^2));
  F := sum clauses;
  fvec := lift(last coefficients(matrix{{lift(F, R)}}, Monomials => mons), kk);
  part := S -> (off := product(S, b -> 1 - clauses#b);
    gens ker lift(last coefficients(matrix{apply(mons, mm -> lift(toQ(mm) * off, R))}, Monomials => allMons), kk));
  Vs := apply(sets, part);
  V := fold(Vs, (a, b) -> a | b);
  Vall := part toList(0..#mems-1);
  print(name | ": members=" | toString(#mems) | " sets=" | toString(#sets) | " dims of parts=" | toString unique apply(Vs, numColumns) |
    " rank of sum=" | toString rank V | " clause sum absorbed by the sets: " | toString(rank(V | fvec) == rank V) |
    "; control, whole family absorbs: " | toString(rank(Vall | fvec) == rank Vall)));
pts3 = projPts 3;
lines3 = unique apply(subsets(#pts3, 2), pr -> (a := pts3#(pr#0); b := pts3#(pr#1);
  sort select(#pts3, i -> (M := matrix(kk, {a, b, pts3#i}); rank M == 2))));
print("lines of PG(2,3): " | toString(#lines3) | ", sizes " | toString unique apply(lines3, l -> #l));
scan({1, 2}, s -> (setRandomSeed s; setTest("(a) tensor c=2 m=3, seed " | toString s, 6, 2, famA(), lines3)));
scan({1}, s -> (setRandomSeed s; setTest("(c) lifted tensor c=3 m=3, seed " | toString s, 7, 3, famC(), lines3)));
exit 0

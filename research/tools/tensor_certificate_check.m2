-- Certificate test for conj:global-tensor-falls (graded, cube model). Same families and line sets as
-- tensor_graded_check.m2. Candidate certificates: mu_T(g) = coefficient of prod y_i^2 in g*T, T = y * omega_Y, where
-- Y (dimension r - c) meets the non-prefix column space Zc = span{w . z} (the l_b) in a hyperplane H and y lies in
-- Zc outside H, so every l_b lies in Y + <y>; the other dim(Y) - 2 basis vectors of Y are taken from the remaining
-- coordinate blocks. Such mu_T kills every single member's leading forms l_b^2 pi_b G_{c-2} (prop:leading-fall-form).
-- Reported: how many candidates also kill the line sets' graded closed parts, and how many of those are nonzero on phi.
kk = ZZ/3;
projPts = m -> (L := {}; scan(3^m, t -> (v := apply(m, i -> (t // 3^i) % 3);
  nz := select(m, i -> v#i != 0); if #nz > 0 and v#(first nz) == 1 then L = append(L, v))); L);
subsetsRREF = (n, k) -> (L := {};
  scan(subsets(n, k), piv -> (
    fr := flatten apply(k, rr -> apply(select(toList(piv#rr+1..n-1), j -> not member(j, piv)), j -> (rr, j)));
    scan(toList(0..3^(#fr)-1), t -> (M := mutableMatrix(kk, k, n);
      scan(k, rr -> M_(rr, piv#rr) = 1_kk); scan(#fr, f -> M_(fr#f) = ((t // 3^f) % 3)_kk);
      L = append(L, matrix M))))); L);
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
  top := diagonalMatrix(kk, apply(mons, mm -> if first degree mm == d then 1 else 0));
  grV := top * V; grF := top * fvec;
  topMon := product(gens R, v -> v^2);
  A := R/ideal(apply(gens R, v -> v^3));
  dmons := select(mons, mm -> first degree mm == d);
  zc := toList(r - 3 .. r - 1);
  others := toList(0 .. r - 4);
  -- hyperplanes H of Zc: kernels of nonzero functionals on the three z-coordinates (one per projective point)
  Hs := apply(projPts 3, u -> (K := gens ker matrix(kk, {u}); apply(2, j -> sum(3, i -> K_(i, j) * A_(zc#i)))));
  ys := apply(projPts 3, u -> sum(3, i -> u#i * A_(zc#i)));
  -- complements from the other coordinates: all subspaces of dimension (r - c) - 2 of span(others)
  kdim := r - c - 2; Ks := null;
  Ks = if kdim == 0 then {{}} else apply(subsetsRREF(#others, kdim), M -> apply(kdim, j -> sum(#others, i -> M_(j, i) * A_(others#i))));
  -- for the lifted family (130 complements) only every fourth complement is used, to keep the run short
  if #Ks > 40 then Ks = apply(select(#Ks, i -> i % 4 == 0), i -> Ks#i);
  cnt := 0; killed := 0; good := 0;
  scan(Hs, H -> scan(Ks, K -> (
    Yb := H | K;
    if rank lift(last coefficients(matrix{Yb}, Monomials => apply(gens A, v -> v)), kk) == r - c then
    scan(ys, y -> (
      if not member(y, apply(H, h -> h)) then (
        T := y * product(Yb, f -> f^2);
        if T != 0 then (
          cnt = cnt + 1;
          Tl := lift(T, R);
          pv := matrix{apply(mons, mm -> (ex := first exponents mm;
            coefficient(product(r, i -> R_i^(2 - ex#i)), Tl)))};
          if pv * grV == 0 then (killed = killed + 1; if pv * grF != 0 then good = good + 1))))))));
  print(name | ": candidates=" | toString cnt | ", killing the line sets' graded parts=" | toString killed |
    ", of these nonzero on phi=" | toString good));
pts3 = projPts 3;
lines3 = unique apply(subsets(#pts3, 2), pr -> (a := pts3#(pr#0); b := pts3#(pr#1);
  sort select(#pts3, i -> (M := matrix(kk, {a, b, pts3#i}); rank M == 2))));
print("lines of PG(2,3): " | toString(#lines3) | ", sizes " | toString unique apply(lines3, l -> #l));
scan({1, 2}, s -> (setRandomSeed s; setTest("(a) tensor c=2 m=3, seed " | toString s, 6, 2, famA(), lines3)));
scan({1}, s -> (setRandomSeed s; setTest("(c) lifted tensor c=3 m=3, seed " | toString s, 7, 3, famC(), lines3)));
exit 0

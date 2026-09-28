-- Checks of the transversality criterion for relations among squared spans (route review of the configuration line).
-- Setting: G = F_3[z_1..z_N]/(z^3); for a c-dimensional space U of linear forms, omega_U = product of the squares of
-- a basis of U. Criterion: sum_U a_U omega_U = 0 iff for every (N-c)-dimensional Y, the sum of a_U over the U with
-- U meet Y = 0 vanishes; equivalently the point coverage kappa(P) = sum_{U contains P} a_U has sum A = sum_U a_U
-- over the points of every such Y.
-- Part 1: for (N, c) = (4, 2) and (5, 2), the transversality matrix T (rows Y, columns U, entry [U meet Y = 0])
--   has the same rank as the omegas and annihilates every relation among them, so the two relation spaces agree.
--   For N = 5, T is computed from point incidences mod 3 and checked against direct ranks on a sample.
-- Part 2: covering principle for 2-spreads of F_3^6 (c = 2, span 3c): a Desarguesian spread (from F_9^3) and a
--   regulus-switched spread; each has sum omega = 0. Then: are the relations among each spread's omegas generated
--   by relations among its members inside 4-dimensional subspaces (span 2c)?
-- Part 3: c = 1, eleven points of F_3^4 (first seed that works): one relation among the squares u^2, whose support
--   spans F_3^4, while every subfamily inside a 3-dimensional subspace is independent (span c + 3, 11 members).
-- Part 4: tensor families. For w in PG(m-1, 3), U_w = w (x) F_3^c inside F_3^m (x) F_3^c, spanned by the forms
--   w . z_j (j = 1..c) in the variables z_{i,j}. Prediction: the relations are the vectors orthogonal to all
--   degree-2c forms on the points w; for m = c + 1 exactly one, the all-ones vector; for m = c none (control).
-- Part 5: for the tensor family with c = 2, m = 3 (13 members, each with forms w . z_1, w . z_2 plus random
--   constants and a random prefix combination P with nonzero coefficient on the first form, so that the top is
--   minus omega), the sum of the clause functions (1 - L_2^2) P^2 over the members,
--   as a function of the six form values: its degree (below 4, since the tops cancel) and whether it is zero.
kk = ZZ/3;
subspaces = (N, c) -> (
  L := {};
  scan(subsets(N, c), piv -> (
    fr := flatten apply(c, r -> apply(select(toList(piv#r+1..N-1), j -> not member(j, piv)), j -> (r, j)));
    scan(toList(0..3^(#fr)-1), t -> (
      M := mutableMatrix(kk, c, N);
      scan(c, r -> M_(r, piv#r) = 1_kk);
      scan(#fr, f -> M_(fr#f) = ((t // 3^f) % 3)_kk);
      L = append(L, matrix M)))));
  L);
cubeAlg = N -> (S := kk[z_1..z_N]; S/ideal(apply(gens S, v -> v^3)));
omegaMatrix = (A, N, c, Us) -> (
  om := apply(Us, U -> product(entries U, row -> (sum(N, j -> row#j * A_j))^2));
  lift(last coefficients(matrix{om}, Monomials => basis(2*c, A)), kk));
-- incidence of points in subspaces: point P lies in U iff P * perp(U) = 0
pointIncidence = (N, Pts, Us) -> (
  Pm := matrix apply(Pts, P -> first entries P);
  cols := apply(Us, U -> (Z := Pm * gens ker U;
    apply(#Pts, p -> if Z^{p} == 0 then 1_kk else 0_kk)));
  transpose matrix cols);
part1 = (N, c, direct) -> (
  A := cubeAlg N;
  Us := subspaces(N, c);
  Ys := subspaces(N, N - c);
  Mom := omegaMatrix(A, N, c, Us);
  K := gens ker Mom;
  T := if direct then matrix apply(Ys, Y -> apply(Us, U -> if rank(U || Y) == N then 1_kk else 0_kk))
    else (Pts := subspaces(N, 1);
      IU := pointIncidence(N, Pts, Us); IY := pointIncidence(N, Pts, Ys);
      map(kk^(#Ys), kk^(#Us), (i, j) -> 1_kk) - transpose(IY) * IU);
  sampleOk := if direct then "direct" else (
    setRandomSeed 7;
    ok := all(2000, s -> (i := random(#Ys); j := random(#Us);
      T_(i, j) == (if rank(Us#j || Ys#i) == N then 1_kk else 0_kk)));
    "2000 sampled entries agree with direct ranks: " | toString ok);
  print("Part 1: N=" | toString N | " c=" | toString c | " subspaces=" | toString(#Us) | " rank(omega)=" |
    toString rank Mom | " rank(T)=" | toString rank T | " T kills all relations: " | toString(T * K == 0) |
    "; " | sampleOk));
part1(4, 2, true);
part1(5, 2, false);
-- Part 2. F_9 = F_3[i]/(i^2 + 1); element (a, b) = a + b i; multiplication by i: (a, b) -> (-b, a).
mulI = v -> {-v#1, v#0};
f9 = flatten apply(3, a -> apply(3, b -> {a, b}));
planeOf = w -> (iw := apply(w, mulI); matrix(kk, {flatten w, flatten iw}));
pts9 = join(flatten apply(f9, s -> apply(f9, t -> {{1,0}, s, t})), apply(f9, t -> {{0,0}, {1,0}, t}),
  {{{0,0}, {0,0}, {1,0}}});
des = apply(pts9, planeOf);
-- regulus: the F_9-points (1, s, 0), s in F_3, and (0, 1, 0), inside T0 = {w3 = 0}
isReg = w -> (w#2 == {0,0} and ((w#0 == {1,0} and (w#1)#1 == 0) or (w#0 == {0,0})));
regIdx = select(#pts9, j -> isReg(pts9#j));
vecs = U -> (rows := entries U; set apply(toList(1..8), t -> (a := t % 3; b := t // 3;
  apply(6, j -> (a * rows#0#j + b * rows#1#j)))));
covered = sum apply(regIdx, j -> vecs(des#j));
-- opposite regulus: planes inside T0 (first four coordinates) whose nonzero vectors lie in the regulus cover
cand = apply(subspaces(4, 2), P -> P | map(kk^2, kk^2, 0));
regKeys = apply(regIdx, j -> toString entries reducedRowEchelonForm des#j);
opp = select(cand, P -> isSubset(vecs P, covered) and not member(toString entries reducedRowEchelonForm P, regKeys));
switched = join(apply(select(#des, j -> not member(j, regIdx)), j -> des#j), opp);
isSpread = F -> (#F == 91 and #(sum apply(F, vecs)) == 728);
A6 = cubeAlg 6;
part2 = (name, F) -> (
  Mom := omegaMatrix(A6, 6, 2, F);
  rel := #F - rank Mom;
  allOnes := (Mom * map(kk^(#F), kk^1, (i, j) -> 1_kk)) == 0;
  Big := fold(apply(F, U -> U), (a, b) -> a || b);
  spans := new MutableHashTable;
  scan(#F, i -> scan(toList(i+1..#F-1), j -> spans#(toString entries reducedRowEchelonForm(F#i || F#j)) = F#i || F#j));
  full := 0; loc := map(kk^(#F), kk^0, 0);
  scan(values spans, T -> (
    Z := Big * gens ker T;
    inside := select(#F, u -> Z^{2*u, 2*u+1} == 0);
    if #inside == 10 then full = full + 1;
    Kl := gens ker Mom_inside;
    if numColumns Kl > 0 then
      loc = loc | map(kk^(#F), kk^(numColumns Kl), (r, s) -> (p := position(inside, x -> x == r);
        if p === null then 0_kk else Kl_(p, s)))));
  print("Part 2: " | name | ": spread=" | toString isSpread F | " rank(omega)=" | toString rank Mom |
    " relations=" | toString rel | " all-ones relation: " | toString allOnes | "; 4-spaces spanned by pairs: " |
    toString(#spans) | ", of which partitioned by members: " | toString full |
    "; rank of relations inside 4-spaces: " | toString rank loc));
print("Part 2: regulus planes " | toString(#regIdx) | ", opposite planes found " | toString(#opp));
part2("Desarguesian", des);
part2("regulus-switched", switched);
-- Part 3.
A4 = cubeAlg 4;
threes = subspaces(4, 3);
generic = seed -> (
  setRandomSeed seed;
  P := {}; seen := {};
  while #P < 11 do (v := random(kk^1, kk^4);
    if v != 0 then (k := toString entries reducedRowEchelonForm v;
      if not member(k, seen) then (P = append(P, v); seen = append(seen, k))));
  Mom := omegaMatrix(A4, 4, 1, P);
  K := gens ker Mom;
  Big := fold(P, (a, b) -> a || b);
  sub := all(threes, T -> (Z := Big * gens ker T; inside := select(11, u -> Z^{u} == 0);
    #inside == 0 or rank Mom_inside == #inside));
  supp := if numColumns K == 1 then select(11, i -> K_(i, 0) != 0) else {};
  (rank Mom, numColumns K, #supp, if #supp > 0 then rank Big^supp else 0, sub));
out3 = null; sd = 0;
while (sd = sd + 1; out3 = generic sd; not (out3#0 == 10 and out3#3 == 4 and out3#4) and sd < 50) do null;
print("Part 3: seed=" | toString sd | " rank(u^2)=" | toString out3#0 | " relations=" | toString out3#1 |
  " support size: " | toString out3#2 | " span of support: " | toString out3#3 |
  " every subfamily in a 3-space independent: " | toString out3#4);
-- Part 4.
projPts = m -> apply(subspaces(m, 1), P -> first entries P);
tensorFamily = (m, c) -> apply(projPts m, w ->
  matrix apply(c, j -> flatten apply(m, i -> apply(c, jj -> if jj == j then w#i else 0_kk))));
scan({(2, 2), (2, 3), (3, 3), (3, 4)}, cm -> (
  c := cm#0; m := cm#1;
  F := tensorFamily(m, c);
  A := cubeAlg(m * c);
  Mom := omegaMatrix(A, m * c, c, F);
  K := gens ker Mom;
  allOnes := (Mom * map(kk^(#F), kk^1, (i, j) -> 1_kk)) == 0;
  sup := if numColumns K == 1 then toString all(#F, i -> K_(i, 0) != 0) else "n/a";
  print("Part 4: c=" | toString c | " m=" | toString m | " members=" | toString(#F) | " span=" |
    toString rank fold(F, (a, b) -> a || b) | " rank(omega)=" | toString rank Mom | " relations=" |
    toString numColumns K | " all-ones relation: " | toString allOnes | " full support: " | sup)));
-- Part 5.
R6 = kk[y_1..y_6];
Q6 = R6/ideal(apply(gens R6, v -> v^3 - v));
part5 = s -> (
  setRandomSeed s;
  F := sum(projPts 3, w -> (
    l1 := sum(3, i -> w#i * Q6_i) + random kk; l2 := sum(3, i -> w#i * Q6_(3 + i)) + random kk;
    ab := {0_kk, 0_kk}; while ab#0 == 0_kk do ab = {random kk, random kk};
    pre := ab#0 * l1 + ab#1 * l2;
    (1 - l2^2) * pre^2));
  (if F == 0 then -1 else first degree lift(F, R6), F == 0));
scan({1, 2, 3}, s -> (r := part5 s; print("Part 5: seed=" | toString s | " degree of the clause sum=" |
  toString r#0 | " zero: " | toString r#1)));
exit 0

-- Falsification test of conj:quadratic-span-locality (cube model). Lifted forced family, c = 2: members Z + <w>,
-- Z = <y_1>, w points of F_3^4 in the forms y_2..y_5. Squares of linear forms: eleven seeded random points of F_3^4
-- with exactly one relation among their squares whose support S spans F_3^4 and has no dependent subfamily inside a
-- 3-dimensional subspace (as in transversal_relation_check.m2, Part 3). The family is the support S with the
-- relation's coefficients a_w: the tops -omega_Z w^2 satisfy sum a_w tau_w = 0 with span 1 + 4 = c + 3, and in W's
-- regime such forced families have span of order sqrt(members), beyond any O(D^2).
-- Member w: forms g = y_1 + b0, f = w . (y_2..y_5) + a; prefix P = s g + t f (s != 0); clause (1 - f^2) P^2.
-- Test: is F = sum a_w C_w absorbed by the closed members (degree <= 3 functions killed by prod (1 - C_b)) of the
-- largest clause sets of proper span, the members with w in a common 3-dimensional subspace? Control: whole family.
kk = ZZ/3;
subspaces = (N, c) -> (L := {};
  scan(subsets(N, c), piv -> (
    fr := flatten apply(c, rr -> apply(select(toList(piv#rr+1..N-1), j -> not member(j, piv)), j -> (rr, j)));
    scan(toList(0..3^(#fr)-1), t -> (M := mutableMatrix(kk, c, N);
      scan(c, rr -> M_(rr, piv#rr) = 1_kk); scan(#fr, f -> M_(fr#f) = ((t // 3^f) % 3)_kk);
      L = append(L, matrix M))))); L);
S4 = kk[u_1..u_4]; A4 = S4/ideal(apply(gens S4, v -> v^3));
threes = subspaces(4, 3);
pick = sd -> (setRandomSeed sd; P := {}; seen := {};
  while #P < 11 do (v := random(kk^1, kk^4);
    if v != 0 then (k := toString entries reducedRowEchelonForm v;
      if not member(k, seen) then (P = append(P, v); seen = append(seen, k))));
  M := lift(last coefficients(matrix{apply(P, v -> (sum(4, j -> v_(0, j) * A4_j))^2)}, Monomials => basis(2, A4)), kk);
  K := gens ker M;
  if numColumns K != 1 then return null;
  supp := select(11, i -> K_(i, 0) != 0);
  Big := fold(P, (a, b) -> a || b);
  if rank Big^supp < 4 then return null;
  ok := all(threes, T -> (Z := Big^supp * gens ker T; ins := select(#supp, u -> Z^{u} == 0);
    #ins == 0 or rank M_(apply(ins, i -> supp#i)) == #ins));
  if not ok then return null;
  (apply(supp, i -> first entries P#i), apply(supp, i -> K_(i, 0))));
sd = 0; fam = null;
while (sd = sd + 1; fam = pick sd; fam === null and sd < 50) do null;
pts = fam#0; wts = fam#1;
print("seed " | toString sd | ": support " | toString(#pts) | " points " | toString pts | ", weights " | toString wts);
R = kk[y_1..y_5]; Q = R/ideal(apply(gens R, v -> v^3 - v)); d = 3;
mons = select(flatten apply(toList(0..d), e -> flatten entries basis(e, R)), mm -> all(first exponents mm, a -> a <= 2));
allMons = select(flatten entries basis(0, 10, R), mm -> all(first exponents mm, a -> a <= 2));
randNZ = () -> (x := 0_kk; while x == 0 do x = random kk; x);
testFam = s -> (setRandomSeed s;
  clauses := apply(pts, w -> (b0 := random kk; a := random kk; s0 := randNZ(); t0 := random kk;
    f := sum(4, j -> w#j * Q_(j + 1)) + a; P := s0 * (Q_0 + b0) + t0 * f; (1 - f^2) * P^2));
  F := sum(#clauses, i -> wts#i * clauses#i);
  degF := if F == 0 then -1 else first degree lift(F, R);
  fvec := lift(last coefficients(matrix{{lift(F, R)}}, Monomials => mons), kk);
  part := S -> (off := product(S, b -> 1 - clauses#b);
    gens ker lift(last coefficients(matrix{apply(mons, mm -> lift(sub(mm, Q) * off, R))}, Monomials => allMons), kk));
  Bp := matrix(kk, pts);
  sets := unique select(apply(threes, T -> (Z := Bp * gens ker T; select(#pts, u -> Z^{u} == 0))), l -> #l > 0);
  V := fold(apply(sets, part), (a, b) -> a | b);
  Vall := part toList(0..#pts-1);
  print("seed " | toString s | ": deg F=" | toString degF | ", proper-span sets " | toString(#sets) | " (sizes " |
    toString sort unique apply(sets, l -> #l) | "), rank of their closed parts " | toString rank V |
    ", F absorbed by them: " | toString(rank(V | fvec) == rank V) | "; control, whole family: " |
    toString(rank(Vall | fvec) == rank Vall)));
scan({1, 2}, testFam);
exit 0

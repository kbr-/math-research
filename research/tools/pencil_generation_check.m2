-- Test of pencil generation: over F_3, in G = F_3[z_1..z_N]/(z^3), for each c-dimensional subspace U of linear
-- forms let omega_U = product of the squares of a basis of U (independent of the basis). Pencil relations: for
-- U0 of dimension c-1 inside V of dimension c+1, the four c-spaces between them have omegas summing to 0.
-- Question: do the pencil relations span all linear relations among the omega_U?
-- Prints: N, c, number of subspaces, rank of the omegas, dimension of the relation space, rank of pencil relations.
kk = ZZ/3;
rrefKey = M -> toString entries reducedRowEchelonForm M;
subspaces = (N, c) -> (
  -- all c-dim subspaces of kk^N, enumerated directly as reduced row echelon c x N matrices
  L := {};
  scan(subsets(N, c), piv -> (
    fr := flatten apply(c, r -> apply(select(toList(piv#r+1..N-1), j -> not member(j, piv)), j -> (r, j)));
    scan(toList(0..3^(#fr)-1), t -> (
      M := mutableMatrix(kk, c, N);
      scan(c, r -> M_(r, piv#r) = 1_kk);
      scan(#fr, f -> M_(fr#f) = ((t // 3^f) % 3)_kk);
      L = append(L, matrix M)))));
  L);
test = (N, c) -> (
  S := kk[z_1..z_N];
  A := S/ideal(apply(gens S, v -> v^3));
  Us := subspaces(N, c);
  idx := new HashTable from apply(#Us, i -> (toString entries Us#i, i));
  omega := U -> product(entries U, row -> (sum(N, j -> row#j * A_j))^2);
  om := apply(Us, omega);
  d := 2*c;
  B := basis(d, A);
  Mom := lift(last coefficients(matrix{om}, Monomials => B), kk);
  r := rank Mom;
  -- pencil relations
  lows := if c == 1 then {map(kk^0, kk^N, 0)} else subspaces(N, c-1);
  highs := subspaces(N, c+1);
  rels := {};
  scan(lows, U0 -> scan(highs, V -> (
    if rank(U0 || V) == c+1 then (
      -- c-spaces between U0 and V: U0 + <v> for v in V not in U0, deduplicated
      between := new MutableHashTable;
      scan(toList(apply((0..3^(c+1)-1), i -> apply(c+1, j -> (i // 3^j) % 3))), co -> (
        v := matrix(kk, {co}) * V;
        W := U0 || v;
        if rank W == c then between#(toString entries reducedRowEchelonForm W) = 1));
      ks := keys between;
      if #ks == 4 then rels = append(rels, apply(ks, k -> idx#k))))));
  P := map(kk^(#Us), kk^(#rels), flatten apply(#rels, j -> apply(rels#j, i -> (i, j) => 1_kk)));
  rp := rank P;
  -- check each pencil relation holds
  ok := all(rels, rl -> sum(rl, i -> om#i) == 0);
  print("N=" | toString N | " c=" | toString c | " subspaces=" | toString(#Us) | " rank(omega)=" | toString r |
    " relations=" | toString(#Us - r) | " pencil rank=" | toString rp | " pencils hold=" | toString ok));
-- Local generation in (c+2)-dimensional subspaces: start from the pencil span and add, for each
-- (c+2)-dimensional V, the relations supported on the c-spaces inside V; keep only additions that raise the rank.
pencilMatrix = (N, c, Us, idx) -> (
  lows := if c == 1 then {map(kk^0, kk^N, 0)} else subspaces(N, c-1);
  highs := subspaces(N, c+1);
  rels := {};
  scan(lows, U0 -> scan(highs, V -> (
    if rank(U0 || V) == c+1 then (
      between := new MutableHashTable;
      scan(toList(apply((0..3^(c+1)-1), i -> apply(c+1, j -> (i // 3^j) % 3))), co -> (
        v := matrix(kk, {co}) * V;
        W := U0 || v;
        if rank W == c then between#(toString entries reducedRowEchelonForm W) = 1));
      ks := keys between;
      if #ks == 4 then rels = append(rels, apply(ks, k -> idx#k))))));
  map(kk^(#Us), kk^(#rels), flatten apply(#rels, j -> apply(rels#j, i -> (i, j) => 1_kk))));
localTest = (N, c) -> (
  S := kk[z_1..z_N];
  A := S/ideal(apply(gens S, v -> v^3));
  Us := subspaces(N, c);
  idx := new HashTable from apply(#Us, i -> (toString entries Us#i, i));
  omega := U -> product(entries U, row -> (sum(N, j -> row#j * A_j))^2);
  B := basis(2*c, A);
  Mom := lift(last coefficients(matrix{apply(Us, omega)}, Monomials => B), kk);
  full := #Us - rank Mom;
  cur := pencilMatrix(N, c, Us, idx);
  r := rank cur;
  r0 := r;
  I := id_(kk^(#Us));
  scan(subspaces(N, c+2), V -> (
    inside := select(toList(0..#Us-1), i -> rank(V || Us#i) == c+2);
    EK := I_inside * gens ker Mom_inside;
    M := cur | EK;
    rM := rank M;
    if rM > r then (cur = M; r = rM)));
  print("N=" | toString N | " c=" | toString c | " relations=" | toString full | " pencil rank=" | toString r0 |
    " with relations inside " | toString(c+2) | "-spaces=" | toString r));
test(3, 1);
test(4, 1);
test(4, 2);
test(5, 2);
localTest(5, 2);
exit 0

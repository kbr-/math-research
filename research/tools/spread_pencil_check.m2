-- (definitions shared with pencil_generation_check.m2)
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
-- Is the regular-spread relation (sum of the omegas of the ten F_9-lines of F_3^4) outside the pencil span?
N = 4; c = 2;
Us = subspaces(N, c);
idx = new HashTable from apply(#Us, i -> (toString entries Us#i, i));
P = pencilMatrix(N, c, Us, idx);
spread = append(apply(flatten apply(3, a -> apply(3, b -> (a, b))), t -> matrix(kk, {{1,0,t#0,t#1},{0,1,-t#1,t#0}})),
  matrix(kk, {{0,0,1,0},{0,0,0,1}}));
sidx = apply(spread, M -> idx#(toString entries reducedRowEchelonForm M));
v = map(kk^(#Us), kk^1, apply(sidx, i -> (i, 0) => 1_kk));
print("pencil rank: " | toString rank P | ", with the spread relation: " | toString rank(P | v));
exit 0

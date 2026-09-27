-- Test of conj:relation-local-generation beyond coordinate forms: prefix-sum chains, members (a_i, b_i) = (x_i, y_i)
-- with the non-identification relations r_i = a_{i+1} - a_i - b_i (so a_i are prefix sums of the b's on the board).
-- R_S = span{r_j : j, j+1 in S}. Tops a_i b_i^2.
-- Members M_i = F3[x_i,y_i]/(cubes, x_i y_i^2) (tops of degree 3). For relation space R (linear forms in
-- the members' variables) Tor_1^{T(R)}(F3, tensor M_i) = Tor_1^A(A/J, A/(R)) (lem:relation-space-tor).
-- For each family we print, by degree 0..14: dim Tor_1 of the whole family, and dim of the span of the
-- images of Tor_1^A(A/J, A/(R_S)) -> Tor_1^A(A/J, A/(R)) over the given subfamilies S (edge bags, with
-- R_S the relations inside S), induced by the quotient maps A/(R_S) -> A/(R).
torImages = (m, rels, bags) -> (
  vs := flatten apply(toList(1..m), i -> {("x"|toString i), ("y"|toString i)});
  R := ZZ/3[vs / (s -> getSymbol s)];
  X := i -> R_(2*i-2); Y := i -> R_(2*i-1);
  A := R/ideal(apply(gens R, v -> v^3));
  x := i -> sub(X i, A); y := i -> sub(Y i, A);
  J := matrix{apply(toList(1..m), i -> x(i)*(y(i))^2)};
  C := res(coker J, LengthLimit => 2);
  relf := r -> sub(r(x, y), A);
  full := coker matrix{apply(rels, relf)};
  T1 := HH_1(C ** full);
  imgs := apply(bags, b -> (
    src := coker matrix{apply(b, relf)};
    f := map(full, src, id_(A^1));
    image HH_1(C ** f)));
  total := sum imgs;
  {apply(toList(0..14), d -> hilbertFunction(d, T1)), apply(toList(0..14), d -> hilbertFunction(d, total))});
report = (name, m, rels, bags) -> (
  r := torImages(m, rels, bags);
  print(name | " Tor_1:        " | toString r#0);
  print(name | " bag images:   " | toString r#1));
r = j -> ((x, y) -> x(j+1) - x(j) - y(j));
scan({3, 4, 5}, m -> (
  rels := apply(toList(1..m-1), j -> r j);
  pairs := apply(toList(1..m-1), j -> {r j});
  triples := apply(toList(1..m-2), j -> {r j, r(j+1)});
  report("prefix chain m=" | toString m | " adjacent pairs", m, rels, pairs);
  report("prefix chain m=" | toString m | " triples", m, rels, triples)));
exit 0

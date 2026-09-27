-- Correction test for ex:relation-bag-images: the star with bags R_S = all relations among the forms of S
-- (conj:relation-local-generation's definition), for every pair S of members, including two leaves.
-- Test of relation-space local generation (conj:relation-local-generation) on small relation hypergraphs.
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
d = (i, j) -> ((x, y) -> x(i) - x(j));
s = (i, j) -> ((x, y) -> y(i) - x(j));
-- star: hub 1 with y1 - x2, y1 - x3, y1 - x4; R_S for pairs: {1,j} -> y1 - xj; {i,j} leaves -> xi - xj
report("star3 R_S pairs", 4, {s(1,2), s(1,3), s(1,4)}, {{s(1,2)}, {s(1,3)}, {s(1,4)}, {d(2,3)}, {d(2,4)}, {d(3,4)}});
report("star3 leaf pairs only", 4, {s(1,2), s(1,3), s(1,4)}, {{d(2,3)}, {d(2,4)}, {d(3,4)}});
exit 0

-- Degree-zero circuits (prop:degree-zero-circuits) in relation space: members (x_b, y_b) with tops x_b y_b^2 (shared square y = A),
-- relations y_1 - y_b (shared form A) and x_1 + ... + x_r (B_r = -(B_1 + ... + B_{r-1})). Images from all
-- member sets of size r-1, with R_S = identifications y_b - y_b' inside S (the x-relation needs all r members).
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
idf = (b, c) -> ((x, y) -> y(b) - y(c));
scan({4, 5}, r -> (
  sumy := (x, y) -> sum(toList(1..r), b -> x(b));
  rels := append(apply(toList(2..r), b -> idf(1, b)), sumy);
  bags := apply(subsets(toList(1..r), r-1), S -> apply(drop(S, 1), b -> idf(S#0, b)));
  report("circuit r=" | toString r | " sets of size r-1", r, rels, bags);
  scan({2, 3}, c -> (
    bc := apply(subsets(toList(1..r), c), S -> apply(drop(S, 1), b -> idf(S#0, b)));
    report("circuit r=" | toString r | " sets of size " | toString c, r, rels, bc)))));
exit 0

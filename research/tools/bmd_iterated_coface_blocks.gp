\\ Iterated coface test for statement 2's slice d=2 (cycle kbl, 9 October 2026).
\\ Statement tested: along the iterated coface degeneration of the degree-two root-curve space (each step
\\ sends one root a_m -> 0), the blocks merge as k[T]_{<=A} + x k[T]_{<=B}, x = sqrt(1+eps T), with
\\ (A,B) = (D_s, E_s) = (1 + s(s+1)/2, s) for the trivial character and (E_s, 0) for each single character.
\\ Such a merge keeps consecutive orders (saturated limit k[T]_{<=A+B+1}) when the square top block
\\ [binom(i, j)] with rows i = A+B+2..2A and odd columns j = 2B+3..2A-1 is invertible mod p.
\\ Reported: the steps s whose block is singular mod p.  Cross-check: the record certifies Delta_{n,2} != 0 mod 3
\\ for n <= 21 (check:cube-ternary-confluent-nonvanishing).

block(A, B, p) = {
  my(m = A - B - 1);
  if(m <= 0, return(1));
  matdet(matrix(m, m, a, b, Mod(binomial(A + B + 1 + a, 2 * (B + b) + 1), p)));
}

{
foreach([3, 5, 7, 1000003], p,
  my(bad = List());
  for(s = 0, 20,
    my(D = 1 + s * (s + 1) / 2, E = s);
    if(block(D, E, p) == 0, listput(bad, ["trivial", s, D, E]));
    if(block(E, 0, p) == 0, listput(bad, ["single", s, E, 0])));
  print("p=", p, " singular blocks for s<=20: ", Vec(bad)));
}
quit;

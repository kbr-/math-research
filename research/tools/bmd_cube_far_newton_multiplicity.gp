\\ Newton-polygon exclusion of repeated factors for the far polynomials W_k (cycle bmd-20260930-zzu, review lead).
\\ If W = G^r H with G nonconstant (r = 2: a repeated root; r = 3: a triple root), then at every prime p the Newton
\\ polygon of W is r NP(G) + NP(H) (Dumas).  A segment of W of slope s = a/b (lowest terms) and length L can receive
\\ from G only lengths l with b | l and r l <= L.  So deg G lies in S_p = { sum_s l_s : b_s | l_s, r l_s <= L_s }.
\\ If the intersection of the S_p over p <= PMAX contains no positive integer, W has no factor G^r: certified by
\\ Newton polygons alone.  Input: the primitive far polynomials saved in cycle bmd-20260930-zzn.
PMAX = 400;
segs(W, p) = {
  my(v = newtonpoly(W, p), out = List(), i = 1);          \\ v: slopes of the roots, sorted
  while (i <= #v, my(j = i); while (j < #v && v[j + 1] == v[i], j++); listput(out, [v[i], j - i + 1]); i = j + 1);
  Vec(out);
}
degset(W, p, r) = {
  my(S = [0]);
  foreach (segs(W, p), sg, my(b = denominator(sg[1]), L = sg[2], T = List());
    foreach (S, x, forstep (l = 0, L \ r, b, listput(T, x + l)));
    S = Set(Vec(T)));
  S;
}
{
  foreach (["1_1", "1_2", "2_1"], nm,
    my(W = read(Str("research/results/bmd-20260930-zzn/W_", nm, ".gp")), d, P);
    W = W / content(W); d = poldegree(W);
    foreach ([2, 3], r,
      my(I = Set(vector(d \ r + 1, k, k - 1)), used = List());
      forprime (p = 2, PMAX, my(S = degset(W, p, r), J = setintersect(I, S));
        if (#J < #I, listput(used, [p, #J - 1])); I = J);
      print("(e,l) = (", nm, "), deg ", d, ", exponent r = ", r, ": degrees of G not excluded by primes <= ", PMAX, ": ",
        setminus(I, [0]), ";  primes that cut (p, remaining positive degrees): ", Vec(used))));
}

\\ Schur expansion of Phi_N modulo 3 (5 October 2026; cycle bmd-20261005-h).  thm:cube-odd-schur-hull: the unanchored
\\ original determinant is V_N^N Phi_N with Phi_N symmetric, translation invariant, homogeneous of degree 3 binom(N,4).
\\ Write Phi_N = sum_lambda c_lambda s_lambda over partitions of 3 binom(N,4) with at most N parts.  We evaluate
\\ Phi = Delta / V^N at random points of F_(3^K) and solve for c_lambda (which lie in F_3).  Output: the partitions with
\\ nonzero c_lambda mod 3 and their values.  Question: is there a shape, defined for every N, whose coefficient is a unit?
\\ Env NS, K, EXTRA (extra evaluation points as a consistency check), SEED.
default(parisizemax, 4000000000);
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
mark(lab, one) = {
  my(N = #lab, D = N * (N - 1) / 2 + 2, bh = vector(D, j, lift(binomial(1/2, j - 1) * Mod(1, 3))), M = matrix(D, D), row = 2);
  M[1, 1] = one; M[2, 2] = one;
  for (i = 1, N, for (j = i + 1, N, row++;
    for (kk = 1, D, M[row, kk] = one * sum(u = 0, kk - 1, bh[u + 1] * bh[kk - u] * lab[i]^u * lab[j]^(kk - 1 - u)))));
  matdet(M);
}
schur(lam, x) = {
  my(N = #x, l = concat(lam, vector(N - #lam)));
  matdet(matrix(N, N, i, j, x[i]^(l[j] + N - j))) / matdet(matrix(N, N, i, j, x[i]^(N - j)));
}
{
my(K = eval(getenv("K")), g = ffgen(ffinit(3, K, 'a), 'a), one = g^0, EX = eval(getenv("EXTRA")));
setrand(eval(getenv("SEED")));
foreach(eval(getenv("NS")), N,
  my(deg = 3 * binomial(N, 4), parts = List(), t0 = getwalltime());
  forpart(p = deg, listput(parts, Vecrev(p)), , N);
  parts = Vec(parts);
  my(P = #parts, A = matrix(P + EX, P), b = vector(P + EX));
  for (r = 1, P + EX,
    my(x = vector(N, i, random(g)), V = prod(i = 1, N, prod(j = i + 1, N, x[j] - x[i])));
    b[r] = mark(x, one) / V^N;
    for (c = 1, P, A[r, c] = schur(parts[c], x)));
  my(sol = matsolve(A[1..P, ], b[1..P]~));
  my(chk = vecmax(apply(r -> if(A[r, ] * sol == b[r], 0, 1), vector(EX, i, P + i))));
  my(nz = List()); for (c = 1, P, if (sol[c] != 0, listput(nz, [parts[c], sol[c]])));
  emit(Str("N = ", N, ": degree ", deg, ", ", P, " partitions with at most ", N, " parts; extra-point check ", if(chk == 0, "passed", "FAILED"),
    "; nonzero Schur coefficients mod 3 (", #nz, "): ", Vec(nz), " (", getwalltime() - t0, " ms)")));
}
quit;

\\ Flat limit of a two-cluster class of the spine (30 September 2026; cycle bmd-20260930-zu).
\\ Class {1,2} of lem:cube-multicluster-spine-classes: sqrt((z-p1)(z-p2)) times the span of the n1*n2 products
\\ (1 - b_j v1)^(1/2) (1 - c_k v2)^(1/2), v_i = eps u_i, u_i = 1/(z - p_i).  With p1 = 0, p2 = 1 and fixed rational
\\ b, c, the script expands each product to order eps^K as a combination of u1^a u2^c, maps every such rational function
\\ to its principal parts at p1, p2 (orders 1..K) and its value at infinity, and computes the flat limit of the span
\\ over Q[[eps]] by valuation reduction: while the leading vectors are dependent, a dependency is used to raise the
\\ valuation of one row.  Output: the valuations (eps-orders) of the reduced rows, and the pole orders at p1 and p2
\\ of the limit functions (a basis in echelon form by pole order), for (n1,n2) = (2,2),(2,3),(3,3),(2,4),(3,4).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
\\ coordinates of u1^a u2^c: principal parts at 0 and 1 (orders 1..K) and value at infinity, as a vector of length 2K+1
coords(a, c, K) = {
  my(F = 1 / ('z^a * ('z - 1)^c), v = vector(2 * K + 1));
  my(s0 = F + O('z^1)); for (k = 1, K, v[k] = polcoef(s0, -k, 'z));
  my(t = subst(F, 'z, 1 + 'y) + O('y^1)); for (k = 1, K, v[K + k] = polcoef(t, -k, 'y));
  v[2 * K + 1] = if (a + c == 0, 1, 0);
  v;
}
flat(n1, n2, K) = {
  my(sd = if (getenv("SEED"), eval(getenv("SEED")), 0), b = vector(n1, j, (2 * j + 1 + 3 * sd) / (7 + sd) * (-1)^j), c = vector(n2, j, (3 * j - 1 + 5 * sd) / (5 + 2 * sd) * (-1)^(j + 1)));
  my(C = matrix(K + 1, K + 1, a, cc, if (a + cc - 2 <= K, coords(a - 1, cc - 1, K), 0)));
  my(D = 2 * K + 1, rows = List());
  for (j = 1, n1, for (k = 1, n2,
    \\ row as a vector of polynomials in eps
    my(r = vector(D));
    for (a = 0, K, for (cc = 0, K - a,
      my(coef = binomial(1/2, a) * (-b[j])^a * binomial(1/2, cc) * (-c[k])^cc * 'e^(a + cc));
      r += coef * coords(a, cc, K)));
    listput(rows, r)));
  my(R = Mat(Vec(rows)~), n = n1 * n2, vals = vector(n), iter = 0);
  \\ valuation reduction
  while (1, iter++; if (iter > 500, error("no convergence"));
    for (i = 1, n, vals[i] = vecmin(vector(D, t, if (R[i, t] == 0, oo, valuation(R[i, t], 'e)))));
    my(L = matrix(n, D, i, t, polcoef(R[i, t], vals[i], 'e)));
    my(ker = matker(L~));
    if (#ker == 0, break);
    \\ pick the row of largest valuation in the dependency's support
    my(w = ker[, 1], i0 = 0, best = -oo);
    for (i = 1, n, if (w[i] != 0 && vals[i] > best, best = vals[i]; i0 = i));
    my(newrow = sum(i = 1, n, w[i] * 'e^(best - vals[i]) * R[i, ]));
    R[i0, ] = newrow;
    for (t = 1, D, R[i0, t] = truncate(R[i0, t] + O('e^(K + 1)))));
  my(L = matrix(n, D, i, t, polcoef(R[i, t], vals[i], 'e)));
  \\ pole orders at p1 = 0 (coordinates 1..K) and p2 = 1 (K+1..2K) of each limit row
  my(po = vector(n, i, [vecmax(concat([0], select(t -> L[i, t] != 0, vector(K, t, t)))), vecmax(concat([0], select(t -> L[i, K + t] != 0, vector(K, t, t))))]));
  \\ dimension counts: limit functions with pole order <= x at p1 and <= y at p2
  my(tab = matrix(K + 1, K + 1));
  for (x = 0, K, for (y = 0, K, my(cols = concat(vector(K - x, t, x + t), vector(K - y, t, K + y + t)));
    tab[x + 1, y + 1] = n - matrank(matrix(n, #cols, i, t, L[i, cols[t]])) ));
  [vecsort(vals), rank(L), tab];
}
rank(M) = matrank(M);
main() = {
  foreach ([[2, 2], [2, 3], [3, 3], [2, 4], [3, 4]], nn,
    my(K = 3 * (nn[1] + nn[2]), r = flat(nn[1], nn[2], K), tab = r[3]);
    emit(Str("(n1,n2)=(", nn[1], ",", nn[2], "): eps-orders of the reduced rows ", r[1], "; rank of the limit ", r[2]));
    my(x0 = nn[1] - 1, y0 = nn[2] - 1);
    emit(Str("  dims of limit with pole order <= (x,y) at (p1,p2), x = 0..", x0 + 3, ", y = 0..", y0 + 3, ":"));
    for (x = 0, x0 + 3, emit(Str("   x=", x, ": ", vector(y0 + 4, y, tab[x + 1, y])))));
}
main();
quit

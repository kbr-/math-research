\\ Generic-coefficient bound for the neck corner polygons (2 October 2026; cycle bmd-20261002-i).
\\ In the setting of bmd_cube_neck_corner_polygon.gp, the neck rows are A(x_i) B(y_j) with
\\ A(x) = sum_a alpha_a (x/z)^a, B(y) = sum_b beta_b (y/(z-1))^b.  By Cauchy-Binet in the expansion
\\ sum_(a,b) alpha_a beta_b x^a y^b z^-a (z-1)^-b, each Pluecker coordinate is a sum over mn-sets T of exponent pairs
\\ of (grid determinant on T) * prod_T alpha_a beta_b lambda^a lambda'^b * (partial-fraction determinant on T).
\\ Replacing alpha_a beta_b by independent generic gamma_(a,b) removes all cancellation between sets T, so the
\\ support function h_gen(w) of the generic version is the minimal weight of an admissible T, a lower bound for the
\\ actual h(w).  Question: does h_gen equal the conjectured antidiagonal support function?  If so, the antidiagonal
\\ polygon conjecture is equivalent to the nonvanishing of the actual minimal-level coefficients.
\\ MODE=sep keeps the product structure with random one-variable coefficients (gamma_a, gamma'_b).
\\ Rows (default): sum over a w1 + b w2 <= T of gamma_(a,b) (rho t^w1 s_i)^a (rho' t^w2 s'_j)^b z^-a (z-1)^-b, gamma random.
default(threadsizemax, 300000000); default(parisizemax, 1000000000);
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
t; z;
T = if (getenv("TT") != 0 && getenv("TT") != "", eval(getenv("TT")), 64); DEN = T;
vecz(f) = my(p = simplify(f*z^DEN*(z-1)^DEN)); if(type(p) == "t_RFRAC" && poldegree(denominator(p), z) > 0, error("denominator")); Vecrev(p, 2*DEN + 2);
costsum(E) = {
  my(k = #E, rows = E, cost = vector(k), M, K, cc, piv, nr);
  for(iter = 1, 2000,
    M = matrix(k, 2*DEN+2, i, j, vecz(polcoef(rows[i], 0, t))[j]);
    K = matker(M~);
    if(#K == 0, return(vecsum(cost)));
    cc = K[,1];
    piv = 0; for(i = 1, k, if(cc[i] != 0 && (piv == 0 || cost[i] > cost[piv]), piv = i));
    nr = sum(i = 1, k, cc[i]*rows[i]);
    if(polcoef(nr, 0, t) != 0, error("relation not zero"));
    rows[piv] = nr/t; cost[piv]++;
    if(cost[piv] > T - 8, error("truncation too low")));
  error("no convergence");
}

GAM = matrix(129, 129, a, b, (a * 7919 + b * 104729 + a * b * 31) % 97 + 1);
MODE = getenv("MODE");
rowgen(x, y, w1, w2) = {
  my(s = 0);
  if (MODE == "sep",
    \\ separable: A(x) B(y) with random one-variable coefficients gamma_a = GAM[a+1,1], gamma'_b = GAM[1,b+1]
    my(A = sum(a = 0, T \ max(w1, 1), GAM[a + 1, 1] * x^a * z^(-a)), B = sum(b = 0, T \ max(w2, 1), GAM[1, b + 1] * y^b * (z - 1)^(-b)));
    return(A * B + O(t^(T + 1))));
  for (a = 0, T, for (b = 0, T, if (a * w1 + b * w2 <= T,
    s += GAM[a + 1, b + 1] * x^a * y^b * z^(-a) * (z - 1)^(-b))));
  s + O(t^(T + 1));
}
hgen(task) = {
  my(m = task[1], n = task[2], w1 = task[3], w2 = task[4]);
  my(S = [0, 1, 3/7, -5/3, 11/4], SP = [0, 1, -2/5, 7/3, 5/8, -7/2], E = List(), rho = 7/5, rhop = -9/4);
  for (i = 1, m, for (j = 1, n, listput(E, rowgen(rho * t^w1 * S[i], rhop * t^w2 * SP[j], w1, w2))));
  costsum(Vec(E)) - w1 * n * binomial(m, 2) - w2 * m * binomial(n, 2);
}
export(t, z, T, DEN, GAM, MODE, vecz, costsum, rowgen, hgen);
\\ conjectured support function
conjh(m, n, w) = {
  my(N = List(), cnt = 0); for (s = 1, m + n - 2, cnt += #select(v -> v, vector(m * n, q, 0)); );
  my(starts = Set(vector(m + n - 2, s, sum(k = 0, m - 1, sum(l = 0, n - 1, k + l < s)))));
  my(c = select(x -> !setsearch(starts, x), vector(m * n - 1, i, i)), M = #c);
  vecmin(vector(M + 1, r, my(rr = r - 1); w[1] * sum(i = 1, rr, c[i]) + w[2] * sum(i = rr + 1, M, m * n - c[i])));
}
{
  my(W = [[1,4],[1,3],[1,2],[2,3],[1,1],[3,2],[2,1],[3,1],[4,1]]);
  my(C = [[2,3],[3,3],[3,4]]);
  my(tasks = List()); foreach (C, mn, foreach (W, w, listput(tasks, [mn[1], mn[2], w[1], w[2]])));
  my(res = parapply(hgen, Vec(tasks)), idx = 0);
  foreach (C, mn, my(H = vector(#W), HC = vector(#W, i, conjh(mn[1], mn[2], W[i])));
    for (i = 1, #W, idx++; H[i] = res[idx]);
    emit(Str("(m,n)=", mn, " weights ", W));
    emit(Str("  h_gen      = ", H));
    emit(Str("  conjecture = ", HC, "  equal: ", H == HC)));
}

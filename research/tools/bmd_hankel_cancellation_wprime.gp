\\ Condition (W') at Hankel-cancelling roots (cycle bmd-20261009-v, 9 October 2026); combines
\\ bmd_equilateral_windows.gp and bmd_tie_moduli_windows.gp.
\\ Tested statement ((W') of cor:cube-cherry-step): along the arc with weights (wx, we), every cross coordinate of
\\ least value sum over its least term X wx + E we + v, (X, E, v) = (Sigma Lambda + n, n, val [u^n] P_Lambda), is a
\\ 2M-subset of one interval of 2M + 1 consecutive integers (all minimizers in the same interval); also whether the
\\ minimizer is unique. Candidates: windows and every coordinate with a term not strictly dominated by a window term
\\ (a strictly dominated coordinate has strictly larger value at every positive weight). Columns [-M, 2M].
\\ Trees: (a) M = 3, roots (1, w, w^2) and (3, 2+w, 2+w^2), w^2 + w + 1 = 0, constant arc (values 0 or oo), exact
\\ over Q(w); (b) M = 4, cherry above a tie over a caterpillar, roots (c0, 1, q, q + q^2), c0 = (1 +- 2 sqrt(-2))/3
\\ in Z_q (q = 1000003, through an integer congruent mod q^14); control (b') c0 = 2. Weights (a/10, b/10), 1 <= a, b <= 30.
OUT = "research/results/bmd-20261009-v/hankel-cancellation-wprime.txt";
Uv = 'u; Wv = varlower("ww"); W = Mod(Wv, Wv^2 + Wv + 1);
q = 1000003;
c(n) = if(n < 0, 0, binomial(-3/2, n));
NU = 20;
val(x, mode) = if(x == 0, oo, if(mode == 0, 0, valuation(x, q)));
coordterms(Y, L, mode) = {
  my(M = #Y, p = #select(t -> t < 0, L));
  my(X = matrix(2 * M, 2 * M, r, i, my(t = L[i]);
    if(r <= M, if(t >= 0, c(t) * Y[r]^t, 0),
      my(s = r - M); sum(m = max(1, -t), NU, c(m) * c(t + m) * Y[s]^(t + m) * 'u^m))));
  my(D = matdet(X), sL = vecsum(L), res = List());
  for (n = 0, NU, my(v = val(polcoef(D, n, 'u), mode)); if(v < oo, listput(res, [sL + n, n, v])));
  [L, L == [-p .. 2 * M - 1 - p], Vec(res)];
};
export(q, NU, c, val, coordterms);
run(name, Y, mode) = {
  my(M = #Y, cols = [-M .. 2 * M], subs = List());
  forsubset([#cols, 2 * M], S, my(L = vector(2 * M, i, cols[S[i]])); if(#select(t -> t < 0, L) <= M, listput(subs, L)));
  my(R = parapply(L -> coordterms(Y, L, mode), Vec(subs)));
  my(wt = List()); foreach(R, r, if(r[2], foreach(r[3], t, listput(wt, t))));
  my(cand = select(r -> r[2] || #select(a -> !#select(b -> b[1] <= a[1] && b[2] <= a[2] && b[3] <= a[3] && (b[1] < a[1] || b[2] < a[2] || b[3] < a[3]), Vec(wt)), r[3]), R));
  my(bad = 0, nonuniq = 0, nonwin = 0, ex = List(), lead = Map());
  foreach(concat(vector(30, a, vector(30, b, [a / 10, b / 10]))), w,
    my(vals = apply(r -> vecmin(apply(t -> t[1] * w[1] + t[2] * w[2] + t[3], r[3])), cand), m = vecmin(vals));
    my(mins = select(i -> vals[i] == m, [1 .. #cand]), Ls = apply(i -> cand[i][1], mins));
    my(lo = vecmax(apply(L -> vecmax(L), Ls)) - 2 * M, ok = 1);
    foreach(Ls, L, if(vecmin(L) < lo, ok = 0));
    if(#Ls > 1, nonuniq++);
    if(!cand[mins[1]][2] || #Ls > 1, nonwin += #select(i -> !cand[i][2], mins) > 0);
    foreach(Ls, L, if(!mapisdefined(lead, L), mapput(lead, L, w)));
    if(!ok, bad++; if(#ex < 6, listput(ex, [w, Ls]))));
  write(OUT, name, ": M=", M, ", ", #cand, " candidate coordinates of ", #R, "; weights 900");
  write(OUT, "  (W') violated at ", bad, " weights; minimizer not unique at ", nonuniq, "; a non-window among the minimizers at ", nonwin);
  foreach(ex, x, write(OUT, "   violation ", x));
  write(OUT, "  coordinates that are minimizers somewhere (first weight): ");
  foreach(Mat(lead)[, 1], L, write(OUT, "   ", L, " at ", mapget(lead, L), if(L == [-#select(t -> t < 0, L) .. 2 * M - 1 - #select(t -> t < 0, L)], " (window)", "")));
};
{
  run("(a) equilateral (1, w, w^2)", [1, W, W^2], 0);
  run("(a) equilateral (3, 2+w, 2+w^2)", [3, 2 + W, 2 + W^2], 0);
  my(r = sqrt(-2 + O(q^14)));
  run("(b) tie modulus (1 + 2 sqrt(-2))/3", [truncate((1 + 2 * r) / 3), 1, q, q + q^2], 1);
  run("(b) tie modulus (1 - 2 sqrt(-2))/3", [truncate((1 - 2 * r) / 3), 1, q, q + q^2], 1);
  run("(b') control: tie modulus 2", [2, 1, q, q + q^2], 1);
}

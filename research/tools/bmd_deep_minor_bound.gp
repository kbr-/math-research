\\ Tested statement (thm:cube-two-alternant-penalty-bound, minor level): for r deep roots
\\ beta_s with valuations nu_1 <= ... <= nu_r, rows V(beta) = sum c_n beta^n w^n and
\\ Q(beta) = (U_eps - 1) V(beta), U_eps = (1 + eps/w)^(-3/2), every eps-coefficient of the
\\ 2r x 2r minor on a column set T with q negative columns has valuation at least
\\ 2 val Vand(beta) + sum_a 2 (r + 1 - q - a)_+ nu_a.
\\ Valuations are read q-adically at eta = PR (conclusive for refutation only).
\\ Usage: gp -q bmd_deep_minor_bound.gp  (writes to the file named in OUT)
OUT = "research/results/bmd-20261008-zs/deep-minor-bound.txt";
PR = 1000003;
c(n) = if(n < 0, 0, binomial(-3/2, n));
\\ entry of V row at column l, Q row at column l (truncated at eps^MM)
MM = 12;
ventry(b, l) = if(l < 0, 0, c(l) * b^l);
qentry(b, l) = sum(m = max(1, -l), MM, c(m) * c(l + m) * eps^m * b^(l + m));
emit(s) = write(OUT, s);
run(nu, bs, lo, hi) = {
  my(r = #nu, beta = vector(r, s, bs[s] * PR^nu[s]), cols = vector(hi - lo + 1, i, lo - 1 + i));
  my(vv = valuation(prod(i = 1, r, prod(j = i + 1, r, beta[j] - beta[i])), PR));
  my(best = vector(r + 1, i, 10^9), bad = 0, cnt = vector(r + 1));
  forsubset([#cols, 2 * r], S,
    my(T = vector(2 * r, i, cols[S[i]]), q = #select(x -> x < 0, T));
    my(A = matrix(2 * r, 2 * r, i, j, if(i <= r, ventry(beta[i], T[j]), qentry(beta[i - r], T[j]))));
    my(D = matdet(A), thr = 2 * vv + sum(a = 1, r, 2 * max(0, r + 1 - q - a) * nu[a]), least = 10^9);
    if(D == 0, next);
    for(k = 0, MM, my(co = polcoef(D, k, eps)); if(co != 0, least = min(least, valuation(co, PR) - thr)));
    if(least == 10^9, next);
    cnt[q + 1]++;
    best[q + 1] = min(best[q + 1], least);
    if(least < 0, bad++; emit(Str("  BELOW: T=", T, " excess ", least))));
  emit(Str("nu=", nu, " b=", bs, " cols [", lo, ",", hi, "] 2valVand=", 2 * vv, " eps-orders <= ", MM));
  for(q = 0, r, if(cnt[q + 1], emit(Str("  q=", q, ": ", cnt[q + 1], " nonzero minors, least excess over threshold ", best[q + 1]))));
  emit(Str("  minors below threshold: ", bad));
};
run([1, 2, 4], [3, 5, 7], -3, 7);
run([1, 1, 3], [3, 5, 7], -3, 7);
run([1, 2, 3, 5], [3, 5, 7, 11], -3, 6);

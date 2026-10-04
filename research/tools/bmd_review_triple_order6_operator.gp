\\ Route review (cycle kep, 9 October 2026), desingularization lead: the order-six joint recurrence of the triple
\\ window's pair sequences g_ij(M) = [T^M] P Phi_ij (lem:cube-level-window-reduction; window M = d+3m..d+3m+4,
\\ d = binomial(m,2)).  At the least degree q* where order six appears (bmd_review_triple_order_floor.gp: q* = 18 at
\\ m = 2, 24 at m = 3), modulo p = 1000003: the kernel dimension; the least M from which the recurrence holds for all
\\ three sequences; and the integer roots M in [0, 400] of the leading coefficient P_6(M) and trailing P_0(M).
\\ With no such roots at or beyond the window start and validity there, a combination vanishing at six consecutive
\\ indices from the window start vanishes identically.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
p = 1000003;
lam = 3/2;
seqs(av, m, N) = {
  my(P = prod(l = 1, 3, (1 + av[l] * 'T)^m), pr = [[1, 2], [1, 3], [2, 3]]);
  vector(3, w, my(a = av[pr[w][1]], b = av[pr[w][2]], s = ((1 + a * 'T) * (1 + b * 'T) + O('T^N))^(-lam), rho = Mod(1, p), c = vector(N));
    for(k = 0, N - 1, if(k > 0, rho *= Mod(k, p) / Mod(k + lam - m, p)); c[k + 1] = rho * Mod(polcoef(s, k, 'T), p));
    my(S = Mod(1, p) * P * Ser(c, 'T)); vector(N, k, polcoef(S, k - 1, 'T)));
}
{
  foreach([[2, 5, -3], [1/3, -4, 7/2]], av, foreach([[2, 18], [3, 24]], mq, my(m = mq[1], q = mq[2], r = 6);
    my(X = seqs(av, m, 700), K0 = 3 * m + 5, nun = (r + 1) * (q + 1), per = nun \ 3 + 10);
    my(A = matrix(3 * per, nun, i, j, my(w = (i - 1) \ per + 1, k = K0 + (i - 1) % per, s = (j - 1) \ (q + 1), e = (j - 1) % (q + 1)); Mod(k, p)^e * X[w][k + s + 1]));
    my(K = matker(A), v = K[, 1], Pc = vector(r + 1, s, Pol(vector(q + 1, e, v[(s - 1) * (q + 1) + q + 2 - e]), 'M)));
    my(val(k) = vector(3, w, sum(s = 0, r, subst(Pc[s + 1], 'M, k) * X[w][k + s + 1])));
    my(first = K0); forstep(k = K0 - 1, 0, -1, if(val(k) == [0, 0, 0], first = k, break));
    my(ok = 1); for(k = K0, 600, if(val(k) != [0, 0, 0], ok = 0; break));
    my(d = m * (m - 1) / 2, ws = d + 3 * m);
    my(lead = select(k -> subst(Pc[r + 1], 'M, k) == 0, vector(401, k, k - 1)), trail = select(k -> subst(Pc[1], 'M, k) == 0, vector(401, k, k - 1)));
    emit(Str("roots ", av, " m=", m, " (r, q) = (6, ", q, "): kernel dim ", #K, "; holds for M >= ", first, " (checked to 600: ", ok, "); window M = ", ws, "..", ws + 4,
      "; integer roots in [0,400] of P_6: ", lead, ", of P_0: ", trail))));
}
quit;

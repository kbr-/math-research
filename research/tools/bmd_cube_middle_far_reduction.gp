\\ Middle-step far spaces of the even peeling: zero-free block unions (3 October 2026; cycle bmd-20261003-zzl).
\\ F_k (thm:cube-base-peeling-degeneration; e = k-1, l = b-k, c = 1): I = P_<R_e, C = <(1+x)^-3>, X0 = x^-(R_l+2) P_<R_l,
\\ II = (1+x)^(-7/2) P_<4e, IV = (1+x)^(-5/2) x^(1/2-4l) P_<4l, III = x^(-7/2+4e-4el) P_<4el.  Far degree (zeros off 0, -1) of the
\\ Wronskian of block unions, mod q = 2^61 - 1, for 3 <= b <= 6 (first run b <= 7 timed out at b = 7) and 2 <= k <= b-1 (blocks [g, b, cnt] = (1+x)^g x^b P_<cnt).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
q = 2^61 - 1;
Rn(n) = n * (2 * n - 1);
detH(bl) = {
  my(d = sum(i = 1, #bl, bl[i][3]), M = matrix(d, d), row = 0);
  foreach (bl, B, my(g = B[1], b = B[2]); for (j = 0, B[3] - 1, row++; my(h = Mod(1, q) * 'x^j);
    for (m = 0, d - 1, M[row, m + 1] = h; h = 'x * (1 + 'x) * deriv(h, 'x) + (b * (1 + 'x) + g * 'x - m * (1 + 2 * 'x)) * h)));
  matdet(M);
}
farpart(P) = { if (P == 0, return(-1)); my(a = valuation(lift(P), 'x)); P /= 'x^a; while (subst(P, 'x, -1) == 0, P /= (1 + 'x)); poldegree(P); }
default(parisizemax, 6000000000);
{
for (b = 3, 6, for (k = 2, b - 1,
  my(e = k - 1, l = b - k, I0 = [0, 0, Rn(e)], C = [-3, 0, 1], X0 = [0, -(Rn(l) + 2), Rn(l)], II = [-7/2, 0, 4 * e],
     IV = [-5/2, 1/2 - 4 * l, 4 * l], III = [0, -7/2 + 4 * e - 4 * e * l, 4 * e * l]);
  emit(Str("b=", b, " k=", k, " (e,l)=(", e, ",", l, "): far degrees I+C+II ", farpart(detH([I0, C, II])),
    ", I+X0 ", farpart(detH([I0, X0])), ", I+X0+C+II ", farpart(detH([I0, X0, C, II])),
    ", I+X0+C+II+III ", farpart(detH([I0, X0, C, II, III])), ", I+II+III ", farpart(detH([I0, II, III])),
    ", I+C+II+III ", farpart(detH([I0, C, II, III])), ", I+C+II+IV ", farpart(detH([I0, C, II, IV])), ", I+X0+II ", farpart(detH([I0, X0, II])),
    ", full ", farpart(detH([I0, C, X0, II, IV, III])),
    " (complement dims: of I+C+II ", Rn(l) + 4 * l + 4 * e * l, ", of I+X0+C+II ", 4 * l + 4 * e * l, ")"))));
}

\\ Odd last-step far space: which block unions have zero-free Wronskians? (3 October 2026; cycle bmd-20261003-zzj)
\\ F_b (odd peeling, l = 0, e = b - 1, c = 1; prop:cube-odd-last-far-mobius): P_<n (n = R_e), <(1+x)^-3>, (1+x)^(-7/2) P_<4e,
\\ (1+x)^(-5/2) x^(-3/2) P_<2, x^(-3/2) P_<2e.  Far degree (zeros off x = 0, -1) of the Wronskian of unions of blocks, mod
\\ q = 2^61 - 1, e = 1..4 (blocks [g, b, cnt] = (1+x)^g x^b P_<cnt; same h-recursion as bmd_cube_last_far_six_reduction.gp).
\\ A union with far degree 0 can be removed by Polya-Mammana, leaving the Wronskian of the complement's image.
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
default(parisizemax, 4000000000);
{
for (e = 1, 4,
  my(n = Rn(e), I0 = [0, 0, n], C = [-3, 0, 1], II = [-7/2, 0, 4 * e], IV = [-5/2, -3/2, 2], III = [0, -3/2, 2 * e]);
  emit(Str("e=", e, " (b = ", e + 1, ", dim ", n + 6 * e + 3, "): far degrees: P+II+III ", farpart(detH([I0, II, III])),
    ", P+II ", farpart(detH([I0, II])), ", P+III ", farpart(detH([I0, III])), ", P+C+II ", farpart(detH([I0, C, II])),
    ", P+II+III+C ", farpart(detH([I0, II, III, C])), ", P+II+III+IV ", farpart(detH([I0, II, III, IV])),
    ", full F_b ", farpart(detH([I0, C, II, IV, III])))));
}

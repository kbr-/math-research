\\ Zeros of the block-IV polynomials S_j after d^n, in t = x/(1+x) (3 October 2026; cycle bmd-20261003-zze).
\\ d_x^n [x^(j-7/2) (1+x)^(-5/2)] = x^(j-7/2-n) (1+x)^(-5/2-n) S_j(x), deg S_j <= n (by induction).  For e = 4..9 and j = 0..3: the
\\ |t| range of the zeros of S_j, their median |t|, and the median of N |Re log t| (N = n + 7/2), to compare with the four
\\ circles of conj:cube-last-far-four-circles (|t| about 0.66, 0.85, 1.08, 1.40 at e = 6).  Question: where does the two-term
\\ splitting S_j = (1+x)^N a_j + x^N b_j hold, i.e. where are the zeros of S_j?
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(realprecision, 80);
Rn(n) = n * (2 * n - 1);
dxf(f) = my(b = f[1], g = f[2], p = f[3]); [b - 1, g - 1, b * (1 + 'x) * p + g * 'x * p + 'x * (1 + 'x) * deriv(p, 'x)];
f4(z) = precision(z, 4) * 1.;
{
for (e = 4, 9,
  my(n = Rn(e), N = n + 7/2, out = List());
  for (j = 0, 3,
    my(f = [j - 7/2, -5/2, 1]); for (r = 1, n, f = dxf(f));
    my(S = f[3], z = polroots(S), tz = apply(x -> abs(x / (1 + x)), z), st = vecsort(tz));
    listput(out, Str("j=", j, ": deg ", poldegree(S), ", |t| in [", f4(st[1]), ", ", f4(st[#st]), "], median ", f4(st[(#st + 1) \ 2]))));
  emit(Str("e=", e, " (N = ", N, "): ", strjoin(Vec(out), "; "))));
}

\\ Cheap tests of the far-simplicity impasse review (4 October 2026; cycle bmd-20261004-d).
\\ (a) Uniform certificate prime (bridge): is the first window prime above max(d, 2n+5) always good, i.e. G_p of the
\\     last-step far polynomial has no factor of multiplicity >= 2 there, for e = 4..11 (saved W_(b-1))?
\\ (b) Density (Chebotarev lead): over all window primes above max(d, 2n+5), the fraction with G_p of multiplicity <= 1
\\     and the fraction with multiplicity <= 2, for e = 4..11, against the random-model expectation 1 - 1/p.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(parisizemax, 4000000000);
Rn(n) = n * (2 * n - 1);
src(e) = if (e <= 6, "research/results/bmd-20261003-zw", if (e == 7, "research/results/bmd-20261003-zy", if (e <= 9, "research/results/bmd-20261003-zz", "research/results/bmd-20261003-zzb")));
maxmult(W, p) = { my(F = factormod(W, p), mo = 0); for (i = 1, #F~, my(g = lift(F[i, 1])); if (g != 'x && g != 'x + 1, mo = max(mo, F[i, 2]))); mo; }
{
my(tot = 0, sq = 0, le2 = 0, expect = 0.);
for (e = 4, 11,
  my(W = read(Str(src(e), "/W_last_e", e, ".gp")), n = Rn(e), d = Rn(e + 2), lo = max(d, 2 * n + 5), hi = 2 * n + 8 * e + 7, first = 0, res = List());
  forprime (p = lo + 1, hi,
    my(m = maxmult(W, p)); listput(res, [p, m]); if (!first, first = [p, m]);
    tot++; if (m <= 1, sq++); if (m <= 2, le2++); expect += 1 - 1. / p);
  emit(Str("(a) e=", e, ": first window prime above max(d,2n+5) and its non-branch multiplicity: ", first, "; all [p, mult]: ", Vec(res))));
emit(Str("(b) e=4..11: ", tot, " window primes; G_p squarefree at ", sq, ", multiplicity <= 2 at ", le2, "; random-model expected squarefree count ", precision(expect, 4) * 1.));
}

\\ Review test (4 October 2026; cycle bmd-20261004-b): do the middle-step far polynomials collapse onto the branch points
\\ modulo suitable primes in Eisenstein form, as the last step does in its window?
\\ For each saved middle W_k (research/results/bmd-20261003-zzm/W_mid_b*_k*.gp, l = 2) and every prime p < 2 deg W_k with
\\ p not dividing lc, report the primes where W_k mod p has the factors x and x+1 to multiplicity >= 2, with v_p(W_k(0)),
\\ v_p(W_k(-1)) (an Eisenstein cluster needs 1) and the largest multiplicity of any other factor. (A first run required
\\ v_p = 1 at both points and found no prime.)
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(parisizemax, 2000000000);
{
foreach ([[6, 4], [7, 5], [8, 6]], bk,
  my(W = read(Str("research/results/bmd-20261003-zzm/W_mid_b", bk[1], "_k", bk[2], ".gp")), D = poldegree(W), lc = pollead(W), w0 = subst(W, 'x, 0), w1 = subst(W, 'x, -1), hits = List(), cnt = 0);
  forprime (p = 3, 2 * D,
    if (lc % p == 0 || w0 == 0, next);
    my(F = factormod(W, p), m0 = 0, m1 = 0, mo = 0);
    for (i = 1, #F~, my(g = lift(F[i, 1])); if (g == 'x, m0 = F[i, 2], if (g == 'x + 1, m1 = F[i, 2], mo = max(mo, F[i, 2]))));
    if (m0 >= 2 && m1 >= 2, cnt++; listput(hits, [p, m0, m1, mo, valuation(w0, p), valuation(w1, p)])));
  emit(Str("(b,k) = (", bk[1], ",", bk[2], "): deg ", D, "; primes p < 2 deg with clusters of size >= 2 at 0 and -1, as [p, mult x, mult x+1, largest other multiplicity, v_p W(0), v_p W(-1)]: ", Vec(hits))));
}

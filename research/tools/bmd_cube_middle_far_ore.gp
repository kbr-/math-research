\\ Ore residual polynomials of the middle-step cluster at -1 (4 October 2026; cycle bmd-20261004-f; Ore lead of the
\\ arithmetic route review).
\\ Tested statement (conj:cube-middle-far-ore-separable): at the collapse primes p of the saved middle far polynomials W_k
\\ (l = 2; (b,k) = (6,4), (7,5), (8,6)), the Newton polygon of W_k(y-1) at p has sides whose residual polynomials are
\\ separable over F_p. By Ore's theorem the roots of W_k with residue -1 are then simple, completing a one-prime
\\ certificate of multiplicity <= 2 per step together with the Eisenstein cluster at 0 and the non-branch bound.
\\ Residual polynomial of a side from (i0, v0) to (i1, v1) with slope -h/e (lowest terms): sum over lattice points
\\ (i0 + j e, v0 - j h) of (coefficient / p^(v0 - j h) mod p) T^j.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(parisizemax, 2000000000);
lowerhull(pts) = {
  my(H = List());
  foreach (pts, q, while (#H >= 2 && (H[#H][2] - H[#H - 1][2]) * (q[1] - H[#H][1]) >= (q[2] - H[#H][2]) * (H[#H][1] - H[#H - 1][1]), listpop(H)); listput(H, q));
  Vec(H);
}
{
foreach ([[6, 4, [53, 59, 61, 67, 71, 73, 79, 83]], [7, 5, [67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127]], [8, 6, [97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173]]], spec,
  my(W = read(Str("research/results/bmd-20261003-zzm/W_mid_b", spec[1], "_k", spec[2], ".gp")), V = subst(W, 'x, 'y - 1), out = List());
  foreach (spec[3], p,
    my(m = 0, pts = List());
    \\ only the part of positive slope matters: points up to the first coefficient of valuation 0
    for (i = 0, poldegree(V, 'y), my(c = polcoef(V, i, 'y)); if (c != 0, my(v = valuation(c, p)); listput(pts, [i, v]); if (v == 0, m = i; break)));
    my(H = lowerhull(Vec(pts)), allsep = 1, sides = List());
    for (s = 1, #H - 1,
      my(i0 = H[s][1], v0 = H[s][2], i1 = H[s + 1][1], v1 = H[s + 1][2], L = i1 - i0, dh = v0 - v1, g = gcd(L, dh), e = L / g, h = dh / g);
      my(R = sum(j = 0, g, my(c = polcoef(V, i0 + j * e, 'y)); if (c == 0, 0, if (valuation(c, p) == v0 - j * h, Mod(c / p^(v0 - j * h), p), 0)) * 'T^j));
      my(sep = (poldegree(gcd(R, deriv(R, 'T))) == 0));
      if (!sep, allsep = 0);
      listput(sides, [L, dh, g, sep]));
    listput(out, [p, m, allsep, Vec(sides)]));
  emit(Str("(b,k) = (", spec[1], ",", spec[2], "): [p, cluster size at -1, all residual polynomials separable, sides [length, height, gcd, separable]]: ", Vec(out))));
}

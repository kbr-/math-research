\\ debug: degrees and valuations of the saturated three-centre limit rows at (2,2,2)
default(parisizemax, 1000000000);
bet(j) = {my(v = if(j % 3 == 1, -1, 1)); j = j \ 3; while(j > 0, if(j % 3 == 2, return(0)); j = j \ 3); v};
{
my(ff = ffinit(3, 5, 'a), g = ffgen(ff, 'a), one = g^0, m = 'm, P = 12);
my(c = g^2, Q = m^2 - c, X = m^2 - 2 * m + c, Z = -m^2 + 2 * c * m - c, T = (X^2 - Q^2) / Q^2);
my(w0 = [one + 0 * m, X / Q, Z / Q], G = Q^(2 * P + 4) * X^(2 * P + 2) * Z^(2 * P + 2), sz = [2,2,2], lab = List());
for (t = 1, 3, for (q = 1, sz[t], listput(lab, [t, if(q == 1, 0 * one, g^(5 * t + 7 * q + 3 * t * q))])));
lab = Vec(lab); my(N = 6, pairs = List()); for (i = 1, N, for (j = i + 1, N, listput(pairs, [i, j]))); pairs = Vec(pairs);
my(r0 = G * T); print("deg G = ", poldegree(G), "; deg G*T = ", poldegree(lift(r0)), "; valuation(G*T, Q) = ", valuation(lift(r0), Q), "; valuation(G, m - g) = ", valuation(G, m - g));
my(h = lift(G * w0[2] * w0[3])); print("pair x z at order 0: deg ", poldegree(h), ", val Q ", valuation(h, Q), ", val X ", valuation(h, X));
print("type of lifted poly coefficient: ", type(polcoef(h, 0)));
}
quit;

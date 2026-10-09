\\ Saddle-point formula for the index of a product series against the exact index.
\\ Statement computed (about power series only): for S(z) = (1+z)^v (1 - q(z))^m, with q the series
\\ of the non-standard monomials of one row divided by (1+z)^k, the exact index D* of the first
\\ non-positive coefficient is compared with v * max over z > 0 of Phi(z) = z S'(z)/S(z) / v, i.e.
\\ Phi = z/(1+z) - (m/v) z q'(z)/(1 - q(z)).  Two row types: half-tables of largest immunity, and
\\ single clauses (one forbidden assignment, q = (z/(1+z))^k) at m = ceil(log(2) 2^k v).
\\ Output lines: type k v m Dstar Dstar/v maxPhi argmax_alpha, alpha = z/(1+z).
default(parisize, 4000000000);
halflevels(k) = { my(left = 2^(k-1), b = vector(k+1)); for(i = 0, k, b[i+1] = min(binomial(k,i), left); left -= b[i+1]); b };
dstar(v, k, m, h) = {
  my(N = v\2 + 2, S, d = -1);
  S = (1 + z + O(z^N))^(v - m*k) * (h + O(z^N))^m;
  for(j = 0, N-1, if(polcoeff(S, j) <= 0, d = j; break));
  d
};
maxphi(v, k, m, h) = {
  my(best = 0, arg = 0, hp = deriv(h, z));
  forstep(a = 0.02, 0.4995, 0.0005,
    my(x = a/(1-a), hv = subst(h, z, x), hpv = subst(hp, z, x), val);
    \\ ln S = (v - m k) ln(1+z) + m ln h ;  z S'/S = (v - m k) z/(1+z) + m z h'/h
    val = ((v - m*k)*x/(1+x) + m*x*hpv/hv)/v;
    if(val > best, best = val; arg = a));
  [best, arg]
};
{
my(v = 2048);
forstep(k = 12, 24, 4,
  my(b = halflevels(k), h = sum(i = 0, k, b[i+1]*z^i), m = v + k, d = dstar(v, k, m, h), r = maxphi(v, k, m, h));
  print("table ", k, " ", v, " ", m, " ", d, " ", precision(1.*d/v, 5), " ", precision(r[1], 5), " ", precision(r[2], 5)));
forstep(k = 8, 20, 4,
  my(h = (1+z)^k - z^k, m = ceil(log(2)*2^k*v), d = dstar(v, k, m, h), r = maxphi(v, k, m, h));
  print("clause ", k, " ", v, " ", m, " ", d, " ", precision(1.*d/v, 5), " ", precision(r[1], 5), " ", precision(r[2], 5)));
}
quit

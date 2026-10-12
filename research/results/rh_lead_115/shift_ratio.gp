\\ Statement tested (entry-2026-10-12, lead on structure functions).
\\ (A) Two numbers read in arXiv math/9812166 (its (3.2) and (3.4)), with xi(s) = s(s-1) pi^(-s/2) Gamma(s/2) zeta(s):
\\     Re{xi(1+282i)/xi(2+282i)} = -0.000131957, and at the 34th zero rho, -Re{xi'(rho) xi(1+rho)} = -5.3891...e-69.
\\ (B) prop:shift-ratio-sign for points on one line (taken as Re = 0): with F(s) = prod (s - i g_j),
\\     c at the lowest point equals prod_{j>1} (1 + i/d_j), d_j the height differences; for three simple points
\\     Re c < 0 exactly when d_1 d_2 < 1; and for every configuration of at least two points there is s with
\\     Re s > 0 and Re{F(s+1)/F(s)} < 0, found at height g_1 - eta where the sum of atan(1/(d_j + eta)) lies
\\     in (pi/2, pi).
\\ Expected, written before the run: (A) both numbers agree with the source to the digits it prints; (B) every
\\ row prints "ok".
\\ Refuted by: a computed value of (A) with the other sign or other leading digits, or a row of (B) printing FAIL.
\\ Possible because: the source's numbers could be mistranscribed or its normalisation misread, and the
\\ proposition's proof could be wrong in its choice of the point or in the sign of an argument.
\\ Independent route for (B): the ratio F(s+1)/F(s) is evaluated from the polynomial itself, not from the
\\ argument sum that chose the point.
default(realprecision, 120);
rhxi(s) = s*(s-1)*Pi^(-s/2)*gamma(s/2)*zeta(s);
print("A1 Re xi(1+282i)/xi(2+282i) = ", precision(real(rhxi(1+282*I)/rhxi(2+282*I)), 12));
rhz = lfunzeros(1, [111, 111.1]);
rhrho = 1/2 + I*rhz[1];
print("A2 height of the zero = ", precision(rhz[1], 25), "; zeros below 111.1: ", #lfunzeros(1, 111.1));
rhh = 10^(-40);
rhd = (rhxi(rhrho + rhh) - rhxi(rhrho - rhh))/(2*rhh);
print("A2 -Re xi'(rho) xi(1+rho) = ", precision(real(-rhd*rhxi(rhrho+1)), 12));
print("A2 |Re xi'(rho)| / |xi'(rho)| = ", precision(abs(real(rhd))/abs(rhd), 5), "  (xi' is imaginary on the line)");
rhF(g, s) = prod(j=1, #g, s - I*g[j]);
rhcheck(g) = {
  my(n = #g, c, th, eta, lo, hi, s, r, okc, pred);
  c = prod(j=2, n, 1 + I/(g[j]-g[1]));
  /* residue of F(s+1)/F(s) at the lowest point, from the polynomial */
  my(e = 10^(-30), res = e*rhF(g, I*g[1]+e+1)/rhF(g, I*g[1]+e));
  okc = abs(res - c) < 10^(-20);
  th = (x -> sum(j=1, n, atan(1/(g[j]-g[1]+x))));
  /* bisection for th(eta) = 3*Pi/4 when th(0+) > 3*Pi/4, else eta small */
  if(th(10^(-9)) > 3*Pi/4, lo = 10^(-9); hi = 10^6; for(k=1, 200, eta = (lo+hi)/2; if(th(eta) > 3*Pi/4, lo = eta, hi = eta)), eta = 10^(-9));
  eta = eta*1.; s = 10^(-12)*1. + I*(g[1]-eta);
  r = rhF(g, s+1)/rhF(g, s);
  pred = if(n == 3, if((g[2]-g[1])*(g[3]-g[1]) < 1, "Re c<0", "Re c>=0"), "-");
  print("B ", g, ": Re c = ", precision(real(c), 8), " [", pred, "] residue ", if(okc, "ok", "FAIL"),
        "; theta(eta) = ", precision(th(eta), 8), " at eta = ", precision(eta, 6),
        "; Re F(s+1)/F(s) = ", precision(real(r), 8), " ",
        if(real(r) < 0 && th(eta) > Pi/2 && th(eta) < Pi && (n != 3 || (real(c) < 0) == ((g[2]-g[1])*(g[3]-g[1]) < 1)), "ok", "FAIL"));
}
rhcheck([0, 5]);
rhcheck([0, 0.3]);
rhcheck([0, 0.5, 1.2]);
rhcheck([0, 2, 3]);
rhcheck([0, 0.9, 1.2]);
rhcheck([0, 1, 2, 3, 4, 5, 6, 7]);
rhcheck([-3, -1, 1, 3]);
\\ one point: the ratio has positive real part everywhere to the right
print("B one point: min over a grid of Re(1+1/s), Re s>0: ", precision(vecmin(vector(400, k, real(1+1/(10^(-3)*((k-1)\20+1) + I*(((k-1)%20)-10)/3)))), 8));
print("done");

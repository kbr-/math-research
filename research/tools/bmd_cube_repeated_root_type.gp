\\ Classify the multiple Wronskian roots at the repeated six-root discriminant factor.
\\
\\ Tested statement: at every F_p-rational root u0 of the exponent-four factor G found by
\\ bmd_cube_wronskian_discriminant.c (N = 6), every multiple root z0 of W_{a(u0)}(z) is a root of
\\ multiplicity three at which the mark has vanishing sequence (0,...,R-1,R+1,R+3): moving the
\\ mark to z0 (b_i = 1/(a_i - z0)), the pair matrices A_L(b) = (H_k(b_i,b_j)), 0 <= k <= L, give
\\   rank A_{R-2} = R-2 (two independent sections with contact >= R+1),
\\   rank A_R     = R-1 (one section with contact >= R+3),
\\   rank A_{R+1} = R   (no section with contact >= R+4, so the next prefix is onto there).
\\ Each repeated root is examined over the splitting field of its factor (degree one or two).
\\ Input: DATA.gp defining alpha, beta and G.  Usage: gp -q DATA.gp bmd_cube_repeated_root_type.gp
default(parisizemax, 2000000000);
p = 2^61 - 1;
N = 6; R = N*(N-1)/2; lam = 3*binomial(N,4); th = 4*lam/N;
beta32(m) = binomial(-3/2, m);
Hk(k, x, y) = sum(m = 0, k, beta32(m) * beta32(k - m) * x^m * y^(k - m));
pairs = vector(R); pc = 0; for (i = 1, N, for (j = i + 1, N, pc++; pairs[pc] = [i, j]));
Amat(b, L) = matrix(R, L + 1, r, k, Hk(k - 1, b[pairs[r][1]], b[pairs[r][2]]));
F(b) = matdet(Amat(b, R - 1)) / prod(r = 1, R, (b[pairs[r][1]] - b[pairs[r][2]])^(N-2));
W(a, z) = F(vector(N, i, 1/(a[i] - z))) * prod(i = 1, N, a[i] - z)^th;
Gm = Mod(1, p) * G;
fa = factor(Gm);
lin = [];
for (k = 1, #fa~, if (poldegree(fa[k,1]) == 1, lin = concat(lin, [-polcoef(fa[k,1], 0) / polcoef(fa[k,1], 1)])));
print("F_p-rational roots of G: ", #lin);
{
for (t = 1, #lin,
  u0 = lin[t];
  a = vector(N, i, Mod(alpha[i], p) + Mod(beta[i], p) * u0);
  zs = vector(2*lam + 1, h, Mod(h + 7, p));
  w = polinterpolate(zs, vector(#zs, h, W(a, zs[h])));
  g = gcd(w, deriv(w));
  gf = factor(g);
  for (k = 1, #gf~,
    q = gf[k,1];
    ff = ffgen(q, 'y);
    wf = lift(w) * ff^0;
    m = 0; ww = wf; while (subst(ww, 'x, ff) == 0, m++; ww = deriv(ww));
    b = vector(N, i, 1/(lift(a[i]) * ff^0 - ff));
    print("u0 #", t, " factor degree ", poldegree(q), ": root multiplicity ", m,
          "; ranks A_{R-2}, A_R, A_{R+1} = ", matrank(Amat(b, R - 2)), ", ",
          matrank(Amat(b, R)), ", ", matrank(Amat(b, R + 1)),
          "  (full ", R - 1, ", ", R, ", ", R, ")")));
}

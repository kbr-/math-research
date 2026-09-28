\\ Real-rootedness test for the quadratic-series Wronskian covariant (non-crossing bridge).
\\
\\ Tested statement (falsification test of a hyperbolicity hypothesis): for real distinct branch
\\ points a_1..a_N, every root of W_a(z) = F(1/(a_i - z)) prod(a_i - z)^theta is real, where
\\ F(b) = det(H_k(b_i,b_j))_{i<j,0<=k<R} / prod(b_i - b_j)^{N-2}.  W_a is computed exactly over Q
\\ by interpolation at 2 lambda + 1 integer points; polsturm counts its real roots.
\\ Usage: gp -q bmd_cube_wronskian_real_roots.gp   (N and the configurations are fixed below)
default(parisizemax, 2000000000);
N = 5; R = N*(N-1)/2; lam = 3*binomial(N,4); th = 4*lam/N;
beta32(m) = binomial(-3/2, m);
Hk(k, x, y) = sum(m = 0, k, beta32(m) * beta32(k - m) * x^m * y^(k - m));
pairs = vector(R); pc = 0; for (i = 1, N, for (j = i + 1, N, pc++; pairs[pc] = [i, j]));
F(b) = matdet(matrix(R, R, r, k, Hk(k - 1, b[pairs[r][1]], b[pairs[r][2]]))) / prod(r = 1, R, (b[pairs[r][1]] - b[pairs[r][2]])^(N-2));
W(a, z) = F(vector(N, i, 1/(a[i] - z))) * prod(i = 1, N, a[i] - z)^th;
configs = [[0, 1, 3, 7, 12], [-5, -2, 1, 4, 11], [0, 1, 2, 3, 4]];
{
for (c = 1, #configs,
  a = configs[c];
  zs = vector(2*lam + 1, h, 100 + 2*h);
  w = polinterpolate(zs, vector(#zs, h, W(a, zs[h])));
  print("a = ", a, ": deg W = ", poldegree(w), ", real roots = ", polsturm(w),
        ", squarefree = ", poldegree(gcd(w, deriv(w))) == 0));
}

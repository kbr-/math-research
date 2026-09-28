p = 2^61 - 1;
N = 6; R = N*(N-1)/2;
beta32(m) = binomial(-3/2, m);
Hk(k, x, y) = sum(m = 0, k, beta32(m) * beta32(k - m) * x^m * y^(k - m));
pairs = vector(R); pc = 0; for (i = 1, N, for (j = i + 1, N, pc++; pairs[pc] = [i, j]));
F(b) = matdet(matrix(R, R, r, k, Hk(k - 1, b[pairs[r][1]], b[pairs[r][2]]))) / prod(r = 1, R, (b[pairs[r][1]] - b[pairs[r][2]])^(N-2));
b = vector(N, i, Mod(random(p), p));
c = Mod(random(p), p);
print("F(b+c)/F(b) = ", F(b + vector(N, i, c)) / F(b));
print("F(2b)/F(b)/2^45 = ", F(2*b) / F(b) / 2^45);
\\ inversion covariance test of W(a,z) = F(1/(a-z)) prod(a-z)^theta, theta = 4*lambda/N
lam = 3*binomial(N,4); th = 4*lam/N;
W(a, z) = F(vector(N, i, 1/(a[i] - z))) * prod(i = 1, N, a[i] - z)^th;
a = vector(N, i, Mod(random(p), p)); z = Mod(random(p), p);
\\ Moebius g: w -> 1/w.  Covariance predicts W(1/a, 1/z) = W(a, z) * z^(-2 lam) * prod(a)^(-th) up to a constant
r1 = W(vector(N, i, 1/a[i]), 1/z) / (W(a, z) * z^(-2*lam) * prod(i = 1, N, a[i])^(-th));
a2 = vector(N, i, Mod(random(p), p)); z2 = Mod(random(p), p);
r2 = W(vector(N, i, 1/a2[i]), 1/z2) / (W(a2, z2) * z2^(-2*lam) * prod(i = 1, N, a2[i])^(-th));
print("inversion ratio constant: ", r1 == r2, "  ratios ", r1, " ", r2);

\\ Two-double divisibility (7 October 2026; cycle bmd-20261007-r).  Tested statement: for every column set S of size
\\ 2M+5, the minor on S of the rows (1+T) phi_(y_s), (1+T) T phi_(y_s) (phi_y = (1+yT)^(-3/2)) and T^i (1+BT)^(-7/2)
\\ (i <= 4) is divisible by prod (y_t - y_s)^4 prod (y_s - B)^8.  M = 1 (all 7-subsets of columns 0..9) and M = 2
\\ (a sample of 9-subsets of columns 0..11).  Prints the number of column sets tested and of failures.
default(parisizemax, 2 * 10^9);
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
bn(x, k) = if (k < 0, 0, binomial(x, k));
cs(y, e, k) = bn(-3/2, k - e) * y^max(k - e, 0) + bn(-3/2, k - e - 1) * y^max(k - e - 1, 0);
cb(B, i, k) = bn(-7/2, k - i) * B^max(k - i, 0);
rowsm(ys, ncol) = { my(M = #ys, A = matrix(2 * M + 5, ncol), r = 0);
  for (s = 1, M, r++; for (c = 1, ncol, A[r, c] = cs(ys[s], 0, c - 1)); r++; for (c = 1, ncol, A[r, c] = cs(ys[s], 1, c - 1)));
  for (i = 0, 4, r++; for (c = 1, ncol, A[r, c] = cb('B, i, c - 1))); A; }
{
my(A1 = rowsm(['y1], 10), P1 = ('y1 - 'B)^8, n = 0, bad = 0);
forsubset([10, 7], S, my(D = matdet(vecextract(A1, "..", Vec(S)))); n++; if (D != 0 && D % P1 != 0, bad++));
emit(Str("M = 1: ", n, " column sets of 0..9, ", bad, " minors not divisible by (y1-B)^8"));
my(A2 = rowsm(['y1, 'y2], 12), P2 = ('y1 - 'B)^8 * ('y2 - 'B)^8 * ('y1 - 'y2)^4, cnt = 0);
n = 0; bad = 0;
forsubset([12, 9], S, cnt++; if (cnt % 11 != 1, next); my(D = matdet(vecextract(A2, "..", Vec(S)))); n++; if (D != 0 && D % P2 != 0, bad++));
emit(Str("M = 2: ", n, " sampled column sets of 0..11, ", bad, " minors not divisible by (y1-B)^8 (y2-B)^8 (y1-y2)^4"));
}

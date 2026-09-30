\\ Is the pair code MDS? (30 September 2026; route review bmd-20260930-x, coding-theory bridge.)
\\ Tested statement: at a random configuration over F_p, p = 2^61 - 1, every maximal (R x R) minor of the
\\ R x (R+2) matrix A_(R+1) = (H_k(a_i,a_j))_(k <= R+1) is nonzero, i.e. the row space is an MDS code of
\\ length R+2 and dimension R (every R columns independent). A zero minor that persists at several random
\\ configurations is an identically vanishing minor and falsifies the translation. N = 5, 6.
p = 2^61 - 1;
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
beta32(m) = binomial(-3/2, m);
Hk(k, x, y) = sum(m = 0, k, beta32(m) * beta32(k - m) * x^m * y^(k - m));
prs(N) = my(v = List()); for (i = 1, N, for (j = i + 1, N, listput(v, [i, j]))); Vec(v);
{
setrand(20260930);
foreach ([5, 6], N,
  my(P = prs(N), R = #P);
  for (trial = 1, 3,
    my(a = vector(N, i, Mod(random(p), p)), A = matrix(R, R + 2, r, k, Hk(k - 1, a[P[r][1]], a[P[r][2]])), zero = List());
    forsubset([R + 2, 2], del, my(cols = setminus([1..R + 2], Vec(del))); if (matdet(vecextract(A, "..", cols)) == 0, listput(zero, Vec(del) - [1, 1])));
    emit(Str("N=", N, " trial ", trial, ": maximal minors ", binomial(R + 2, 2), ", zero minors (deleted column orders) ", Vec(zero)))));
}

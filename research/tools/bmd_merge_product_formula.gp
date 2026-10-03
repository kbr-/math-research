\\ Control for the merge product formula (cycle kbn, 9 October 2026).
\\ Statement: for A >= B >= 0, det[binom(1/2, A+1+i-j)]_{0<=i,j<=B}
\\   = +- prod_{k=1}^{B+1} (2A-2k+1)!! (2k-1)!! (k-1)! / (2^(A+1) (A+k)!),
\\ and the merge block M_{A,B} = [binom(i,j)], i = A+B+2..2A, j = 2B+3, 2B+5, .., 2A-1
\\ (lem:cube-unbalanced-merge-criterion) is singular mod p iff v_p of that product is positive.
\\ Part (a): exact identity over Q for A, B <= 14.  Part (b): the two singularity tests agree for
\\ p = 3, 5, 7, 11 and 0 <= B <= A <= 40.

dfact(m) = if(m <= 0, 1, prod(i = 0, (m - 1) \ 2, m - 2 * i));  \\ m!! for odd m >= -1
formula(A, B) = prod(k = 1, B + 1, dfact(2*A - 2*k + 1) * dfact(2*k - 1) * (k - 1)! / (2^(A + 1) * (A + k)!));
carries(x, y, p) = (sumdigits(x, p) + sumdigits(y, p) - sumdigits(x + y, p)) / (p - 1);
toep(A, B) = matdet(matrix(B + 1, B + 1, i, j, my(m = A + 1 + (i - 1) - (j - 1)); if(m < 0, 0, binomial(1/2, m))));
block(A, B, p) = { my(m = A - B - 1); if(m <= 0, return(1));
  matdet(matrix(m, m, a, b, Mod(binomial(A + B + 1 + a, 2 * (B + b) + 1), p))); }

{
my(bad = 0);
for(A = 0, 14, for(B = 0, A, if(abs(toep(A, B)) != abs(formula(A, B)), bad++; print("identity fails at ", [A, B]))));
print("(a) identity |Toeplitz| = |product| for 0 <= B <= A <= 14: ", if(bad, "FAILS", "holds"));
foreach([3, 5, 7, 11], p,
  my(mism = 0, sing = 0);
  for(A = 0, 40, for(B = 0, A,
    my(s1 = valuation(formula(A, B), p) > 0, s2 = block(A, B, p) == 0);
    sing += s1; if(s1 != s2, mism++; print("mismatch p=", p, " ", [A, B]))));
  print("(b) p=", p, ": ", sing, " singular pairs of 861 by the formula; mismatches with the block test: ", mism));
\\ Part (c): the carry form v_p = sum_k [carries(m+m) - carries(m+(2k-1))], m = A+1-k (Kummer).
foreach([3, 5, 7, 11], p,
  my(mism = 0);
  for(A = 0, 40, for(B = 0, A,
    my(v = sum(k = 1, B + 1, my(m = A + 1 - k); carries(m, m, p) - carries(m, 2*k - 1, p)));
    if(v != valuation(formula(A, B), p), mism++)));
  print("(c) p=", p, ": carry form against the product's valuation, mismatches: ", mism));
}
quit;

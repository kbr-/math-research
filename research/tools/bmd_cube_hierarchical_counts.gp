\\ Local-exponent counts of the hierarchical double-root pair spaces (29 September 2026).
\\ Space V^(a): N roots, a double roots D_1..D_a in collision order, n = N - 2a simple roots k.
\\ Rows: phi_k phi_l; phi_D phi_k, phi_D' phi_k; phi_D^2; for r < s the block
\\ V7(r,s) = T^j (1+D_r T)^(-5/2) (1+D_s T)^(-7/2), j = 0..3 (the later double gets -7/2).
\\ Count: T(a) = (#branch - 2) E - 3R - sum over branch values of the minimal exponent sum,
\\ which is the degree bound minus the minimal multiplicities (pole orders cancel).
\\ Minimal exponent sums: simple value: half class -3/2 + {0..N-2}, integral {0..R-N};
\\ double with no earlier double: half class -5/2 + {0..2N-5}; with an earlier double: -7/2 + ...;
\\ integral class {-3} u {0..binom(N-2,2)-1}.
\\ Tested statements:
\\  (1) T(0), T(1), T(2) agree with the record's T_sep = binom(N-2,2) + 2(N-2)(N-3) + T_conf,
\\      T_conf and T_dir (prop:cube-directional-two-double-count), symbolically in N;
\\  (2) the level differences T(a) - T(a+1), compared with face + neck counts
\\      binom(M,2) + 2M(M-1-a), M = N-2, where the neck count 2M(M-1-a) is what the
\\      multi-double window ranks (a + 1 singular top windows) allow.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
ms(N) = my(R = binomial(N, 2)); -3/2 * (N - 1) + binomial(N - 1, 2) + binomial(R - N + 1, 2);
md(N, c) = my(K = 2 * N - 4); -c * K + binomial(K, 2) - 3 + binomial(binomial(N - 2, 2), 2);
T(N, a) = {
  my(R = binomial(N, 2), E = binomial(R, 2), n = N - 2 * a);
  (N - a - 2) * E - 3 * R - n * ms(N) - if (a >= 1, md(N, 5/2) + (a - 1) * md(N, 7/2), 0);
}
Tdir(N) = my(R = binomial(N, 2), E = binomial(R, 2), Sd = -5 * (N - 2) + binomial(2 * N - 4, 2) - 3 + binomial(binomial(N - 2, 2), 2), msv = binomial(N - 1, 2) + binomial(R - N + 1, 2)); (N - 4) * E - 4 * N + 2 - 2 * Sd - (N - 4) * msv;
Tconf(N) = binomial(N - 2, 2) + 2 * (N - 2) * (N - 4) + Tdir(N);
Tsep(N) = binomial(N - 2, 2) + 2 * (N - 2) * (N - 3) + Tconf(N);
main() = {
  emit(Str("check T(1) - Tconf, T(2) - Tdir, T(0) - Tsep (symbolic in N): ",
    [T(x, 1) - Tconf(x), T(x, 2) - Tdir(x), T(x, 0) - Tsep(x)]));
  emit(Str("T(a) - T(a+1) - [binom(M,2) + 2M(M-1-a)], M = N-2, symbolic in N, a = 0..4: ",
    vector(5, i, my(a = i - 1, M = x - 2); T(x, a) - T(x, a + 1) - (binomial(M, 2) + 2 * M * (M - 1 - a)))));
  emit(Str("T(a) - T(a+1) - [binom(M,2) + 2M(M-2)], a = 1..4: ",
    vector(4, a, my(M = x - 2); T(x, a) - T(x, a + 1) - (binomial(M, 2) + 2 * M * (M - 2)))));
  for (N = 5, 10, emit(Str("N=", N, " T(a), a = 0..", N \ 2, ": ", vector(N \ 2 + 1, i, T(N, i - 1)))));
  emit(Str("known: Tsep(5)=30 Tconf(5)=15 Tconf(6)=60 Tdir(5)=6 Tdir(6)=38 -> ",
    [T(5, 0), T(5, 1), T(6, 1), T(5, 2), T(6, 2)]));
}
main();

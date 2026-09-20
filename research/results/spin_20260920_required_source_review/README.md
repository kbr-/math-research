# Prime-field MOD-frame NS certificates

The full theorem and proof are in notebook entry
`entry-2026-09-20-prime-modular-source`. The finite artifact tests its local MOD
frame, not the full Frege-to-PHP boundary or source-exclusion theorem.

Reproduce from the repository root, with the standard resource controls active:

```bash
./compute.sh g++ -std=c++20 -O2 -Wall -Wextra -Werror \
  research/tools/check_prime_mod_frame.cpp -o /tmp/check_prime_mod_frame
./compute.sh /tmp/check_prime_mod_frame --out /tmp/mod-frame-certificates.json
```

`mod-frame-certificates.json` contains every coefficient of the frame polynomial,
its two NS cofactors, the relations `a^2-a` and `t^p-t`, the nonzero remainder
when the field relation is omitted, and the recursion-interpolation target and
cofactor. A term is `[t_exponent, a_exponent, coefficient]`, reduced modulo the
case's prime. A degree of `-1` denotes the zero polynomial.

The C++ checker reconstructs each certificate exactly, checks all grid points,
verifies the general degree ceilings, and checks that the missing-field control
is nonzero. Cases are fixed at 2, 3, 5 and 7; this is a bounded check, not an
exhaustive theorem test. Sparse compiled arithmetic uses two-variable polynomials
of degree at most 60 and has a negligible memory budget compared with the shared
10 GB limit. No dependencies were installed.

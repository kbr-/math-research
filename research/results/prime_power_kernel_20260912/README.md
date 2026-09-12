# Prime-power kernel verification

`pc_boundary.hpp` now computes a prime-th polynomial power by Frobenius:
coefficients stay in the same prime field and every monomial exponent is
multiplied by p. This is an ordinary-polynomial identity, with no Boolean or
field-domain reduction of variables. It avoids intermediate cross terms that
would later cancel. Other nonnegative exponents retain the existing algorithm.

The exponent-255 guard is preserved, and negative exponents now fail explicitly.
The kernel's existing prime-field assumptions are unchanged.

## Reproduce

```bash
./compute.sh run CHECK --threads 1 --category local_processing --timeout 60 -- \
  g++ -O2 -std=c++17 -Wall -Wextra -pedantic \
  research/tools/check_prime_power_kernel.cpp -o /tmp/check_prime_power_kernel
./compute.sh run CHECK --threads 1 --category local_processing --timeout 60 -- \
  /tmp/check_prime_power_kernel --out PATH-TO-NEW-OUTPUT.jsonl
```

`checks-01.jsonl` preserves 39 exact polynomial comparisons over primes 2, 3,
5, 7 against independent repeated multiplication. They cover zero and constant
polynomials, mixed higher-degree polynomials, generic exponents, and the largest
accepted univariate exponent. Five guard cases cover matching overflow rejection
and negative-exponent rejection. Every check passed.

This is a software-kernel check, not a new mathematical research result or a
performance benchmark. No historical research suite was rerun. The work is timed
in `column_statistic_freezing_20260912_54` as the separate framework improvement
following the categorical-profile checkpoint. `provenance.json` records sources
and complete output.

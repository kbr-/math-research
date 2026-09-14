# Shared ordinary prime-power optimization

The sparse polynomial kernel now uses prime-field Frobenius when the exponent
equals its coefficient prime. Each monomial's exponents are multiplied by p;
coefficients stay in Fp. No Boolean or field-domain reduction occurs, and the
existing degree and term guards remain active.

This consolidates the local shortcut used by the shared-probe checker and
matches the optimization already present in the separate primitive-PC kernel.
Other powers continue using the existing multiplication routine.

Reproduce the focused checks from the repository root:

~~~sh
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -O2 -std=c++17 -Wall -Wextra research/tools/check_polynomial_prime_power.cpp \
  -o /tmp/math-prime-power-kernel-check
./compute.sh run TURN --threads 1 -- \
  /tmp/math-prime-power-kernel-check --out NEW_OUTPUT_PATH
~~~

validation.jsonl preserves 20 exact comparisons against independent repeated
multiplication over F2, F3, F5, and F7, including adjacent exponents, zero and
constant inputs. Four control groups check ordinary powers, the degree limit,
and negative exponents.

The shared-probe checker was rebuilt against the changed kernel and its full
57-certificate output was compared byte-for-byte with the accepted research
output. The result is recorded in reproduction.json. Temporary output is an
exact duplicate; the accepted research file remains the canonical evidence.

# Complete quadratic-source endpoint: low-case controls

The full end-to-end working theorem is in notebook entry
`entry-2026-09-20-general-quadratic-source`. This fixture checks its low-case
weighted interpolation over a satisfiable Boolean base; it is not a full PHP
instance or a computation of the structural dichotomy.

There are seven old variables x0,...,x6. Put e=x5*x6, f=x1+x2 and
G=(x0*x1+e, x0*x2+e, x0*x3+e, x0*x4+e). At x0=0, every input is the exceptional
quadratic e. At x0=1, the affine difference g1+g2=f supplies the weighted clamp.
The coefficient images are beta1=1+x0+x0*f, beta2=x0, beta3=beta4=0.
The accuracy-one product is P=1+sum beta_i*g_i over F2.

`weighted-branch-certificates.json` retains ordinary polynomials and all NS
cofactors for f*g_i*P and f*(beta_i^2+beta_i), four of each. Each certificate is
reconstructed exactly and has zero Boolean remainder. The source companion
has degree five, source coefficient Booleanity degree two, substitution degree
T=2 and weight degree one. The allowed old ceilings are therefore eleven and
five, respectively; actual certificate ceilings are also reported.

Each monomial integer encodes the exponent of xi in nibble i. Coefficients are
one in F2; absent monomials have coefficient zero. Ordinary exponents are retained
until division by xi^2+xi, so Boolean reduction does not silently reset the costs.
The JSON also retains nonzero remainders after omitting either the affine-branch
term or the exceptional low-branch term from beta1.

The workload is fixed and tiny: seven variables, eight certificates and two
controls, with no adjustable search-size input. Reproduce with active controls:

```bash
./compute.sh g++ -std=c++17 -O2 -Wall -Wextra -Werror \
  research/tools/check_weighted_quadratic_branch.cpp -o /tmp/check_weighted_quadratic_branch
./compute.sh /tmp/check_weighted_quadratic_branch --out /tmp/weighted-branch-certificates.json
```

The build and all checks passed. The preceding structural cycle's rank evidence
is reused as recorded, not rerun. The general proof remains a human working proof;
these certificates neither establish its asymptotic parameter bounds nor replace
independent expert review or a prior-art audit.

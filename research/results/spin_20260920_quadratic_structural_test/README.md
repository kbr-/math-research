# Binary quadratic structural controls

The full statements and proofs are in notebook entry
`entry-2026-09-20-quadratic-space-dichotomy`. The complete source exclusion is a
separate subsequent audit, not a conclusion of these finite checks.

`check_quadratic_rank_structure.cpp` has a fixed workload: four field-product
polar spaces, at most 15 nonzero combinations per space, at most 256 sampled
solutions per selected direction, and matrices no larger than 64 by 64.
There is no arbitrary input size. The cases (a,v) are (1,4), (2,16), (3,40), (4,64),
with field degrees 2,8,20,32 and field polynomials recorded in the JSON. Each
polynomial is independently checked for irreducibility by Frobenius/gcd tests.

For q_c(x,y)=Tr(cxy), the checker forms the exact alternating matrices, checks all
nonzero binary combinations of the a selected forms, and constructs 2a directions
with the prescribed diagonal cross-pairings and independent polar images. It
records the full coordinate basis, original and transformed polar matrices, and
linear parts of the transformed multilinear quadratic functions. Unsigned integers
encode bit vectors (bit j is coordinate j); each polar-row integer encodes one
matrix row. The JSON's seed is the exact initial xorshift state.

All four cases pass, with 20 sampled candidates total; minimum ranks are
4,16,40,64. Replacing the first selected direction by zero is detected by the
pairing check. A separate six-variable control has all three nonzero binary
combination ranks equal to four, but a combination over F8 has rank six; the
radical of a binary maximum-rank matrix is explicitly not common isotropic.
This checks the reason the proof passes through generic extension-field rank.

Reproduce from the repository root with the resource controls already active:

```bash
./compute.sh g++ -std=c++17 -O2 -Wall -Wextra -Werror \
  research/tools/check_quadratic_rank_structure.cpp -o /tmp/check_quadratic_rank_structure
./compute.sh /tmp/check_quadratic_rank_structure --out /tmp/rank-structure-checks.json
```

The first compile failed on a helper-name collision with std::apply and a
misleading-indentation warning. Both were fixed; the accepted source compiles
with warnings treated as errors. The complete accepted output is
`rank-structure-checks.json`. No numerical test of Bogolyubov-Ruzsa, large branch
family, or source exclusion was performed. The imported theorem's exact source
and reading scope are recorded in `sources.json`; no third-party full text is
published here.

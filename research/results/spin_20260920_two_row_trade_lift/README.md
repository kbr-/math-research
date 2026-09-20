# Two-row matching lifts and coordinatewise product codes

The notebook's [degree-one two-row criterion](https://kbr.is-a.dev/math-research/#two-row-product-code-lift)
characterizes the image by the diagonal quotient of two evaluation kernels.
This checker tests that criterion, an explicit incompatible eight-label target,
and complete coordinate-unit product witnesses on sixteen labels. It does not
construct a complete source design or prove a higher-degree lifting theorem.

Reproduce using a fresh output path:

```bash
./compute.sh --threads 1 g++ -O2 -std=c++17 -Wall -Wextra -Werror \
  research/tools/check_two_row_code_lift.cpp -o /tmp/check_two_row_code_lift
./compute.sh --threads 1 /tmp/check_two_row_code_lift --out /tmp/two-row-code-checks.json
```

The six fixed cases use primes 2, 3 and 5 and bit cubes with 3 or 4 bits.
Labels are integers in increasing order; predicate a is `(label >> a) & 1`,
starting at bit zero. All array entries are canonical field residues. There
is no randomness or large search: at most 240 off-diagonal source unknowns
and 160 marginal/conditioning equations.

Output includes the evaluation matrix (constant row, then bits), a nullspace
basis, every product of two basis vectors with indices a<=b, and exact ranks.
Source columns are ordered `(k,l)` lexicographically, omitting k=l. Marginal
rows are first the N row sums, then N column sums. Conditioning rows are all
first-row predicates with the second-row label varying fastest, followed by
second-row predicates with the first-row label varying fastest. This ordering
specifies the saved dual against the complete marginal/conditioning matrix.

For eight labels, output contains the full target (z then w), the dual vector
and its value -1 on the requested right side. The checker verifies target
zero sums and commuting contractions, annihilation of every source column
by the dual, and a one-dimensional augmented-rank increase. The compatible
space has dimension 33, actual image 32 and product-code rank 7 in every field.
For sixteen labels those dimensions are 104, 104 and 16. Every coordinate unit
has two saved codewords whose product is that unit; these are disjoint-direction
signed squares. All claimed identities pass exact modular checks.

The symbolic proofs work over every field; these finite checks are corroboration,
not a replacement. One initial build failed two misleading-indentation warnings,
fixed before the accepted build. The cycle also contains a context restoration
and a brief public Pages-status recheck, confirming two successful deployments
following the earlier transient failure. No publication tooling was changed.

# Growing binary field-product sources

The [notebook entry](https://kbr.is-a.dev/math-research/#entry-2026-09-14-large-field-product-source)
contains the working finite theorem and full source transfer. It replaces
the degree-d inverse witness with a degree-preserving reduction in conjugate
coordinates. Their correct domain equations are X_j^2-X_(j+1), with cyclic
indices. These and the diagonal product equations pull back to the original
binary generators through degree two.

The reduction image has binary dimension at most d*J(v,d,k). A coefficient
projection preserving one descends its kernel witnesses back to F2 before
any ENS coefficient map is defined. For d=Theta(v), polynomial inventory
and polylogarithmic source degree, the old degree is sqrt(n)*polylog(n).
General bilinear tensors, later nonlinear levels, and odd-prime source
compilation are not covered by this theorem.

## Reproduce

From the repository root, with resource controls and an active timing session:

~~~sh
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -O2 -std=c++17 -Wall -Wextra \
  research/tools/check_conjugate_field_source.cpp -o /tmp/math-conjugate-field-source
./compute.sh run TURN --threads 1 --timeout 180 -- \
  /tmp/math-conjugate-field-source --out NEW_MAIN_OUTPUT
./compute.sh run TURN --threads 1 --timeout 180 -- \
  /tmp/math-conjugate-field-source --out NEW_DESCENT_OUTPUT --unital-descent-only
~~~

Output paths must be new. No dependencies were installed. The auxiliary
arithmetic is represented by vectors of binary polynomials, so ordinary
variable powers and extension-field coefficients are kept distinct.
The shared binary monomial-reduction core applies because the conjugate
divisors themselves have binary coefficients in their coordinate variables.

## Evidence schema and main run

Both JSONL files encode polynomials as
`[coefficient,[variable IDs with repetitions]]`. For extension certificates,
coefficients are polynomial-basis bitmasks modulo the specified binary
irreducible polynomial; binary certificates use zero or one. Large parameter
integers are exact decimal strings. Coordinate variables start at ID 64.

`conjugate-field-source-checks.jsonl` contains 905 ordinary NS certificates:
457 over the specified auxiliary fields and 448 over F2. The fields have
dimensions 1,2,3,4 and modulus bitmasks 3,7,11,19. Both directions of every
conjugate-coordinate change are checked, and all Moore matrices and their
inverses are retained.

The certificate counts are:

- 34 extension-field pullbacks of every coordinate divisor to original
  Boolean and input generators, through degree two;
- 416 reductions of every ordinary monomial through degree three in
  3,5,7,9 old variables, each retaining both its auxiliary-field and binary
  witness;
- four selected strict kernels, each with both witness versions;
- three nonquotient relations, each with both witness versions;
- 25 complete weighted binary source-axiom images.

Every witness is reconstructed and every ordinary generator multiple is
charged. The complete binary kernel matrices, RREFs, pivots, bases, and
selected targets are saved:

| Field dimension | Matrix rows | Columns | Rank | Kernel dimension |
| --- | ---: | ---: | ---: | ---: |
| 1 | 6 | 1 | 0 | 1 |
| 2 | 36 | 10 | 6 | 4 |
| 3 | 138 | 35 | 26 | 9 |
| 4 | 392 | 84 | 68 | 16 |

Rows encode a normal monomial and a coefficient coordinate; columns are
homogeneous squarefree cubic old monomials. The selected targets in field
dimensions 2,3,4 have nonzero old-Boolean corrections. Their selected
extension witnesses happen to already have binary cofactors, which motivates
the separate nontrivial descent control below.

The nonquotient control reduces X0^2*Z0 to the nonzero X1*Z0 despite the
original polynomial being a multiple of the input X0*Z0. Its ordinary
degree-three ideal witness is retained. The reduction is a sufficient
linear kernel map, not a canonical quotient normal form.

## Complete source and descent controls

The actual source fixture has five old bits, four reused rank-two bottoms,
and a two-input field-product parent, on fifteen variables. It uses the
selected strict cubic kernel and its descended linear coefficients.
The full source registry, coefficient maps, Boolean correction, and 25
old-Boolean image certificates are saved. Every image fits the original
e+3 ceiling. All four nonzero-weight source assignments and an unweighted
companion failure are retained. This local fixture is not PHP.

The naive equation X_j^2-X_j fails on the saved old Boolean points, while
the correct twisted domain equation holds. The coefficient projection is
explicitly checked to be nonmultiplicative. Its value at one is one;
ordinary trace has value zero at one in even field dimension.

`unital-descent-controls.jsonl` supplies 36 additional certificates:
30 relevant divisor pullbacks, three extension witnesses, and their three
binary projections. In dimensions 2,3,4, a nonbinary Koszul syzygy is added
to a binary cubic target's witness. The extension identity is checked
through degree four, and the chosen unital projection retains the target
through degree three. Ordinary trace loses the target in dimensions 2 and 4.
These controls exercise descent when the witness coefficients are genuinely
outside F2. They do not replace or alter the main degree-three kernel checks.

Together the two retained runs contain 941 ordinary NS certificates:
490 over auxiliary fields and 451 over F2. The main suite was not rerun
when the focused optional mode was added.

## Parameters and checkpoint

Exact parameter cases use M=n^2, D=ell^3, R=floor(v/2), and
H=4*ell+2*ceil(log2(ell))+5 as an upper bound on ln(8*M*v*(v+1)).
All sufficient conditions pass at ell=64 and 128. At ell=40, range,
image, domain, and cube-packing conditions pass, while old-degree room
fails. Full integers are retained; field cardinalities are not instantiated.
These large parameter cases are separate from the small algebra fixtures.

Both compilations and both exact runs passed. `check-metadata.json` records
the focused evidence and touched-link review; `provenance.json` records
code and evidence hashes. Timing and complete command output are archived
under this session name in `research/provenance/session-records/`.

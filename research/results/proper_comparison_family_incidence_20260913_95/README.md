# A wide family of collected proper comparisons

The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-13-proper-comparison-family)
contains the source-compatible construction, collected-coefficient proof,
exact separator bound, and fixed-target block-necessity theorem. The target
is a selector-valued theorem approximation, not the old PHP target one.

For h>=2, r=2h+1, and m>=2, use independent affine child tuples G_i,H_j.
Their products are X_i,Y_j and the union products are Z_ij. The target is

    T_m = sum_(i,j) Z_ij - (sum_i X_i)*(sum_j Y_j).

Summing the actual source OR-union witnesses gives an NS certificate through
6h. A flat OR and an OR of double-negated child ORs express the same Boolean
function. The latter's rank-two block packs to X_i*Y_j within its original
degree budget. A parity combination of these equality theorems realizes T_m
after the stated source preprocessing. Polynomial-size bounded-depth proofs
and the source balancing theorem provide logarithmic proof height.

This is a particular compatible certificate, not a claim that every source
simulation or every PHP proof must retain the same graph.

## Complete factored certificates

<code>family-certificates.jsonl</code> uses h=2,r=5 and m=2,3,6. It references
the already verified local case <code>proper_union_h2</code> in

    research/results/proper_source_subspace_relations_20260913_94/proper-OR-union-checks.jsonl

The preflight check verifies its fifty-variable layout, degree-twelve
certificate, and all twenty axiom/cofactor pairs. The full local polynomials
travel with the repository and are pinned by provenance.

Every global comparison has an injective local-to-global variable map.
Every collected canonical companion coefficient records all its template
summands. Together with the old-coordinate change below, this is a complete
global NS certificate. No coefficient is truncated or left only in scratch;
re-expanding the same local identity for every module would duplicate data.

| m | Retained blocks | Comparison modules | Collected cofactors | Summands | Isolated coefficients |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 2 | 8 | 4 | 60 | 80 | 100 |
| 3 | 15 | 9 | 120 | 180 | 225 |
| 6 | 48 | 36 | 420 | 720 | 900 |

The coefficient of a child companion is

    C_(A_i,a) = -sum_j P_(B_j) * U_(C_ij,a).

Selecting the complete rows of C_ij and B_j kills every other union prefix,
leaving exactly g_(i,a)^(h-1)*h_(j,b)^h. Each projection record lists its
one surviving module, all discarded modules, and the exact old-signal
monomial. The 1,225 projections are checked from the symbolic prefix rules
and canonical registry, using the earlier verified local extraction.
They are not new expansions of 900-variable polynomials.

## Coordinate and polynomial encoding

There are v=2*m*r old variables. Formal signals are

    u_s = sum_(t != s) x_t.

The unsigned 64-bit signal words encode those affine linear forms; read
them with exact integer arithmetic. Since v is even, the matrix I+J is its
own inverse. The checker verifies this, the canonical input ranks, and
absence of literal coordinate directions in every input span.

Each block lists its input-signal indices and coefficient start. Coefficient
variables are indexed after the v old coordinates, in h rows of the listed
arity. In the main cases, child blocks A_i precede B_j and then union blocks.
All coefficient scopes are fresh except intentional canonical sharing.

To reconstruct a template module:

1. For template old variables 0..9, use its variable map to select the global
   signal and then substitute the signal's full affine expression in the old x's.
2. For template coefficient variables 10..49, rename to the indicated global
   coefficient variable directly.
3. Read the named local axiom and cofactor polynomials from the pinned template.
   Sum the indicated renamed cofactors for each canonical companion.

The root is the sum of all renamed local targets. The template is an
ordinary-polynomial identity, so affine substitution and addition prove
the complete certificate with no degree increase. The domain equations
for old signal coordinates map to sums of original Boolean domains through
degree two. The global products and actual inputs are therefore explicit.

## Graph and separator evidence

The comparison graph has edges A_i-C_ij-B_j. Child vertices have weight one,
union vertices weight zero; separator cost counts all removed vertices.
Every remaining component must have at most 4m/3 child weight.
Its minimum separator is ceil(2m/3), proved in the notebook. The supplied
attaining separator is checked in every main case.

All separator subsets were enumerated only for m=2 and m=3, with complete
size histograms retained. At m=6 the minimum four uses the analytic lower
bound and a checked upper witness, not an exhaustive search of 48 vertices.
The minimum block set meeting every comparison triple is m, by disjoint
diagonal triples and the cover consisting of all A_i.

## Semantic block-deletion models

<code>block-deletion-countermodels.jsonl</code> preserves an assignment for
every omitted block in each main case:

| m | Models | Retained companion checks |
| ---: | ---: | ---: |
| 2 | 8 | 420 |
| 3 | 15 | 1,680 |
| 6 | 48 | 19,740 |

All 71 models satisfy every other companion and every Boolean domain, but
give T_m=1. The file records the omitted block, all old x coordinates equal
to one, all coefficient variables equal to one, every block-product value,
and the check counts. Unlisted variables are zero. Products are evaluated
from those assignments, not merely set to their predicted values.

The analytic construction works at every h>=2. For an omitted union block,
make all child tuples nonzero. For an omitted A_i, make all G tuples
nonzero and exactly one H tuple zero; reverse the roles for an omitted B_j.
Retained nonzero tuples select one nonzero input in their first coefficient
row, and all other coefficients are zero. The omitted block uses all-zero
coefficients. The invertible signal map supplies the required old x values.

Thus every block is semantically necessary for deriving this fixed target
from this specified system, at any NS or PC degree. This does not force
the same graph in every possible proof, and it does not apply after adding
extra axioms or changing the target. In particular it is not an old-target
PHP nonderivability result.

## Preprocessing controls

At m=3, if all rank-five tuples share the same span, canonicalization leaves
one product. Every comparison is P-P^2 and uses only domains. Their odd
total multiplicity leaves a nonzero Booleanity target, so the empty
companion-comparison graph is not an even-multiplicity cancellation artifact.
The retained canonical product is not counted as a vertex of an active
comparison graph when all such modules have been removed.

At h=2 with independent child ranks two, both child and union ranks fit
packing. The recorded packing bins give exact complement products, and
every comparison target is then the zero product identity. All active
comparison modules disappear. These controls reuse the proven domain and
packing witnesses; no duplicate expanded control certificate was generated.

## Reproduction

Use fresh output paths from the repository root:

~~~bash
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -std=c++17 -O2 -Wall -Wextra -pedantic \
  research/tools/check_proper_comparison_family.cpp \
  -o /tmp/check_proper_comparison_family
./compute.sh run TURN --threads 1 -- \
  /tmp/check_proper_comparison_family \
  --template research/results/proper_source_subspace_relations_20260913_94/proper-OR-union-checks.jsonl \
  --out NEW_FAMILY.jsonl
./compute.sh run TURN --threads 1 -- \
  /tmp/check_proper_comparison_family \
  --template research/results/proper_source_subspace_relations_20260913_94/proper-OR-union-checks.jsonl \
  --out NEW_MODELS.jsonl --essentiality
~~~

Both compilations, both runs, and the template preflight passed under the
shared resource limits. No dependencies were installed. Orchestration
quoting errors were corrected before any commands ran. Coding time includes
some source-realization and model-construction reasoning; no retrospective
timing split was invented.

The provenance manifest pins the checker, helper, both full outputs, the
local template and its provenance, and this record. Timing and complete
protected command output are archived with the checkpoint.

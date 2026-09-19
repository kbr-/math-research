# Significance audit: five normalizer and Booleanity claims

19 September 2026. This is a completed targeted literature assessment, not an
exhaustive priority search or a new correctness audit. Exact notebook statements,
proof arguments and encoding qualifications were read. Primary-source searches
and the specific passages below were compared. No matching publication of the
five exact formulations was identified in this bounded search; that observation
is not evidence establishing novelty.

## Recommended dispositions

| Claim | Category | Novelty | Publication disposition |
|---|---|---|---|
| `thm:odd-affine-Booleanity-classification` | general_tool | unknown | not_applicable |
| `thm:reduced-product-Booleanity-PC-NS-gap` | general_tool | unknown | not_applicable |
| `thm:PHP-reduced-product-Booleanity-gap` | general_tool | unknown | not_applicable |
| `thm:ternary-coefficient-degree-frontier` | general_tool | unknown | not_applicable |
| `thm:heterogeneous-scalar-profile-frontier` | independent_result | unknown | candidate |

These are editorial significance judgments. They do not change the working-proof
status, assert equivalence to a published theorem, or retract any mathematics.
All five significance reviews can be marked **reviewed**: the targeted comparison
was performed. Unknown novelty is its honest outcome, not an unperformed-audit
placeholder. Only the heterogeneous frontier merits retaining a separate candidate
flag on current evidence; this is prioritization, not a prediction of acceptance.

## Odd-characteristic affine Booleanity

The notebook classifies affine polynomials with `b²-b` in the ordinary degree-two
weak-PHP NS/PC space, modulo row equations, for odd prime characteristic and n≥4.
It excludes same-row functionality as an implicit axiom. The extension variant
requires every nonzero retained companion's original degree above two.

There is a close structural antecedent: Ellis–Friedgut–Pilpel classify Boolean
functions in the first permutation representation space as indicators of disjoint
unions of 1-cosets (Corollary 2). [Primary paper](https://arxiv.org/pdf/1011.3342).
Dafni–Filmus–Lifshitz–Lindzey–Vinyals state the row-or-column dictatorship form and
extend degree-one classification to perfect matchings (Section 6, Theorems 6.1–6.2).
Their framework uses real-valued functions on nonempty permutation/matching domains.
[Author PDF](https://yuvalfilmus.cs.technion.ac.il/Papers/measures.pdf).

Our inference: the partial-column conclusion belongs near that literature, but
those results do not directly imply this odd-field, truncated-certificate statement
on an unsatisfiable weak-PHP presentation. In particular, pointwise Booleanity on
full PHP models would be vacuous. The rectangle coefficient argument is useful
for controlling sharp affine normalizers; independent publication significance is
not established. If publication is later considered, compare the truncated
weak-row ideal criterion explicitly with finite-characteristic degree-one
classification, rather than citing real permutation dictatorship as an identical
result.

## Two exact PC/NS Booleanity-degree examples

The first record fixes a consistent old Boolean domain, odd p, a monomial input
of degree t and one original companion of degree `e=(h+1)t+h`. The consequence is
the Booleanity of the reduced value, with exact NS degree `e+h` and PC degree
`max(e,2(h+t))`. The second preserves these values over full weak PHP under
`n-t≥2(e+h)-3`, using a residual design. Neither is a separation of refutation
size, nor does the first claim a result over arbitrary added equations.

The broad degree separation is old. Buresh-Oppenheim, Pitassi, Clegg and Impagliazzo,
*Homogenization and the Polynomial Calculus*, ICALP 2000, give almost linear
NS-versus-constant-PC refutation-degree separations for explicit 3CNFs; their
Theorem 2 and Corollary 1 relate homogenized PC to NS degree.
[Author PDF, abstract and Section 3](https://www.cs.utoronto.ca/~toni/Papers/homo-icalp.pdf).
The newer pebbling literature also studies exact NS degree and tradeoffs;
[de Rezende et al., ECCC TR20-001](https://eccc.weizmann.ac.il/report/2020/001/)
was screened at its abstract, not used as a matching theorem.

Our inference: the notebook's contribution, if original, is an exact small ENS
consequence example and its PHP-relative preservation, exposing why completed PC
lines cannot be reused as same-degree NS certificates. It is not discovery of
PC/NS degree separation. The original-degree activity condition and a target other
than one distinguish the formulas from the surveyed refutation results. Retain
both as useful proof-accounting tools. An eventual publication comparison should
ask specifically about target-degree examples after reducing an input while
retaining the original companion degree; it should not advertise a new general
separation phenomenon.

## Ternary and heterogeneous coefficient frontiers

The ternary theorem counts coefficient degree in actual independent Boolean
column coordinates and requires all companions to vanish modulo the proper
column/domain ideal. Its exact row count is `ceil(n/(T+1))` in characteristic two
and `ceil(2n/(2T+1))` in odd characteristic. The heterogeneous theorem uses
mutually exclusive state coordinates encoding scalar alphabets of sizes k_j;
it permits h rows exactly when the smallest `max(0,N-hT)` nonzero alphabet sizes
sum to at most h. Additional PHP row equations are explicitly outside the lower
bound. Native scalar coordinates have a different degree cost, already separated
in the notebook.

At T=0 this is the classical finite-grid hyperplane covering problem. Alon–Füredi's
1993 result gives the minimum number of hyperplanes covering a finite product
grid except one point. The sharp one-point polynomial bound and its generalization
are stated in Bishnoi–Clark–Potukuchi–Schmitt, *On Zeros of a Polynomial in a Finite
Grid*, Section 1.2, Theorems 1.1–1.2.
[Primary follow-up with a new proof](https://community.middlebury.edu/~jschmitt/papers/on_zeros_of_a_polynomial_in_a_finite_grid.pdf).
The [original author PDF](https://web.math.princeton.edu/~nalon/PDFS/Publications/Covering%20the%20cube%20by%20affine%20hyperplanes.pdf)
was located and opened, but its scan did not expose text to the browsing tool;
this audit relies on the readable theorem statement in the follow-up.

Our inference: forced grid selectors, interpolation and top-monomial degree
counting are established techniques. The positive-T exact encoded-coefficient
optimization is more specific: the coefficient polynomials use state coordinates,
and the heterogeneous proof counts groups untouched by their occurrences. The
read theorems bound ordinary polynomial degree/support and do not directly state
that constrained factor frontier. No exact matching result was located. This
justifies retaining the heterogeneous theorem as a **candidate with unknown
novelty**, while treating the ternary theorem as a useful special case in the same
family, not a separate candidate. Before promotion, present the precise encoded
model and positive-T optimality criterion to a finite-grid covering expert; ask
whether the occurrence-budget refinement is known under another formulation.

## Search and retrieval boundaries

`sources.json` preserves queries, primary URLs, precise reading scopes and the
comparison verdicts. Broad exploratory searches also returned secondary pages;
they were used only to locate the primary sources cited above. Exact phrase
searches for reduced-product Booleanity and encoded/polynomial-coefficient grid
covers did not identify an exact match. Search terms and absence of matches are
not a completeness certificate. No copyrighted full text was copied into this
artifact, no dependencies were installed, and no paper request is currently needed.

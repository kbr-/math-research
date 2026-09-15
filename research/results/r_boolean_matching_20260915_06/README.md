# Explicit binary cube operator

Completed lem:binary-cube-degree-drop, a reusable prerequisite of R14. Full MathJax statement/proof: entry-2026-09-15-lean-binary-cube-degree-drop. Finite selected groups I, tag:V→Option I, fixed untagged images g_v of degree≤1, tagged scalar images a_v(epsilon_i). cubeDifference is the actual finite sum of ordinary polynomial homomorphisms.

Verified: fixed-point-free flip cancellation; missing-group monomial cancellation; tagged/untagged exponent partition and inside degree≥|I|; total-degree drop by|I|; exact zero below|I| even without a g-degree bound; fixed-factor extraction; NS_B→NS_(B−|I|) and annihilator transport under explicit cube-independent source-generator images in G∪{0}. The last assumption is not claimed proved for the R14 board yet. Actual R13 coefficient isolation remains separate. Empty selected family and zero/constant polynomials are included.

The final version bounds g_v only if tag(v)=none. The earlier audit verification.txt bounded all g_v, including unused ones; this hypothesis was removed before checkpoint, and generalized-verification.txt is the final14-declaration audit. Both complete reports retained. No custom axioms or unfinished proof; only standard foundations. Input/output variable types need not be finite, while I is Fintype.

Initial proof failures concerned update API names, beta reduction, unused instances and inequality tokenization (`≤i` parsed as an initial-segment notation without whitespace). They were repaired and did not expose a mathematical gap. All full command output/timing is canonically archived. No dependencies installed/upgraded and no living notebook sections/route edited. Parent was sent exact progress; R14 remains incomplete. No post-all-Rxx generalization sweep has begun.

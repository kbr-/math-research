# Open problems and benchmarks

Literature navigation for significance assessment, not the project's live status
or a publication-candidate queue. The [notebook](https://kbr.is-a.dev/math-research/)
owns current mathematics; the [claim registry](claims/README.md) owns claim-level
assessments. Follow a benchmark anchor from a claim's significance references when
useful. Absence from this map is not evidence of insignificance or novelty.

**Last source check for every entry below: 19 September 2026.** Initial coverage:
targeted primary-source abstracts and introductions, not a systematic literature
review or re-verification of proofs. “Open in checked literature” is deliberately
weaker than a certified current open-problem verdict. A preprint is not automatically
peer reviewed. Search for newer versions before relying on a novelty assessment.

## Conventions

PHP means the unsatisfiable CNF encoding, or its negation when discussing Frege
tautologies. Unary PHP has variables x(i,j), a clause saying each pigeon chooses
some hole, and pairwise clauses forbidding two pigeons in one hole; same-pigeon
exclusion clauses define a different, functional variant. Bit PHP uses log2(n)
bits per pigeon for n a power of two and the usual collision-forbidding CNF.
Specify the number of pigeons rather than conflating n+1 with weak PHP regimes.

Res(⊕) means DAG-like resolution with linear clauses over F2 unless qualified.
Match inference and weakening rules before transferring a bound. Size below is
node/line count for Res(⊕); a node lower bound also bounds total written size.
Proof-DAG depth is longest inference-path length, not Boolean formula depth in
Frege. Rank width (independent equations) and syntactic clause width are distinct.

| Anchor | Benchmark | Literature classification at this check |
| --- | --- | --- |
| [frege-php](#frege-php) | Ordinary PHP in fixed-depth AC⁰[p]-Frege | Main open target |
| [res-parity-size](#res-parity-size) | Unrestricted Res(⊕) size on an explicit family | Open in checked literature; local candidate linked |
| [res-parity-bit-php](#res-parity-bit-php) | Unrestricted Res(⊕) size for usual bit PHP | Restricted bounds published; local candidate linked |
| [res-parity-unary-php](#res-parity-unary-php) | Unrestricted Res(⊕) size for unary PHP | Separate unresolved target in this map |
| [res-parity-size-width](#res-parity-size-width) | Size versus width and depth | Method benchmark; exact conversion needs audit |
| [ac0-php-baseline](#ac0-php-baseline) | PHP in bounded-depth Frege without MOD gates | Established lower-bound baseline |

## frege-php

**Question.** For every fixed prime p, fixed formula-depth bound d, and constant
K, must sufficiently large ordinary PHP with n+1 pigeons and n holes require
AC⁰[p]-Frege proofs of written size greater than n^K? A polynomial-size upper
bound at some fixed p,d would be a significant alternative outcome for that scope.

**Literature boundary.** The introduction of [Itsykson–Podolskii–Shekhovtsov,
TR26-018](https://eccc.weizmann.ac.il/report/2026/018/download/) still describes
superpolynomial AC⁰[p]-Frege lower bounds as open. [Lu–Santhanam–Tzameret,
ITCS 2026](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ITCS.2026.99)
prove an infinitely-often nonexistence of short proofs for a DNF family whose
tautologicity is unresolved; this is not a PHP lower bound or an explicit hard
tautology family with established tautologicity.

**Local connection / next check.** Read the notebook's
[remaining route](https://kbr.is-a.dev/math-research/#remaining-route) and
[ordinary-to-bit encoding audit](https://kbr.is-a.dev/math-research/#unary-to-bit-Frege-encoding-clarification).
The latter concerns Frege substitution, not affine Res(⊕) queries. Before a novelty
claim, search fixed-prime/fixed-depth results and verify the exact PHP encoding.

## res-parity-size

**Question.** Exhibit an explicit polynomial-size unsatisfiable CNF family F_n
such that every unrestricted DAG-like Res(⊕) refutation has n^{ω(1)} nodes.
No regularity, tree-likeness, width or depth restriction belongs in this endpoint.

**Literature boundary.** [Efremenko–Garlík–Itsykson, SIAM J. Comput. 2025
(STOC 2024 precursor)](https://doi.org/10.1137/24M1696640) describe the unrestricted
problem as open and prove regular lower bounds. [Bhattacharya–Chattopadhyay–Dvořák,
2024](https://arxiv.org/abs/2402.04364) separate their regular system from even
ordinary resolution, so a regular bound cannot simply be read as unrestricted.
[Itsykson–Podolskii–Shekhovtsov, February 2026](https://eccc.weizmann.ac.il/report/2026/018/)
give a pure quadratic lower bound as well as depth-restricted superpolynomial
bounds; quadratic alone does not reach the endpoint above.

**Local connection / next check.** The
[publication theorem](https://kbr.is-a.dev/math-research/#publication-Res-parity-bit-PHP-theorem)
and its [formalization](https://kbr.is-a.dev/math-research/#lean-publication-bit-PHP-superpolynomial)
are local candidates for this benchmark. Consult their current registry assessments
and [publication prerequisites](../publications/bit-php-resolution-over-parities/PUBLICATION_PREREQUISITES.md); this map neither
certifies novelty nor upgrades internal verification to independent review.

## res-parity-bit-php

**Question.** The preceding unrestricted size endpoint for the usual CNF bit PHP
with n+1 pigeons, n=2^ℓ holes, and N=(n+1)ℓ Boolean variables.

**Literature boundary.** [Efremenko–Garlík–Itsykson](https://doi.org/10.1137/24M1696640)
give a regular size bound 2^{Ω(n^{1/3}/log n)} and an unrestricted linear-clause
rank-width lower bound Ω(n). [Byramji–Impagliazzo, TR25-118 revision 1,
25 November 2025](https://eccc.weizmann.ac.il/report/2025/118/) state, for usual
bit PHP, size exp(Ω̃(N^ε)) at proof depth N^{2−ε}. Their weak-PHP regime has
different parameters. Use the revised statement, not only the original abstract.
Neither restriction-free size follows merely by dropping a depth or regularity
hypothesis from these results.

**Local connection / next check.** See the
[bit-PHP publication audit](https://kbr.is-a.dev/math-research/#bit-PHP-prior-size-lower-bounds)
and [supplementary literature audit](https://kbr.is-a.dev/math-research/#publication-additional-regularity-literature).
Before comparison, align CNF axioms, weakening conventions, N versus n, and proof
depth versus formula depth; refresh the candidate's literature audit separately.

## res-parity-unary-php

**Question.** Superpolynomial unrestricted DAG-like Res(⊕) size for the unary
CNF defined above, with n+1 pigeons and n holes; record functional variants separately.

**Literature boundary.** The introduction of
[Efremenko–Garlík–Itsykson, TR23-187](https://eccc.weizmann.ac.il/report/2023/187/download)
reports tree-like unary-PHP lower bounds and cites Itsykson–Sokolov. This check
does not establish a complete best-bound survey for unary DAG proofs; a dedicated
encoding-specific search remains necessary before calling a new bound novel.

**Local connection / next check.** The
[encoding audit](https://kbr.is-a.dev/math-research/#unary-to-bit-Frege-encoding-clarification)
does not preserve affine queries under substitution. A bit-PHP Res(⊕) bound must
not be advertised as a unary-PHP bound without a suitable proof-system reduction.

## res-parity-size-width

**Question to audit.** For a CNF F on N variables, which quantitative relation
between minimum DAG-like Res(⊕) size S(F), minimum rank width W(F), and initial
width w₀(F) is valid? Specify the width convention and rule set. A candidate
conversion must turn the known bit-PHP width bound into a superpolynomial size
bound if that is its intended application; width hardness alone is insufficient.
This is a method benchmark, not an assertion that a particular classical
resolution size–width formula remains open or holds unchanged for Res(⊕).

**Literature boundary.** [Chattopadhyay–Dvořák, CCC 2025](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.CCC.2025.24)
establish supercritical width–size tradeoffs for **tree-like** Res(⊕).
[Itsykson–Knop, ITCS 2026](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ITCS.2026.81)
give size–depth tradeoffs even for formulas with quasipolynomial resolution proofs.
[TR26-018](https://eccc.weizmann.ac.il/report/2026/018/) lifts ordinary resolution
width w through a 1-stifling gadget to depth Ω(w²/log S) for Res(⊕) proofs of size
at most S. These are different assertions from an unrestricted same-formula
rank-width-to-size theorem.

**Local connection / next check.** Start with the
[additional literature audit](https://kbr.is-a.dev/math-research/#publication-additional-regularity-literature).
Before using any proposed conversion, read its full theorem and test its exact
hypotheses against these separations. No new conversion is claimed here.

## ac0-php-baseline

**Established comparison.** Ordinary PHP has exponential lower bounds in Frege
at each fixed formula depth without MOD gates. [Krajíček–Pudlák–Woods,
TR94-018](https://eccc.weizmann.ac.il/report/1994/018/) and the
[Ben-Sasson–Harsha presentation, TR03-004](https://eccc.weizmann.ac.il/report/2003/004/download)
are entry points; the latter states a bound exp(n^δ) with positive δ depending
on fixed depth/system. This is a baseline, not a new open problem. The
[main route](https://kbr.is-a.dev/math-research/#remaining-route) must handle MODp
gates; a new proof for the no-MOD subsystem alone does not close that gap.

## Maintenance

During significance review, consult only the relevant entries. Match system,
encoding, parameter and restriction first; then follow primary sources and search
for updates if the candidate warrants a novelty audit. Record source version,
date, scope read and unresolved comparison here when changing an entry. Keep
proofs and new mathematical deductions in dated notebook entries with claim
metadata. Keep candidate decisions in registry significance metadata (and the
planned shared attention register), not a second queue here. Fossick should link
these stable benchmark anchors rather than copy their literature summaries.

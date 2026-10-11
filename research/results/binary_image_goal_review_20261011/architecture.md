# Final architecture and source tests for staged review

Review title: Rank-residual order leaves circuit hardness open.
Status: working exact order and binary scalar-oracle obstruction; goal unchanged.
All three Open statements remain open, none has dropped since the review >10
research entries back. This is scheduled after six research entries.

Necessary target: for each fixed d a family F_d of encoding N independent of A,
requiring more than N^A symbols for every fixed A eventually. A proof-local
surviving W with actual leaf/copy/MP errors zero through degW+2L<=D suffices
by cor:proof-observation-rank. Alternatively all relevant depth-O(d) binary
formal IPS circuits must be superpolynomial, using imp:depth-preserving-IPS-
simulation and imp:binary-algebraic-CNF-IPS-transfer at their exact scope.
The latter overhead is polynomial for each fixed depth; no numerical exponent
is needed to preserve the forall-polynomial-exponents goal. It would be needed
for transferring the current limited fixed exponent bound. No change to that
bound is claimed.

Extra requirements: universal source templates, a common input target,
canonical coefficients, deep coefficients in I^r, and a determinant extraction
from every certificate are NOT necessary endpoints. The reviewer proposed
deep-coefficient construction as a test; retain it only as one attempted
construction, not a hardness premise. All complete Boolean corrections remain.

Independent stage: blind reviewer found no complete architecture; its IPS
suggestion coincides with the revealed alternative. Full certificate
nonuniqueness remains. New draft's rank-order result is not goal progress.
No registered conjecture is used as proved: all three stable Open statements,
source coverage, and full residual hardness are open; no new route conjecture
is promoted here.

Rank normalization: new result is local order, not a dimension ratio, so it
must not replace the actual-error numerator/denominator in the old quotient.
No proper global algebra of satisfying assignments is assumed. I here is the
Boolean ideal in the ordinary polynomial ring, not the charged PC pseudoideal.

Decision: reject treating raw multiplicity, a single leading jet or a scalar
black-box extraction as a lower-bound mechanism. Return to the existing
rank-family item's full-certificate task, with any small correction tuple allowed.
A direct small-certificate construction could disqualify this family for the
stronger IPS route; a lower bound must cover the whole tuple class. Compare
this against source method repair (still missing compiler coverage) and the
bounded-feature candidate change (explicitly easy): the rank family escapes
that structural upper bound, has a fixed polynomial encoding, and has a
nontrivial fixed residual, but no circuit hardness is established.

Concrete next test: at m=2n, construct or obstruct a shared Boolean row-elimination
recurrence for the entire tuple Q in P=sum_x b_x q_x, over F2 and with all
Boolean coefficients retained. Start from A_11=1 versus A_11=0 and derive
the exact cofactor gluing identity. Move a selected nonzero pivot to position
(1,1) by recorded row/column permutations; share subproblems only when their
displayed input/coefficient expressions are then literally identical. Any
stronger algebraic sharing must be separately proved and costed. Track these
distinct subproblems and depth before attempting larger instances.
The target is polynomial total circuit size and a depth bounded independently
of n. Deep coefficients q_x in I^n are an optional organization only.
A small constant-depth full certificate excludes this IPS candidate; an
unconditional lower bound for all such Q would give the desired route.
An exponential branching/depth cost in this particular recurrence ends that
construction, not all certificates. Do not report a generic recurrence,
multiplicity estimate, or failure to find coefficients as progress.

Trivial cases: duplicate equations may replace P by P^2, doubling its ideal
order without strengthening the unsatisfiable system. Existing explicit
Frobenius certificates K_P(B)=P^2+P transport Q<->Q+K_P at polynomial size and
constant extra depth; this is an immediate specialization of the last cycle's
proved field-defect construction, and is an existing cheap residual transport.
Hence numerical ideal order is not a semantic hardness invariant. Constant
contradictions and fixed n have tiny certificates and are not the test family.
Row/column permutations must be handled as equivalent presentations.
Power: known PC degree Omega(n) does not exclude constant-depth circuits
with high degree; single-point initial forms are small, and zero-factor slice
extraction is defeated by cheap syzygies. No finite enumeration is planned.

Outside leads:
1. Chinese remainder theorem for comaximal powers (Stacks 00DT). Translation:
the nonreduced Boolean scheme I^q records all local jets. Answers: a proved
size-sensitive restriction on complete residual decompositions in that module
could resolve binary-frege-lower-bound. Test PASSED as an object construction:
exact q=m-n+1, with all-point and syzygy controls in draft.md. No automatic
circuit lower bound. Pick this continuation but merge into existing
entry-2026-10-09-rank-certificate-slice:s1 (parent rank-principle lead), since
it is the same full-certificate question with a new concrete object.
2. Determinantal-ideal closure: Dey-Guo ITCS2026 Theorem6 and its statement of
Andrews-Forbes Theorem1.1. The former requires char0 or char>deg f and a
sufficiently large field. Answers: a matched closure could turn a certificate-
derived ideal element into a known hard determinant. Test FALSIFIED for direct
binary application: hypotheses fail, and oracle-draft.md proves the stronger
fixed-F2 counterexample. Also H(X)=prod_i X_ii prod_(i!=j)(1+X_ij) is not in
the rank<=n determinantal ideal: X=t J_m has rank1<=n but H=t^m(1+t)^(m(m-1))
is formally nonzero. No impossibility of large-field variants is claimed.
3. Multiplicity Schwartz-Zippel (Bhandari-Harsha-Kumar-Shankar Lemma3.5,
attributing DKSS). Answers: a degree-to-certificate-complexity theorem might
turn high local order into a lower bound. Test FALSIFIED for degree alone:
on the binary cube it yields degP>=2q; here degP=2m^2, so the bound is
compatible with the existing small circuit. The control (x^2+x)^q has order
q everywhere and size O(q), depth two. No full multiplicity-code decoding
theorem is imported.

Absurd bridges:
1. Knill-Laflamme Theorem3.2. Translate error operators into channels on a
surviving subspace. Answers: a degree-paid theorem forcing simultaneous zero
errors could construct the missing W. Test FALSIFIED for recovery=>annihilation:
the identity channel is perfectly correctable on every code but its kernel is
zero. This fails already over C, before the separate F2/positivity mismatch.
It does not rule out a more specific error-algebra construction.
2. Green-Karvounarakis-Tannen provenance, Proposition3.5/Theorem4.3. Translate
shared derivations to symbolic semiring provenance and evaluate into F2.
Answers: a field-faithful compression bound might control the actual error
map while retaining sharing. Test FALSIFIED for witness-count/support preserving
nonzero field output: 2x is nonzero provenance over N[x] but zero over F2.
Keeping the full mod2 polynomial avoids that loss but supplies no new
complexity bound; no broad provenance impossibility is claimed.

Only the first Outside lead passes; no bridge passes. No new standalone queue
item is needed: merge the picked duplicate into the existing rank-certificate
child. The deferred coefficient construction remains at the destination.
No existing broad item is closed. Queue stays24, not draining.

Source-reading limits: Stacks CRT statement; powered-ideal argument reproved here. Dey-Guo Theorems4/6
statements and Section4 field restriction discussion, not full proof; Lemma3.5
and multiplicity definitions in the cited multiplicity paper, not its decoding
algorithm; Knill-Laflamme Theorem3.2 statement/nearby code definition, not full
paper; provenance Proposition3.5/Theorem4.3 statements and semiring definitions.
All five tests are explicit symbolic controls, not unrun computations.
The original Andrews-Forbes PDF and NSF link returned tool errors; its
large-field statement is read through Dey-Guo, not claimed as a new original
proof audit.

Reviewer suggestion disposition: deep coefficients can be an optional upper-bound
construction, but restricting the LOWER-bound target to them would strengthen
the necessary endpoint unjustifiably. Verify the actual application in
oracle-application.md too (one-line differentiation using rank-order>=2).
Please check the complete architecture, test specificity, five controls,
merge-only closure and process findings, without recertifying outside papers.


# Axiom-cut normalization

Question: can the matched Frege-to-IPS image retain a protected unit-slice
coefficient, even though general IPS permits cheap syzygies? This tests queued
entry-2026-10-09-core-scope-review:s3, under the rank parent and
binary-frege-lower-bound. Goal unchanged if the obstruction is removable.
Scope of novelty: elementary refinement/application of the recorded
unit-slice lemma, not an independently new circuit lower bound.

Lemma (axiom cut normalization).
For any field, full generator tuple F, and IPS certificate C(x,Y) with
C(x,0)=0, C(x,F)=1, choose a generator F0. Put
D=(1-F0)C+Y0.
Then D is an IPS certificate, and D=Y0 modulo the ideal (1-F0).
It follows that rho D=Y0 for ANY polynomial substitution rho with rho F0=1,
fixing placeholders; no retraction assumption is needed.
If C is Hilbert-like, so is D, with every Boolean cofactor included.
A shared circuit of size S/depth d for C and size s0/depth delta0 for F0
gives size O(S+s0+1), depth <=max(d,delta0+1)+2.
If Hilbert-like coefficients have degree <=L and degF0<=g, new coefficients
have degree <=L+g (using max(L+g,0) for the constant coefficient).
This refines the recorded unit-slice existence and bounds where it applies.

Proof: D(x,0)=0, D(x,F)=(1-F0)*1+F0=1, and D-Y0 is visibly a multiple
of 1-F0. For Hilbert-like C=sum c_iY_i, coefficient i!=0 becomes
(1-F0)c_i and coefficient 0 becomes (1-F0)c_0+1.
The difference from C is the explicit Koszul sum
sum_(i>0)c_i(F_iY0-F0Y_i), since sum c_iFi=1.
This uses c_i themselves, not separately extracted or restricted coefficients.
The actual circuit is the constant-operation D above. No factorization.

Matched binary simulation:
Fix the specific GP sequent-to-Hilbert-like construction, with t(A) zero
when A is true. Let pi be a tree-like refutation with compiled certificate C,
and let A0 be an original input formula, with generator F0=t(A0).
Append LEFT weakening at the final empty sequent, obtaining A0 -> empty.
Apply the first negation rule to get -> not A0.
Use a fresh input leaf -> A0 and cut them to obtain the empty sequent.
No earlier proof is copied. The appended proof stays tree-like and has
three extra inference nodes and one fresh input leaf; symbol overhead
O(|A0|+1), formula depth <=max(d,depth(not A0)).
The source's actual local translations are:
left weakening multiplies C by t(not A0)=1-F0;
negation changes nothing;
cut concatenates coefficient-term lists, i.e. adds;
the new input leaf gives Y0.
Hence the polynomial compiled by THIS proof is exactly D. Its displayed
output circuit can be flattened as in the source; the conservative circuit
bounds above already suffice. Thus the same unit-slice erasure exists inside
the matched image, not merely in an enlarged IPS class.
It is not claimed that every general syzygy is in that image.

Binary rank inputs:
Take A0 to assert the parity of (A_il AND B_lk), l<=n, equals delta_ik.
Explicitly, A0 is the odd-XOR formula when delta_ik=1 and its negation
when delta_ik=0.
With standard odd XOR, t(XOR_r)=1+r+sum t(arguments) over F2,
t(AND(x,y))=1+xy. Thus t(A0)=delta_ik+sum_l A_il B_lk exactly.
Input formulas have constant depth and total size O(m^2 n).
The source proof's input case is just an input placeholder; its rest does
not require clause width. Thus its same construction applies to these
bounded-depth input formulas (this explicit extension is not mislabeled
the source's stated 3CNF premise). No 3CNF conversion or gate-variable
elimination is asserted here.
Choose j=n+1 and F0=F_jj. The preceding matrix restriction has rho_xF0=1,
so every compiled C has another compiled certificate D with rho_xD=Y_jj.
Under direct residual normalization using the prior explicit K_F, the
previous rho probe equals the small mask R. The determinant obstruction
cannot be restored by insisting only on membership in this simulation image.
This removes a proposed distinction; it proves no shallow rank refutation.

Source check:
Read GP April 14 2014, Theorem2.3 and complete proof pp23-25.
The printed parity translation on p24 is r-sum t(A_i), whereas its
zero-if-true convention and axiom ->not XOR() require the extra constant 1
for standard odd XOR. The empty gate is an exact counterexample to the
printed constant. Corrected formula 1+r+sum t gives the printed abstract
parity recurrence t(XOR(A,rest))=1+t(A)+t(XOR(rest)); the local parity
sums still work, and no depth/size claim is changed. Our new proof
appendage uses only weakening, negation, cut and an input leaf.
Do not call this a disproof of the published simulation theorem.

Nonvacuity and checks planned before coding:
F0=x, F1=1-x, C=Y0+Y1 give nonempty unsatisfiable input and D;
unused variables give arbitrary ambient counts. The actual proof skeleton
uses the contradictory input clauses x, not x and one cut.
The local checker tests four Boolean value pairs for the cut, generic
normalization identities symbolically over F2, the 31 input assignments to
XOR gates of arities 0..4, and six symbolic rank-input encodings (n=1..3,
delta=0,1). These finite rules have universal algebraic proofs above;
no size extrapolation or rank-residual expansion is required.
Negative controls use the wrong weakening multiplier and the printed
empty-parity constant, each required to fail. Small n=1 matrix inputs are
nonvacuous; parity arity zero intentionally tests the source's base case.
No expensive matrix computation or new mathematical kernel is needed.

Degeneracies: F0=1 makes D=Y0 directly; F0=0 leaves D=C+Y0, a valid
certificate since its generator is zero, but no rhoF0=1 exists. Without a
certificate the lemma constructs none. A repeated input may be chosen by its
own placeholder. The statement controls one chosen slice, not simultaneous
normalization to two different placeholders on overlapping slices.

Next: the child is resolved for the relevant unit-slice property (not exact
equality to the old restricted-coefficient patch). General simulation-image
constraints might still help, but this one does not. Parent remains open.
The rank item now has two consecutive cycles with no goal-parameter bearing,
so next develop the different intrinsic-shadow item. Its two developments
(nonlinear-shadow and outside-basis) were read in full. Test the independent
outside-coordinate plus nonlinear-offset class by replacing the whole-function
graph bound sum 2^s with the actual degree-filtered graph-restriction rank in
cor:graph-input-common-target (exact proof read). Compare the resulting rank
with dim[wU] in the same charged quotient, and retain its map degree
T=max(1,delta(k-1)) and replay b+k+TB. The decisive question is whether this
gives a common surviving weight at the goal's polynomial inventory, rather
than only a smaller numerator without a usable denominator. Start with the
recorded one-indicator-per-edge caution: partner indicators remain in the
graph domain. A qualifying bound or a proved failure of this dimension
comparison ends the test; no new full-cell basis or separate one-block repairs.

Completed exact checker: run 3d77c690a0, Singular, 219 checks, all31 XOR
assignments and168 rank-input assignments, six formal rank identities,
two negative controls, zero failures. Full check.txt retained. No larger
run is needed: the general proof is algebraic, not an extrapolation.


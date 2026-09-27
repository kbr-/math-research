# Native medium correctness reviews — 27 September 2026

These are verdicts from two native reviewers that started in fresh contexts; related continuations are identified below. The verdicts are recorded verbatim except for Markdown heading layout.
Both reviewers were explicitly spawned with reasoning_effort: medium and fork_turns: none.
No external Codex process was used for these reviews, and no computations were rerun.

## residual_source_correctness — uniform resolutions and bounded residual source

Pass, conditional on the stated normalized-quotient exact sequence. No mathematical gaps or unused hypotheses found.

- Both Koszul resolutions are exact and minimal over \(S\). The \(N=5\) trace equation, graded finiteness argument, Hilbert-series proof of freeness, and recurrence proof of minimality are valid.
- The polynomial cover construction, coefficientwise bound, generator count \((N-3)(3N-10)\), and weight range \(2N-1\) through \(4N-6\) check out.
- The Tor support inequalities and marked-core argument give the claimed monic bound.
- The quintic control correctly forces \(\max\operatorname{supp}\beta_1(T)=18\).
- The \(S/S_+^r\) warning is valid, including compatibility with the coefficient connection.

Minor wording improvement: replace “first-syzygy weights of the bounded residual source” with “first-syzygy weights of \(K_2\).” The constructed source itself is free.

Read all supplied draft and dependency excerpts; performed no edits or computations.

## extraction_image_correctness — extraction and normalized quotient

**Pass on all five claims**, taking the supplied reviewed dependencies as proved. No mathematical correction or additional hypothesis is required.

- **Conormal obstruction — pass.** The four displayed EPD images generate \(I\) as a \(P\)-ideal. For an order-one operator with \(IM=0\), the derivation-plus-multiplication formula makes its restriction to \(I\) \(P\)-linear. Thus annihilating \(\mathcal L(J)\) forces that restriction to vanish.

- **Global polynomial extraction — pass.** The retained script and certificate match the stated operator, Taylor-factor conventions, marked value, and coordinate restoration. The source cutoff is complete: multiplier order at least four yields base output order at least four, and coefficient-variation output order at least two. Coefficient-dependent multiplier terms vanish because both the value and \(x\)-derivative of \(\mathcal L(gv)\) vanish for either local generator. Frozen coefficients are used consistently. The identities \(h(b,c)=h_x(b,c)=0\) establish \(S\)-linearity, and polynomial identities on the integral parameter ring extend annihilation across every excluded collision. The shift \(D_{32}(N-6)\) and value \(20dq^2\) are correct.

- **Quintic consequence — pass.** The supplied filtration gives \(\Theta(T)=0\). The degree-eight class maps to a nonzero constant generator of the unshifted quotient. Cancellation using the coefficient-image elements \(z^2,z^3\) correctly upgrades the induced \(S\)-linear map to \(k[z]\)-linearity. Hence the kernel is exactly \(T\), and the image is \(z^7k[z]\).

- **Pair-ideal reduction — pass.** The product-rule matrix is correct. Under \(P\oplus yP=S[x,y]\), it is precisely \(-\tfrac12+(y-x)\partial_x\), with eigenvalues \(-(r+\tfrac12)\). Its polynomial \(S\)-linear inverse preserves weight. This proves \(I=J+\mathcal L(J)\) without assuming independence of the two quotient generators or ideal structure for \(\mathcal L(J)\).

- **Normalized quotient and residual dimension layer — pass.** Both product formulas are correct, including all coefficient-derivative terms for \(a_N\). The second Euler operator has eigenvalues \(1+2r/5\). Using both pair-ideal generators therefore gives the actual image \(F D_{32}\), rather than its ideal closure. Division by the nonzero polynomial \(F\) is globally defined and \(S\)-linear, yielding the stated surjection and shift \(-N-3\). Reviewed support and generic length one imply \(\dim K_2\le N-5\); the domain-annihilator argument proves maximality among submodules of that dimension.

I read the specified drafts, dependency excerpts, support verdict, driver, and retained certificate. No computations were rerun. No unused substantive hypotheses were found.

## residual_source_correctness — continuation on the same graded Tor line

Pass. No correctness gaps or unused hypotheses found.

- The explicit upper-layer resolutions give second-Tor maxima \(15\) and \(18\). Thus \(\operatorname{Tor}_2(C/T,k)_{>18}=0\).
- The retained complete resolution places all seventeen actual second-Tor classes of \(C\) in degrees \(19\)–\(23\). The quotient map therefore kills them all, and \(\operatorname{Tor}_2(T,k)\to\operatorname{Tor}_2(C,k)\) is surjective.
- Finite-length sheaf vanishing, connection stability of \(T\), and the shift by \(9\) are correct. The text appropriately excludes the separate monic-generator term and does not treat \(C/T\) as another cyclic marked defect.
- All five algebraic lead/bridge tests pass their stated scope: the Tor test, module-level primary-decomposition applicability, Fischer commutators and failed descent, reaction-ideal closure erasing the surviving class, and the two-dimensional erasure-channel obstruction.

The reaction and quantum conclusions concern precisely the specified translations; neither overclaims a general obstruction. No source theorem is promoted to a cube theorem. No edits or computations performed.

## Coordinator disposition

The wording clarification was incorporated. The normalized-quotient dependency passed the second review, closing the first verdict's explicit condition. All reviewed claims are promoted through a new dated notebook verification-closure record; their earlier provisional entries remain unchanged.

## residual_source_correctness — focused rank-budget strengthening

Pass. The strengthening follows from the existing hypotheses, conditional on the normalized-quotient dependency used in the upper bound.

Over \(L=\operatorname{Frac}(S)\), torsion of \(C\) gives \(L\mathscr A_0v=F_L\). The derivation extends to \(L\). If the first dependence has highest iterate \(D^dv\), dividing by its nonzero leading coefficient gives a **rational** monic relation; differentiation makes the span of \(v,\ldots,D^{d-1}v\) stable. Minimality gives independence, so \(d=\operatorname{rank}F\). Therefore
\[
U_{\rm original}\ge 2N-1+\binom{N-2}{2}=\binom N2+2.
\]

The difference from \(4N-5\) is correctly
\[
\frac{(N-7)(N-2)}2>0\qquad(N\ge8).
\]
Consequently the reviewed upper bound forces
\[
B\ge\binom N2+1.
\]

Specify “rational monic relation of order \(d\)” rather than “any dependence among the first \(j\) iterates gives order \(j\).” No other correction needed. This rules out a uniform \(O(N)\) bound for these first-syzygy weights.

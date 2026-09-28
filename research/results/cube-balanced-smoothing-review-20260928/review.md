# Correctness review: balanced simultaneous smoothing

Verdict: the four results pass this focused review. No mathematical gap or
unused substantive hypothesis was found. The generic six-label proposition is
a computer-assisted symbolic result over F3(b,c,d), not an inference from the
earlier finite-field sample. No larger-dimensional normality follows or is
claimed. No computation was rerun: inspection identified no concrete reason
to repeat the retained exact runs.

Reviewed the supplied review draft, the preceding balanced-cluster dependency
draft, both current computation scripts, the generic saturation trace and
basis, and the endpoint certificate. The preceding draft's simultaneous result
was used only in its finite-specialization scope, as instructed.

## Checks

- DVR observation: saturation gives a finite free direct summand in the stated
  finite coefficient module. Its unit maximal minor makes the minimum valuation
  exactly ord(det H), and determinant multiplicativity proves (OV), including
  infinite observation order. The two-function specialization control has
  function valuations zero and one respectively and proves the stated failure
  of commuting saturation with specialization.
- Residue-balanced minors: the integer binomial Vandermonde identity is valid
  after a common Laurent shift, whose jet action is invertible. At every p-power
  the collision count has the same independent minimum as the consecutive
  exponent set. The valuation difference is a sum of nonnegative integers, so
  zero is equivalent to balance at every level, for every prime. Cauchy–Binet
  retains all surviving terms; the cancellation warning is necessary and present.
- Generic mixed lattice: the coefficient generator is the expansion of the two
  square-root factors after removing x. At smoothing order m <= 12, multiplication
  by y^12 puts every exponent between zero and 24, so the saved columns include
  the complete coefficient, rather than a Laurent truncation that could hide a
  pole. Every row transformation is checked invertible. Each divided row has
  zero complete residue; eight divisions leave precision four. The saved ranks
  give 8+6+4+4+4+2+2+1 = 31. A final independent reduction supplies the finite
  unit minor needed to prove saturation in the full formal coefficient space.
- Internal blocks: the preceding three-label determinant is homogeneous of
  degree nine in the slopes and nonzero. Its two normalized blocks share the
  exact rows 1,T and reduce to the stated eight distinct even monomials. Thus
  their costs add to eighteen. Independence of the final even and odd reductions
  justifies adding this to thirty-one; there is no extra cross-block saturation.
- Endpoint extraction: the script checks both support bounds, the middle rank
  seven, and the normalized endpoint rowspace, not just its determinant. Restoring
  x*y^-12 maps polynomial indices 7,8,16,17 exactly to -9,-7,9,11. The retained
  completion marker and equality checks support (GL) and (EP).
- Ambient kernel: both displayed sections vanish to order eighteen. After
  deleting the two indicated columns, the shifted exponent set is 3,...,18,20;
  its residue counts are balanced modulo three and nine and distinct modulo
  twenty-seven. The minor lemma proves rank seventeen and hence kernel dimension
  two. Their endpoint vectors and the endpoint plane give determinant
  -sB*sC*(DeltaB^2*sB^3 + DeltaC^2*sC^3). The degree-seven b term has coefficient
  one, so the determinant is nonzero over the stated generic field. The observation
  valuation is consequently 31+18=49. T=x^2-1 is unramified at x=1, so changing
  between the original marked jets and these jets does not change the conclusion.
- Ternary block: h has units digit two and all higher digits one. For allowed e,
  subtraction h-e has no borrow, and multiplication by each Frobenius factor
  keeps every surviving exponent digitwise below h. The resulting transformation
  is triangular with diagonal one. Splitting digits covers all exponents below q;
  h+(h-1) and h+h cover q and q+1. Finally (1+bT)^h is the unique square root
  modulo T^q with constant coefficient one, since 2h=q+1. Generic generalized
  Vandermonde independence and the product span prove the first-q-jet assertion.
  Independent root characters justify dimension M^2. The nine-jet failing control
  at q=3 correctly prevents extending this to dimension-length normality.

## Scope and presentation

The Outside leads and Absurd bridges use the explicitly proved algebraic
translations and do not import an unread theorem. The Schur residual example is
exact. The text keeps smoothing valuation separate from original polynomial
degree, preserves the sequential failing control, and does not infer generic
saturation from a successful specialization. No mathematical correction is
required.

Two small clarifications would improve standalone readability without changing
any claim:

- Restate the original seventeen rows in the generic proposition: 1,T and the
  fifteen pair products, with w_i^2=1+a_i*T and w_i(0)=1. At present this setup is
  inherited from the preceding entry.
- In the third Outside lead, replace “the sequential witness ... satisfy the
  criterion” with wording that explicitly says the criterion detects the
  sequential failure and the generic coupled success. This avoids suggesting that
  the sequential limit is normal.

The generic hypotheses are used: denominators and endpoint normalization need
parameter-field units. The proof correctly declines to classify special slopes.
The finite support hypothesis in the Laurent-minor lemma and the integrality
hypothesis in (OV) are also used. No hypothesis should be removed.

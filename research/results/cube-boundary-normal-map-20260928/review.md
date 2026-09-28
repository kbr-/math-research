# Focused review: rectangular cyclic normal map

Verdict: mathematical arguments pass. Two minor statement clarifications are
listed below; neither changes a mathematical conclusion. Reviewed without
numerical computations or additional agents.

Read the root AGENTS.md and COMPUTATION_RULES.md, the draft
`/tmp/bmd-normal-map-entry.html`, the appended
`entry-2026-09-28-cube-boundary-normal-map`, the exact earlier
`cube-boundary-deformation-pairing` excerpt, and the supplied boundary-radical
and invariant-prefix drafts. The last two were read for the application scope,
not independently re-reviewed in full.

## Criterion and transport

At a height-two prime, the localized polynomial ring is regular local of
dimension two. In characteristic zero its conormal space injects into the
ambient differential space. At rank r-1, a unit minor splits off an identity
block and leaves one row (a,b). Differentiating changing frames contributes
terms killed by restriction to the right kernel and projection to the
cokernel. Thus the stated rank-two normal map is precisely independence of
the classes of a,b in the conormal space; Nakayama gives the equivalence.
The right kernel has dimension two and the cokernel dimension one.

At rank at most r-2, all cofactors vanish in the residue field, so all maximal
minor differentials vanish. Injectivity of the conormal map forces their
classes into the square of the maximal ideal. They cannot generate that
ideal. Thus generic corank one is genuinely necessary, not an omitted
convenience. Unmixedness then makes generic reducedness equivalent to
radicality as stated.

For undivided iterates, delta(v_i)=v_(i+1)-C v_i. After the left-kernel
pairing, only the final shifted column remains, giving exactly
ell(v_(r+1)) times the two final right-kernel coordinates. No factorial or
order factor belongs in this formula. The older square coefficient formula
has a different normalization, explicitly accounting for its order factor.

## Counterexample

Direct symbolic expansion gives the three minors
2x^2+y^6, 6y^5, and 12y^4-12xy. Their ideal is exactly
(x^2,y^5,xy-y^4). For lexicographic x>y, the leading monomials are
x^2,y^5,xy; their S-polynomials reduce to zero (the potentially nonzero
remainders reduce through xy-y^4 and y^5). Hence the six standard monomials
1,y,y^2,y^3,y^4,x are a basis, proving length six and nonreducedness.
Its radical is (x,y), where the three columns vanish. The gcd calculation
with 6y^5 is correct, and proves squarefreeness; the displayed algebraic
closure factorization also checks.

The pivot in f''' is the unit 6. The stated row subtraction leaves
-2xy-3y^4, 2x-8y^3, -12y^2, whose ideal is (x,y^2).
The determinant of f''',f'''' is 144, so the full image is the whole target.

For h=r-2, the first h rows in the first h columns form a unit triangular
block with polynomial inverse, while all later upper entries vanish.
The last two components differentiate h times to exactly f. Block
elimination therefore preserves every later lower column. The square
determinant is the rank-two determinant; boundary maximal minors generate
the same ideal; the next cokernel is the same quotient. The full minor
using columns 0 through h-1 and h+3,h+4 has determinant 144. The boundary
rank at (x,y) is h. This proves the assertions for every r>=2, including
the empty upper block when r=2.

## Scope and precision

- The sentence that the formulas are independent of normalization should
  say that the intrinsic normal map and its rank/vanishing are independent
  of the choices. The coordinate vectors themselves scale or change basis.
- Global properness and height two of J are not used by the pointwise
  equivalence once a height-two P containing J is fixed. Drop them from that
  local statement, or explicitly retain them as the intended boundary
  setting for the global radicality consequence. No other unnecessary
  hypothesis requires action. Characteristic zero supports the conormal
  argument and the all-rank factorial construction.
- The example is expressly outside the cube's positive-degree connection
  setting. It only refutes the abstract shortcut with its listed hypotheses.
  It neither settles the uniform cube normal rank nor the weaker original
  cohomology-degree bound. This limitation is accurately stated.
- Literature is only reported as an abstract-scope search and is not a
  theorem dependency of either proof; this review does not certify those
  external source descriptions.

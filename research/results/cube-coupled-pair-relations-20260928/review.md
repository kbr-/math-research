# Focused review: finite-field branch defects

Reviewed the stable draft `/tmp/bmd-finite-field-defect-entry.html` against the complete supplied exact pair-algebra and curve-transport dependency excerpts. This was an algebraic review; no numerical run was needed or performed.

**Verdict:** The digit identities, transported relations, rank bound, exact complete-field count, and bounded-replacement obstruction are correct. No substantive mathematical gap found. Make the minor scope clarification below before assigning final status.

## Scope clarification

- State `2 <= N <= q` in the finite-field theorem. The supplied original pair-algebra lemma assumes `N >= 2`, as does the original degree-two root-space interpretation using at least one nonzero label. The current theorem does not explicitly exclude the singleton dummy set. Its displayed rank inequality would still be harmless there if its separately displayed span were adopted as a definition, but invoking the original degree-two interpretation and its dependency should preserve that hypothesis.

## Checks

- For `q = 3^e`, splitting `r = 3m+t` gives the digit factorization without carries. At `t=1,2`, the restriction `r <= q-3` guarantees `m+1 < q/3`; at `t=0` the final allowed position causes no carry term. The factor is exactly `h_a^q`, including `e=1`, where only `r=0` occurs. Polynomial cancellation is legitimate in the integral polynomial ring.
- The adjacent identity `Q_(9k+1) = s Q_(9k)` follows from the exact coupled formula with `m=3k`; it is not an unjustified inverse-prefix substitution.
- For retained labels, `alpha_i^q = alpha_i/(1+c alpha_i)` follows from `a_i^q=a_i`. The denominator is nonzero at every stated unramified point. The transformed pair formulas and the displayed five-term pair identity have the correct characteristic-three signs.
- Multiplication by `h_(3j)^q Q_r` produces exactly the five stated indices and scalar coefficients. Since `q` is divisible by nine and `r <= q-9`, both required offsets lie inside the valid digit block. Different `j` use disjoint length-`3q` intervals; different `k` use disjoint offset pairs within each of the three subintervals. The leading coefficient is always one, so independence survives `c=0`.
- After the first two jet pivots, the original matrix is equivalent in rank to the pair-evaluation matrix with nonzero row scalars. Scaling roots and translating the local base parameter preserve the original degree-two source and the complete finite jet rank. Relations are scalar relations on the jet columns at each fixed point, not relations with pair-dependent algebra coefficients.
- For `N=q`, there are `(q-3)/6` complete length-`3q` blocks, each supplying `q/9` relations. The remaining `q` positions supply none among the specified relations. This gives exactly `q(q-3)/54` for the defined count, including `q=9`. This is an exact count of the constructed relations, not a claim that the true rank deficit equals it.
- Replacing at most `k_0` nonzero labels affects at most `binom(q,2)-binom(q-k_0,2)` pair rows. The original disjoint-support coefficient vectors remain independent and annihilate all retained-pair rows. Restricting their span to the affected rows can reduce its kernel dimension by at most that row count. The claimed bound therefore requires no genericity of replacements or independence of constraints.
- At `T=0`, `Q_q=s^q=s=Q_1` on finite-field pairs, including `q=3`. The condition `R>q` correctly ensures both columns occur. The warning does not assert that this condition has a distinct-label realization for every field size.
- Every-point failure is proved on the finite unramified locus, which suffices for generic nonclassicality. Neither the structured family nor bounded replacements are asserted to refute the algebraically independent branch problem. No surplus mathematical hypothesis was found beyond the harmless choice of an algebraically closed ambient field, which keeps the geometric formulation uniform.

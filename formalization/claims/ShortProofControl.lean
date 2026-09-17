/-
Claim: obs:generic-criterion-short-proof-control
Source: https://kbr.is-a.dev/math-research/#lean-generic-criterion-short-proof-control
Scope: Over any field and variable type. If a base derives one through degree d, then every polynomial of total degree at most B is derivable through B whenever d ≤ B; hence no nonzero subspace of degree-at-most-k polynomials is separated at any degree B ≥ max d k. Instantiated for a base containing a degree-at-most-one polynomial L and 1 - L, which derives one through degree one. This is the consistency control for the generic criterion on the easiest parity contradiction; it is not an audit of known short Res(⊕) refutations.
Declarations: MathResearch.PolynomialCalculus.derives_all_of_derives_one MathResearch.PolynomialCalculus.complementary_pair_derives_one MathResearch.PolynomialCalculus.no_separated_subspace_of_complementary_pair
-/
import claims.PolynomialCalculusReuse

namespace MathResearch.PolynomialCalculus
noncomputable section
open MvPolynomial
variable {K V : Type*} [Field K]

/-- A base that derives one derives every polynomial within the degree budget. -/
theorem derives_all_of_derives_one {F : Set (Poly K V)} {d B : ℕ} (h1 : Derives F d 1)
    (hdB : d ≤ B) (f : Poly K V) (hf : f.totalDegree ≤ B) : Derives F B f := by
  have h := h1.mul_polynomial f
  rw [mul_one] at h
  exact h.mono (fun _ hx => hx) (by
    have : (1 : Poly K V).totalDegree = 0 := totalDegree_one
    omega)

/-- A complementary pair `L`, `1 - L` of degree at most one derives one through degree one. -/
theorem complementary_pair_derives_one {F : Set (Poly K V)} (L : Poly K V)
    (hL : L.totalDegree ≤ 1) (hmem : L ∈ F) (hmem' : 1 - L ∈ F) : Derives F 1 1 := by
  have hd : (1 - L).totalDegree ≤ 1 :=
    (totalDegree_sub _ _).trans (max_le (by simp) hL)
  have h := Derives.add (Derives.hyp hmem hL) (Derives.hyp hmem' hd)
  simpa using h

/-- With a complementary pair in the base, a separated subspace must be zero. -/
theorem no_separated_subspace_of_complementary_pair {F : Set (Poly K V)} (L : Poly K V)
    (hL : L.totalDegree ≤ 1) (hmem : L ∈ F) (hmem' : 1 - L ∈ F) (k B : ℕ) (hB : 1 ≤ B)
    (hkB : k ≤ B) (U : Submodule K (Poly K V)) (hU : ∀ p ∈ U, p.totalDegree ≤ k)
    (hsep : ∀ f ∈ U, Derives F B f → f = 0) : U = ⊥ := by
  rw [Submodule.eq_bot_iff]
  intro f hf
  exact hsep f hf (derives_all_of_derives_one (complementary_pair_derives_one L hL hmem hmem')
    hB f ((hU f hf).trans hkB))

end
end MathResearch.PolynomialCalculus

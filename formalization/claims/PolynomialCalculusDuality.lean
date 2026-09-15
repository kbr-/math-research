/-
Claim: lem:duality
Source: https://kbr.is-a.dev/math-research/#lean-pc-finite-separation
Scope: Full historical finite-dimensional separation lemma: bounded-degree normalized NS designs iff no NS refutation, normalized PC annihilators iff no PC refutation, and NS≤PC. Functionals live on the ordinary bounded-total-degree subspace. No positivity or multiplicativity is assumed.
Declarations: MathResearch.PolynomialCalculus.normalizedFunctional_iff MathResearch.PolynomialCalculus.ns_design_iff MathResearch.PolynomialCalculus.pc_annihilator_iff MathResearch.PolynomialCalculus.nsSpace_le_pcSpace
-/
import claims.PolynomialCalculusReuse
import «third-party-claims».LinearSeparation

namespace MathResearch.PolynomialCalculus
noncomputable section
variable {K V : Type*} [Field K]

/-- A normalized functional on the actual bounded-degree polynomial space,
annihilating all eligible members of S. -/
def HasNormalizedFunctional (S : Submodule K (Poly K V)) (B : ℕ) : Prop :=
  ∃ l : degreeSpace (K := K) (V := V) B →ₗ[K] K,
    l ⟨1, by simp [degreeSpace]⟩ = 1 ∧
      ∀ p : degreeSpace (K := K) (V := V) B, (p : Poly K V) ∈ S → l p = 0

theorem normalizedFunctional_iff (S : Submodule K (Poly K V)) (B : ℕ) :
    HasNormalizedFunctional S B ↔ (1 : Poly K V) ∉ S := by
  exact MathResearch.LinearSeparation.normalized_annihilator_iff
    (S.comap (degreeSpace B).subtype) ⟨1, by simp [degreeSpace]⟩

theorem ns_design_iff (F : Set (Poly K V)) (B : ℕ) :
    HasNormalizedFunctional (nsSpace F B) B ↔ (1 : Poly K V) ∉ nsSpace F B :=
  normalizedFunctional_iff _ _

theorem pc_annihilator_iff (F : Set (Poly K V)) (B : ℕ) :
    HasNormalizedFunctional (pcSpace F B) B ↔ ¬ Derives F B (1 : Poly K V) :=
  normalizedFunctional_iff _ _

end
end MathResearch.PolynomialCalculus

/-
Claim: lem:simultaneous-affine-family-removal
Source: https://kbr.is-a.dev/math-research/#lean-simultaneous-affine-family-removal
Scope: Complete finite dependent-registry low/high affine ENS removal with supplied literal high witnesses and ordinary weighted PC replay; all domains retained, no multilinearity requirement on the degree-bounded target.
Declarations: MathResearch.affine_family_removal
-/
import claims.AffineFamilyRemovalWithUnits

namespace MathResearch
noncomputable section
open MvPolynomial PolynomialCalculus
open scoped BigOperators

theorem affine_family_removal {σ κ : Type} [Fintype σ] {ι : κ → Type} [∀ b, Fintype (ι b)]
    (g : ∀ b, ι b → MvPolynomial σ (ZMod 2)) (hg : ∀ b i, (g b i).totalDegree ≤ 1)
    (h k D : ℕ) (hh : 1 ≤ h) (hk : 1 ≤ k) (hD : 2*h+1 ≤ D)
    (F : Set (MvPolynomial σ (ZMod 2))) (hF : booleanBase ⊆ F)
    (f : MvPolynomial σ (ZMod 2)) (hf : f.totalDegree ≤ k)
    (hhigh : ∀ b, h*(k+1) < Module.finrank (ZMod 2) (Submodule.span (ZMod 2) (Set.range (g b))) →
      ∃ a : ι b → MvPolynomial σ (ZMod 2),
        (∀ i, (a i).totalDegree ≤ k-1) ∧ f = ∑ i, a i * g b i)
    (href : Derives (ensFamilySystem g h F) D 1) :
    Derives F (k*(D+1)) f := by
  exact affine_family_removal_with_units g hg h k D hh hk hD F hF f hf
    (fun b hb => Or.inr (hhigh b hb)) href

end
end MathResearch

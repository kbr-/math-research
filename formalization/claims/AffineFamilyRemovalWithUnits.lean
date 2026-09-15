/-
Claim: lem:affine-family-removal-with-unit-blocks
Source: https://kbr.is-a.dev/math-research/#lean-affine-family-removal-with-unit-blocks
Scope: Complete finite dependent-registry low/high affine ENS removal allowing each high block either a unit-span certificate or literal degree-(k−1) target witnesses. Unit-span blocks specialize to zero; all Boolean domains and ordinary weighted PC budgets are retained.
Declarations: MathResearch.affine_family_removal_with_units
-/
import claims.LowRankENS
import Mathlib.Tactic.Linarith

namespace MathResearch
noncomputable section
open MvPolynomial PolynomialCalculus
open scoped BigOperators

private theorem removal_budget (h k D r : ℕ) (hh : 1 ≤ h) (hk : 1 ≤ k)
    (hD : 2*h+1 ≤ D) (hr : r ≤ h*(k+1)) :
    r+1 ≤ k*D ∧ 2*k+1 ≤ k*D ∧ 2*k ≤ k*D ∧ D ≤ k*D := by
  have h1 := Nat.mul_le_mul_left k hD
  have h2 := Nat.mul_le_mul_left (h+1) hk
  have h3 := Nat.mul_le_mul_left D hk
  constructor
  · nlinarith
  constructor
  · nlinarith
  constructor <;> nlinarith

private def firstRowCoefficients {σ ι : Type} {h : ℕ}
    (a : ι → MvPolynomial σ (ZMod 2)) (u0 : Fin h) (v : Fin h × ι) :
    MvPolynomial σ (ZMod 2) := if v.1 = u0 then a v.2 else 0

private theorem substitution_old {σ ι : Type} {h : ℕ}
    (β : Fin h × ι → MvPolynomial σ (ZMod 2)) (p : MvPolynomial σ (ZMod 2)) :
    aeval (Sum.elim X β) (rename Sum.inl p) = p := by
  rw [aeval_rename]
  exact aeval_X_left_apply p

private theorem firstRow_product {σ ι : Type} [Fintype ι] {h : ℕ}
    (g a : ι → MvPolynomial σ (ZMod 2)) (u0 : Fin h) (f : MvPolynomial σ (ZMod 2))
    (hf : ∑ i, a i * g i = f) :
    aeval (Sum.elim X (firstRowCoefficients a u0)) (freshENSProduct g h) = 1-f := by
  classical
  have hfactor (u : Fin h) :
      aeval (Sum.elim X (firstRowCoefficients a u0)) (freshENSFactor g u) =
        if u = u0 then 1-f else 1 := by
    simp only [freshENSFactor, map_sub, map_one, map_sum, map_mul, aeval_X,
      Sum.elim_inr, substitution_old]
    by_cases hu : u = u0 <;> simp [firstRowCoefficients, hu, hf]
  rw [freshENSProduct, map_prod]
  simp_rw [hfactor]
  simp

private theorem local_removal_coefficients {σ ι : Type} [Fintype σ] [Fintype ι]
    (g : ι → MvPolynomial σ (ZMod 2)) (hg : ∀ i, (g i).totalDegree ≤ 1)
    (h k D : ℕ) (hh : 1 ≤ h) (hk : 1 ≤ k) (hD : 2*h+1 ≤ D)
    (f : MvPolynomial σ (ZMod 2)) (hf : f.totalDegree ≤ k)
    (hhigh : h*(k+1) < Module.finrank (ZMod 2) (Submodule.span (ZMod 2) (Set.range g)) →
      (1 : MvPolynomial σ (ZMod 2)) ∈ Submodule.span (ZMod 2) (Set.range g) ∨
      ∃ a : ι → MvPolynomial σ (ZMod 2), (∀ i, (a i).totalDegree ≤ k-1) ∧ f = ∑ i, a i*g i) :
    ∃ β : Fin h × ι → MvPolynomial σ (ZMod 2),
      (∀ v, (β v).totalDegree ≤ k) ∧
      ∀ i, f * (g i * aeval (Sum.elim X β) (freshENSProduct g h)) ∈
        nsSpace booleanBase (k*D+f.totalDegree) := by
  classical
  let r := Module.finrank (ZMod 2) (Submodule.span (ZMod 2) (Set.range g))
  by_cases hr : r ≤ h*(k+1)
  · obtain ⟨β,Z,hβ,hZ,hZd,_hZval,hcomp⟩ := lowRankENS_specialization g hg h k hr
    refine ⟨β,hβ,?_⟩
    intro i
    rw [hZ]
    exact nsSpace_mono (Set.Subset.refl _) (by
      have hb := (removal_budget h k D r hh hk hD hr).1
      omega) (nsSpace_mul (hcomp i) f)
  · rcases hhigh (Nat.lt_of_not_ge hr) with hunit | hhigh
    · obtain ⟨c,hc⟩ := (Submodule.mem_span_range_iff_exists_fun (ZMod 2)).mp hunit
      let a : ι → MvPolynomial σ (ZMod 2) := fun i => C (c i)
      have ha : ∑ i, a i*g i = 1 := by
        simpa only [a, smul_eq_C_mul] using hc
      let u0 : Fin h := ⟨0, by omega⟩
      refine ⟨firstRowCoefficients a u0, ?_, ?_⟩
      · intro v
        by_cases hv : v.1 = u0 <;> simp [firstRowCoefficients, hv, a]
      · intro i
        rw [firstRow_product g a u0 1 ha]
        simp
    · obtain ⟨a,ha,haf⟩ := hhigh
      let u0 : Fin h := ⟨0, by omega⟩
      refine ⟨firstRowCoefficients a u0, ?_, ?_⟩
      · intro v
        by_cases hv : v.1 = u0
        · simpa [firstRowCoefficients, hv] using (ha v.2).trans (Nat.sub_le k 1)
        · simp [firstRowCoefficients, hv]
      · intro i
        rw [firstRow_product g a u0 f haf.symm]
        have hp := nsSpace_mul (polynomial_boolean_ns_bound f k hf) (g i)
        have hn : -(g i * (f^2-f)) ∈ nsSpace booleanBase (k*D+f.totalDegree) := by
          apply Submodule.neg_mem
          exact nsSpace_mono (Set.Subset.refl _) (by
            have hb := (removal_budget h k D 0 hh hk hD (Nat.zero_le _)).2.1
            have hgi := hg i
            omega) hp
        convert hn using 1; ring

abbrev ENSFamilyVars (σ κ : Type) (ι : κ → Type) (h : ℕ) :=
  σ ⊕ (Σ b : κ, Fin h × ι b)

def familyFreshEmbedding {σ κ : Type} {ι : κ → Type} {h : ℕ} (b : κ) :
    FreshENSVars σ (ι b) h ↪ ENSFamilyVars σ κ ι h :=
  (Function.Embedding.refl σ).sumMap (Function.Embedding.sigmaMk (β := fun b => Fin h × ι b) b)

def ensFamilyValue {σ κ : Type} {ι : κ → Type} [∀ b, Fintype (ι b)]
    (g : ∀ b, ι b → MvPolynomial σ (ZMod 2)) (h : ℕ) (b : κ) :
    MvPolynomial (ENSFamilyVars σ κ ι h) (ZMod 2) :=
  rename (familyFreshEmbedding b) (freshENSProduct (g b) h)

def ensFamilySystem {σ κ : Type} {ι : κ → Type} [∀ b, Fintype (ι b)]
    (g : ∀ b, ι b → MvPolynomial σ (ZMod 2)) (h : ℕ) (F : Set (MvPolynomial σ (ZMod 2))) :
    Set (MvPolynomial (ENSFamilyVars σ κ ι h) (ZMod 2)) :=
  (rename Sum.inl) '' F ∪ booleanBase ∪
    {p | ∃ b, ∃ i : ι b, p = rename Sum.inl (g b i) * ensFamilyValue g h b}

private def familyImages {σ κ : Type} {ι : κ → Type} {h : ℕ}
    (β : ∀ b, Fin h × ι b → MvPolynomial σ (ZMod 2)) :
    ENSFamilyVars σ κ ι h → MvPolynomial σ (ZMod 2)
  | Sum.inl x => X x
  | Sum.inr ⟨b,v⟩ => β b v

private theorem familyImages_old {σ κ : Type} {ι : κ → Type} {h : ℕ}
    (β : ∀ b, Fin h × ι b → MvPolynomial σ (ZMod 2)) (p : MvPolynomial σ (ZMod 2)) :
    aeval (familyImages β) (rename Sum.inl p) = p := by
  rw [aeval_rename]
  exact aeval_X_left_apply p

private theorem familyImages_value {σ κ : Type} {ι : κ → Type} [∀ b, Fintype (ι b)] {h : ℕ}
    (g : ∀ b, ι b → MvPolynomial σ (ZMod 2))
    (β : ∀ b, Fin h × ι b → MvPolynomial σ (ZMod 2)) (b : κ) :
    aeval (familyImages β) (ensFamilyValue g h b) =
      aeval (Sum.elim X (β b)) (freshENSProduct (g b) h) := by
  rw [ensFamilyValue, aeval_rename]
  apply AlgHom.congr_fun
  ext v
  cases v <;> simp [familyImages, familyFreshEmbedding]

theorem affine_family_removal_with_units {σ κ : Type} [Fintype σ] {ι : κ → Type} [∀ b, Fintype (ι b)]
    (g : ∀ b, ι b → MvPolynomial σ (ZMod 2)) (hg : ∀ b i, (g b i).totalDegree ≤ 1)
    (h k D : ℕ) (hh : 1 ≤ h) (hk : 1 ≤ k) (hD : 2*h+1 ≤ D)
    (F : Set (MvPolynomial σ (ZMod 2))) (hF : booleanBase ⊆ F)
    (f : MvPolynomial σ (ZMod 2)) (hf : f.totalDegree ≤ k)
    (hhigh : ∀ b, h*(k+1) < Module.finrank (ZMod 2) (Submodule.span (ZMod 2) (Set.range (g b))) →
      (1 : MvPolynomial σ (ZMod 2)) ∈ Submodule.span (ZMod 2) (Set.range (g b)) ∨
      ∃ a : ι b → MvPolynomial σ (ZMod 2),
        (∀ i, (a i).totalDegree ≤ k-1) ∧ f = ∑ i, a i * g b i)
    (href : Derives (ensFamilySystem g h F) D 1) :
    Derives F (k*(D+1)) f := by
  classical
  have hc := fun b => local_removal_coefficients (g b) (hg b) h k D hh hk hD f hf (hhigh b)
  choose β hβ hcomp using hc
  have him : ∀ v, (familyImages β v).totalDegree ≤ k := by
    intro v
    cases v with
    | inl x => simpa [familyImages] using hk
    | inr v => exact hβ v.1 v.2
  have hbudget := removal_budget h k D 0 hh hk hD (Nat.zero_le _)
  have haxioms : ∀ a ∈ ensFamilySystem g h F, a.totalDegree ≤ D →
      Derives F (k*D+f.totalDegree) (f * aeval (familyImages β) a) := by
    intro a ha hd
    rcases ha with (ha | ha) | ha
    · obtain ⟨q,hq,rfl⟩ := ha
      have hqD : q.totalDegree ≤ D := by
        have he : (rename Sum.inl q : MvPolynomial (ENSFamilyVars σ κ ι h) (ZMod 2)).totalDegree =
            q.totalDegree := totalDegree_rename_injective ⟨Sum.inl, Sum.inl_injective⟩ q
        rwa [he] at hd
      rw [familyImages_old]
      have hp := (Derives.hyp hq hqD).mul_polynomial f
      apply hp.mono (Set.Subset.refl _)
      apply max_le
      · omega
      · omega
    · obtain ⟨v,rfl⟩ := ha
      simp only [map_sub, map_pow, aeval_X]
      have hp := nsSpace_mul (polynomial_boolean_ns_bound (familyImages β v) k (him v)) f
      apply nsSpace_le_pcSpace
      exact nsSpace_mono hF (by omega) hp
    · obtain ⟨b,i,rfl⟩ := ha
      rw [map_mul, familyImages_old, familyImages_value]
      exact nsSpace_le_pcSpace F (k*D+f.totalDegree) (nsSpace_mono hF le_rfl (hcomp b i))
  have hp := href.substitute_weighted (familyImages β) k him F f haxioms
  simp only [map_one, mul_one] at hp
  apply hp.mono (Set.Subset.refl _)
  nlinarith

end
end MathResearch

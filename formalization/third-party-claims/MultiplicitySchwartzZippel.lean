/-
Claim: third-party:DKSS-multiplicity-schwartz-zippel
Source: https://kbr.is-a.dev/math-research/branches/binary-multiplicity-degree/#entry-2026-09-24-lean-multiplicity-schwartz-zippel
Scope: Dvir, Kopparty, Saraf and Sudan, "Extensions to the method of multiplicities", SICOMP 2013,
Lemma 2.7 (arXiv 0901.2529v2, Lemma 8), for Hasse multiplicity as in their Definition 2.2 / Definition 3:
for any field F, finite index type σ with at least one variable, nonzero P ∈ F[x_σ] and finite S ⊆ F,
∑_{a ∈ S^σ} mult(P, a) ≤ totalDegree(P) · |S|^{|σ|-1}, with multiplicities in ℕ∞. Also the scaled form
|S| · ∑ mult ≤ totalDegree(P) · |S|^{|σ|}, valid for every finite σ including the empty one. The proof
follows theirs by induction on the number of variables, with their Hasse derivative P^{(i,0)} evaluated
on a line replaced by the coefficient of z'^i in P(a' + z', y).
Declarations: MathResearch.ThirdParty.MultiplicitySchwartzZippel.sliceMap MathResearch.ThirdParty.MultiplicitySchwartzZippel.coeff_sliceMap MathResearch.ThirdParty.MultiplicitySchwartzZippel.sliceMap_taylor MathResearch.ThirdParty.MultiplicitySchwartzZippel.sum_rootMultiplicity_le MathResearch.ThirdParty.MultiplicitySchwartzZippel.optionEquivLeft_shift MathResearch.ThirdParty.MultiplicitySchwartzZippel.mult_le_line MathResearch.ThirdParty.MultiplicitySchwartzZippel.multiplicity_schwartz_zippel_scaled MathResearch.ThirdParty.MultiplicitySchwartzZippel.multiplicity_schwartz_zippel
-/
import claims.HasseMultiplicity
import Mathlib.Algebra.MvPolynomial.Equiv
import Mathlib.Algebra.Polynomial.Taylor
import Mathlib.Algebra.Polynomial.Roots
import Mathlib.Data.Fintype.Option
import Mathlib.Data.Fintype.Pi
import Mathlib.Data.Finsupp.Option

namespace MathResearch.ThirdParty.MultiplicitySchwartzZippel

universe u

open MathResearch.HasseMultiplicity

noncomputable section

section slice

variable {R A : Type*} [CommRing R] [CommRing A] [Algebra R A]

/-- Apply an `R`-linear functional to every coefficient of a polynomial over `A`. -/
def sliceMap (L : A →ₗ[R] R) : Polynomial A →ₗ[R] Polynomial R :=
  Polynomial.lsum fun j => (Polynomial.monomial j).comp L

theorem sliceMap_monomial (L : A →ₗ[R] R) (n : ℕ) (a : A) :
    sliceMap L (Polynomial.monomial n a) = Polynomial.monomial n (L a) := by
  simp [sliceMap, Polynomial.lsum_apply, Polynomial.sum_monomial_index]

theorem coeff_sliceMap (L : A →ₗ[R] R) (Q : Polynomial A) (j : ℕ) :
    (sliceMap L Q).coeff j = L (Q.coeff j) := by
  induction Q using Polynomial.induction_on' with
  | add p q hp hq => simp [hp, hq]
  | monomial n a =>
    rw [sliceMap_monomial, Polynomial.coeff_monomial, Polynomial.coeff_monomial]
    split_ifs <;> simp

/-- Extracting coefficients by a linear functional commutes with the Taylor shift by a scalar. -/
theorem sliceMap_taylor (L : A →ₗ[R] R) (Q : Polynomial A) (c : R) (r : ℕ) :
    L ((Polynomial.taylor (algebraMap R A c) Q).coeff r) =
      (Polynomial.taylor c (sliceMap L Q)).coeff r := by
  induction Q using Polynomial.induction_on' with
  | add p q hp hq => simp [hp, hq]
  | monomial n a =>
    rw [sliceMap_monomial, Polynomial.taylor_monomial, Polynomial.taylor_monomial,
      Polynomial.coeff_C_mul, Polynomial.coeff_C_mul, Polynomial.coeff_X_add_C_pow,
      Polynomial.coeff_X_add_C_pow]
    have : a * ((algebraMap R A c) ^ (n - r) * (n.choose r : A)) =
        (c ^ (n - r) * (n.choose r : R)) • a := by
      rw [Algebra.smul_def, map_mul, map_pow, map_natCast]
      ring
    rw [this, map_smul, smul_eq_mul]
    ring

end slice

/-- Roots counted with multiplicity in a finite set are at most the degree. -/
theorem sum_rootMultiplicity_le {F : Type*} [Field F] (S : Finset F) (g : Polynomial F) :
    ∑ c ∈ S, g.rootMultiplicity c ≤ g.natDegree := by
  classical
  calc ∑ c ∈ S, g.rootMultiplicity c = ∑ c ∈ S, g.roots.count c := by
        simp [Polynomial.count_roots]
    _ = ∑ c ∈ S.filter (· ∈ g.roots.toFinset), g.roots.count c := by
        rw [Finset.sum_filter_of_ne]
        intro c _ hc
        simpa [Multiset.mem_toFinset] using Multiset.count_ne_zero.1 hc
    _ ≤ ∑ c ∈ g.roots.toFinset, g.roots.count c :=
        Finset.sum_le_sum_of_subset (fun c hc => (Finset.mem_filter.1 hc).2)
    _ = Multiset.card g.roots := Multiset.toFinset_sum_count_eq _
    _ ≤ g.natDegree := Polynomial.card_roots' g

variable {F : Type*} [Field F]

open MvPolynomial

/-- The point `(c, a')` of `F^{Option σ}`. -/
def pt {σ : Type*} (c : F) (a' : σ → F) : Option σ → F := fun o => o.elim c a'

/-- Shifting all variables, seen as a polynomial in the variable `none`, is the Taylor shift of
the coefficientwise shift. -/
theorem optionEquivLeft_shift {σ : Type*} (c : F) (a' : σ → F) (P : MvPolynomial (Option σ) F) :
    optionEquivLeft F σ (shift (pt c a') P) =
      Polynomial.taylor (C c) ((optionEquivLeft F σ P).map (shift a').toRingHom) := by
  have h : (optionEquivLeft F σ).toAlgHom.comp (shift (pt c a')) =
      ((Polynomial.taylorAlgHom (C c : MvPolynomial σ F)).restrictScalars F).comp
        ((Polynomial.mapAlgHom (shift a')).comp (optionEquivLeft F σ).toAlgHom) := by
    apply MvPolynomial.algHom_ext
    intro i
    cases i with
    | none =>
      simp [pt, optionEquivLeft_X_none, optionEquivLeft_C, Polynomial.taylor_X]
    | some j =>
      simp [pt, optionEquivLeft_X_some, optionEquivLeft_C, Polynomial.taylor_C,
        Polynomial.C_add]
  have := AlgHom.congr_fun h P
  simpa [Polynomial.mapAlgHom] using this

/-- The line estimate: along the line through `a'` in the direction of `none`, multiplicity is at
most the degree of a chosen monomial plus the root multiplicity of the coefficient slice. -/
theorem mult_le_line {σ : Type*} (P : MvPolynomial (Option σ) F) (a' : σ → F) (β : σ →₀ ℕ)
    (g : Polynomial F)
    (hg : g = sliceMap (lcoeff F β) ((optionEquivLeft F σ P).map (shift a').toRingHom))
    (hg0 : g ≠ 0) (c : F) :
    mult (pt c a') P ≤ ((β.degree + g.rootMultiplicity c : ℕ) : ℕ∞) := by
  set r := g.rootMultiplicity c
  have htay : Polynomial.taylor c g ≠ 0 := by
    intro h
    exact hg0 (Polynomial.taylor_injective c (by rw [h, map_zero]))
  have hr : r = (Polynomial.taylor c g).natTrailingDegree := by
    simp only [r]
    rw [Polynomial.rootMultiplicity_eq_natTrailingDegree, Polynomial.taylor_apply]
  have hcoeff : (Polynomial.taylor c g).coeff r ≠ 0 := by
    rw [hr]
    exact mt Polynomial.trailingCoeff_eq_zero.1 htay
  set m : Option σ →₀ ℕ := Finsupp.optionElim r β
  have hm : (shift (pt c a') P).coeff m = (Polynomial.taylor c g).coeff r := by
    rw [← optionEquivLeft_coeff_some_coeff_none F σ m, optionEquivLeft_shift]
    simp only [m, Finsupp.optionElim_apply_none, Finsupp.some_optionElim]
    rw [hg, ← sliceMap_taylor, algebraMap_eq]
    rfl
  have hdeg : m.degree = β.degree + r := by
    have hsplit : m = β.embDomain .some + Finsupp.single none r := by
      ext o
      cases o with
      | none => simp [m]
      | some x => simp [m, Finsupp.embDomain_some_some]
    rw [hsplit, map_add, Finsupp.embDomain_eq_mapDomain, Finsupp.degree_mapDomain,
      Finsupp.degree_single]
  have := mult_le_degree (pt c a') P (d := m) (by rw [hm]; exact hcoeff)
  rw [hdeg] at this
  exact this

/-- A polynomial in no variables is the constant given by its value. -/
theorem eval_ne_zero_of_isEmpty {σ : Type*} [IsEmpty σ] {P : MvPolynomial σ F} (hP : P ≠ 0)
    (a : σ → F) : eval a P ≠ 0 := by
  have hC : P = C (P.coeff 0) := by
    ext m
    rw [Subsingleton.elim m 0, coeff_C]
    simp
  rw [hC, eval_C]
  intro h
  exact hP (by rw [hC, h, C_0])

/-- The line bound for one fibre of the induction step. -/
theorem sum_line_le {σ : Type*} (S : Finset F) (P : MvPolynomial (Option σ) F) (a' : σ → F)
    (hPt : (optionEquivLeft F σ P).leadingCoeff ≠ 0) :
    ∑ c ∈ S, (mult (pt c a') P).toNat ≤
      S.card * (mult a' (optionEquivLeft F σ P).leadingCoeff).toNat +
        (optionEquivLeft F σ P).natDegree := by
  set Q0 := optionEquivLeft F σ P
  set t := Q0.natDegree
  obtain ⟨β, hβ, hβdeg⟩ := exists_coeff_ne_zero_degree_eq_mult a' hPt
  set g := sliceMap (lcoeff F β) (Q0.map (shift a').toRingHom) with hg
  have hgcoeff : ∀ j, g.coeff j = (shift a' (Q0.coeff j)).coeff β := by
    intro j
    rw [hg, coeff_sliceMap, Polynomial.coeff_map, lcoeff_apply]
    rfl
  have hg0 : g ≠ 0 := by
    intro h
    apply hβ
    show ((shift a') (Q0.coeff t)).coeff β = 0
    rw [← hgcoeff t, h, Polynomial.coeff_zero]
  have hgdeg : g.natDegree ≤ t := by
    rw [Polynomial.natDegree_le_iff_coeff_eq_zero]
    intro j hj
    rw [hgcoeff, Polynomial.coeff_eq_zero_of_natDegree_lt (by exact_mod_cast hj), map_zero]
    simp
  have hβnat : β.degree = (mult a' Q0.leadingCoeff).toNat := by
    rw [← hβdeg, ENat.toNat_natCast]
  calc ∑ c ∈ S, (mult (pt c a') P).toNat
      ≤ ∑ c ∈ S, (β.degree + g.rootMultiplicity c) := by
        apply Finset.sum_le_sum
        intro c _
        exact ENat.toNat_le_of_le_natCast (mult_le_line P a' β g hg hg0 c)
    _ = S.card * β.degree + ∑ c ∈ S, g.rootMultiplicity c := by
        rw [Finset.sum_add_distrib, Finset.sum_const, smul_eq_mul]
    _ ≤ S.card * β.degree + t := by
        gcongr
        exact (sum_rootMultiplicity_le S g).trans hgdeg
    _ = _ := by rw [hβnat]

omit [Field F] in
/-- Points of `S^{Option σ}` are pairs of a point of `S^σ` and a value in `S`. -/
theorem sum_piFinset_option {σ : Type*} [Fintype σ] [DecidableEq σ] [DecidableEq (Option σ)]
    (S : Finset F)
    (f : (Option σ → F) → ℕ) :
    ∑ a ∈ Fintype.piFinset (fun _ : Option σ => S), f a =
      ∑ a' ∈ Fintype.piFinset (fun _ : σ => S), ∑ c ∈ S, f (pt c a') := by
  rw [← Finset.sum_product']
  apply Finset.sum_nbij' (fun a => (a ∘ some, a none)) (fun p => pt p.2 p.1)
  · intro a ha
    simp only [Finset.mem_product, Fintype.mem_piFinset] at ha ⊢
    exact ⟨fun i => ha _, ha _⟩
  · intro p hp
    simp only [Finset.mem_product, Fintype.mem_piFinset] at hp ⊢
    intro o
    cases o with
    | none => exact hp.2
    | some i => exact hp.1 i
  · intro a _
    funext o
    cases o <;> rfl
  · intro p _
    rfl
  · intro a _
    congr 1
    funext o
    cases o <;> rfl

/-- The scaled multiplicity Schwartz–Zippel bound `|S| · ∑ mult ≤ deg P · |S|^{|σ|}`, valid for
every finite index type, including the empty one. -/
theorem multiplicity_schwartz_zippel_scaled (S : Finset F) (σ : Type u) [Fintype σ] :
    ∀ [DecidableEq σ] (P : MvPolynomial σ F), P ≠ 0 →
      S.card * ∑ a ∈ Fintype.piFinset (fun _ : σ => S), (mult a P).toNat ≤
        P.totalDegree * S.card ^ Fintype.card σ := by
  refine Fintype.induction_empty_option (P := fun σ _ => ∀ [DecidableEq σ]
    (P : MvPolynomial σ F), P ≠ 0 →
      S.card * ∑ a ∈ Fintype.piFinset (fun _ : σ => S), (mult a P).toNat ≤
        P.totalDegree * S.card ^ Fintype.card σ) ?_ ?_ ?_ σ
  · intro α β _ e ih _ P hP
    classical
    let _ : Fintype α := Fintype.ofEquiv β e.symm
    set P' := rename e.symm P
    have hP' : P' ≠ 0 := by
      intro h
      apply hP
      exact rename_injective _ e.symm.injective (h.trans (map_zero _).symm)
    have hback : rename e P' = P := by
      simp [P', rename_rename]
    have hdeg : P'.totalDegree = P.totalDegree :=
      totalDegree_renameEquiv e.symm P
    have hcard : Fintype.card α = Fintype.card β := Fintype.card_congr e
    have hsum : ∑ a ∈ Fintype.piFinset (fun _ : β => S), (mult a P).toNat =
        ∑ b ∈ Fintype.piFinset (fun _ : α => S), (mult b P').toNat := by
      apply Finset.sum_nbij' (fun a => a ∘ e) (fun b => b ∘ e.symm)
      · intro a ha
        simp only [Fintype.mem_piFinset] at ha ⊢
        exact fun i => ha _
      · intro b hb
        simp only [Fintype.mem_piFinset] at hb ⊢
        exact fun i => hb _
      · intro a _
        funext i
        simp
      · intro b _
        funext i
        simp
      · intro a _
        rw [← hback, mult_rename_equiv]
    have := ih P' hP'
    rw [hsum, ← hdeg, ← hcard]
    convert this using 3
  · intro _ P hP
    have hzero : ∀ a : PEmpty → F, (mult a P).toNat = 0 := by
      intro a
      rw [(mult_eq_zero_iff a P).2 (eval_ne_zero_of_isEmpty hP a)]
      rfl
    simp [hzero]
  · intro α _ ih _ P hP
    classical
    set Q0 := optionEquivLeft F α P
    have hQ0 : Q0 ≠ 0 := by
      intro h
      apply hP
      exact (optionEquivLeft F α).injective (h.trans (map_zero _).symm)
    set t := Q0.natDegree
    set Pt := Q0.leadingCoeff
    have hPt : Pt ≠ 0 := Polynomial.leadingCoeff_ne_zero.2 hQ0
    have hdeg : Pt.totalDegree + t ≤ P.totalDegree := by
      have ht : t ≤ P.totalDegree := by
        simp only [t, Q0, natDegree_optionEquivLeft]
        exact degreeOf_le_totalDegree P none
      exact totalDegree_coeff_optionEquivLeft_add_le F α P t ht
    have hih := ih Pt hPt
    have hcardpi : (Fintype.piFinset (fun _ : α => S)).card = S.card ^ Fintype.card α := by
      rw [Fintype.card_piFinset, Finset.prod_const, Finset.card_univ]
    rw [sum_piFinset_option, Fintype.card_option]
    calc S.card * ∑ a' ∈ Fintype.piFinset (fun _ : α => S), ∑ c ∈ S, (mult (pt c a') P).toNat
        ≤ S.card * ∑ a' ∈ Fintype.piFinset (fun _ : α => S),
            (S.card * (mult a' Pt).toNat + t) := by
          gcongr with a' _
          exact sum_line_le S P a' hPt
      _ = S.card * (S.card * ∑ a' ∈ Fintype.piFinset (fun _ : α => S), (mult a' Pt).toNat) +
            t * S.card ^ (Fintype.card α + 1) := by
          rw [Finset.sum_add_distrib, ← Finset.mul_sum, Finset.sum_const, hcardpi, smul_eq_mul]
          ring
      _ ≤ S.card * (Pt.totalDegree * S.card ^ Fintype.card α) +
            t * S.card ^ (Fintype.card α + 1) := by
          gcongr
      _ = (Pt.totalDegree + t) * S.card ^ (Fintype.card α + 1) := by ring
      _ ≤ P.totalDegree * S.card ^ (Fintype.card α + 1) := by gcongr

/-- **Multiplicity Schwartz–Zippel** (Dvir–Kopparty–Saraf–Sudan, Lemma 2.7): for a nonzero
polynomial `P` in at least one variable over a field and a finite set `S`,
`∑_{a ∈ S^σ} mult(P, a) ≤ deg P · |S|^{|σ| - 1}`. -/
theorem multiplicity_schwartz_zippel {σ : Type u} [Fintype σ] [DecidableEq σ]
    (hσ : 0 < Fintype.card σ) (S : Finset F) {P : MvPolynomial σ F} (hP : P ≠ 0) :
    ∑ a ∈ Fintype.piFinset (fun _ : σ => S), mult a P ≤
      ((P.totalDegree * S.card ^ (Fintype.card σ - 1) : ℕ) : ℕ∞) := by
  have hcoe : ∑ a ∈ Fintype.piFinset (fun _ : σ => S), mult a P =
      ((∑ a ∈ Fintype.piFinset (fun _ : σ => S), (mult a P).toNat : ℕ) : ℕ∞) := by
    rw [Nat.cast_sum]
    apply Finset.sum_congr rfl
    intro a _
    exact (ENat.natCast_toNat (mult_ne_top a hP)).symm
  rw [hcoe, Nat.cast_le]
  rcases S.eq_empty_or_nonempty with hS | hS
  · have : Nonempty σ := Fintype.card_pos_iff.1 hσ
    subst hS
    simp
  · have hpos : 0 < S.card := Finset.card_pos.2 hS
    apply Nat.le_of_mul_le_mul_left _ hpos
    have := multiplicity_schwartz_zippel_scaled S σ P hP
    calc S.card * ∑ a ∈ Fintype.piFinset (fun _ : σ => S), (mult a P).toNat
        ≤ P.totalDegree * S.card ^ Fintype.card σ := this
      _ = S.card * (P.totalDegree * S.card ^ (Fintype.card σ - 1)) := by
          conv_lhs => rw [show Fintype.card σ = Fintype.card σ - 1 + 1 by omega, pow_succ]
          ring

end

end MathResearch.ThirdParty.MultiplicitySchwartzZippel

/-
Claim: thm:per-order-value-char-two
Source: https://kbr.is-a.dev/math-research/branches/binary-multiplicity-degree/#per-order-value-char-two
Scope: Descent from a commutative ring R of characteristic two (for example any field of characteristic
two) to 𝔽₂. For an additive map φ : R → 𝔽₂ applied to every coefficient, the Hasse coefficients of
the image at a point a ∈ 𝔽₂^σ are the images of those of P at a, and the support can only shrink.
Choosing φ nonzero on one coefficient of lowest degree at the origin gives: every P ∈ R[x_1..x_n] with
multiplicity ≥ k at the nonzero points of {0,1}^n and exactly ℓ at the origin has total degree
≥ Φ(n,k,ℓ), and the 𝔽₂ polynomial of the per-order theorem, mapped to R, attains Φ. Hence the
per-order value δ_R(n,k,ℓ) = Φ(n,k,ℓ) for n ≥ 1, ℓ < k, and the least degree of a k-admissible
polynomial over R is degreeMin n k for n, k ≥ 1.
Declarations: MathResearch.PerOrderCharTwo.coeffMap MathResearch.PerOrderCharTwo.coeff_shift_coeffMap MathResearch.PerOrderCharTwo.totalDegree_coeffMap_le MathResearch.PerOrderCharTwo.lower_bound_char_two MathResearch.PerOrderCharTwo.per_order_value_char_two MathResearch.PerOrderCharTwo.degree_complete_char_two
-/
import claims.PerOrderMinimum
import Mathlib.LinearAlgebra.Dual.Lemmas

namespace MathResearch.PerOrderCharTwo

open MvPolynomial MathResearch.HasseMultiplicity MathResearch.PerOrderUpperBound
open MathResearch.PerOrderValue MathResearch.BinaryMultiplicityDegreeComplete

noncomputable section

variable {σ : Type*} {R : Type*} [CommRing R] [CharP R 2]

/-- The inclusion `𝔽₂ → R`. -/
abbrev iota (R : Type*) [CommRing R] [CharP R 2] : ZMod 2 →+* R := ZMod.castHom (dvd_refl 2) R

/-- Apply an additive map `φ : R → 𝔽₂` to every coefficient. -/
def coeffMap (φ : R →+ ZMod 2) (P : MvPolynomial σ R) : MvPolynomial σ (ZMod 2) :=
  ∑ u ∈ P.support, monomial u (φ (P.coeff u))

omit [CharP R 2] in
theorem coeff_coeffMap (φ : R →+ ZMod 2) (P : MvPolynomial σ R) (d : σ →₀ ℕ) :
    (coeffMap φ P).coeff d = φ (P.coeff d) := by
  classical
  rw [coeffMap, coeff_sum]
  simp only [coeff_monomial]
  rw [Finset.sum_ite_eq']
  split_ifs with h
  · rfl
  · rw [notMem_support_iff.1 h, map_zero]

theorem zmod_two_cases : ∀ t : ZMod 2, t = 0 ∨ t = 1 := by decide

theorem phi_mul_iota (φ : R →+ ZMod 2) (x : R) (t : ZMod 2) : φ (x * iota R t) = t * φ x := by
  rcases zmod_two_cases t with rfl | rfl <;> simp

omit [CharP R 2] in
theorem coeffMap_monomial (φ : R →+ ZMod 2) (u : σ →₀ ℕ) (c : R) :
    coeffMap φ (monomial u c) = monomial u (φ c) := by
  classical
  ext d
  rw [coeff_coeffMap, coeff_monomial, coeff_monomial]
  split_ifs <;> simp

omit [CharP R 2] in
theorem coeffMap_add (φ : R →+ ZMod 2) (P Q : MvPolynomial σ R) :
    coeffMap φ (P + Q) = coeffMap φ P + coeffMap φ Q := by
  ext d
  simp [coeff_coeffMap]

/-- The shift commutes with the inclusion `𝔽₂ → R`. -/
theorem map_shift (a : σ → ZMod 2) (P : MvPolynomial σ (ZMod 2)) :
    map (iota R) (shift a P) = shift (fun i => iota R (a i)) (map (iota R) P) := by
  have h : (map (iota R)).comp (shift a).toRingHom =
      (shift (fun i => iota R (a i))).toRingHom.comp (map (iota R)) := by
    apply MvPolynomial.ringHom_ext
    · intro r
      simp [shift]
    · intro i
      simp [shift]
  exact congrArg (fun f => f P) h

/-- **Descent of Hasse coefficients.** At a point of `𝔽₂^σ`, the Hasse coefficients of `coeffMap φ P`
are the images under `φ` of those of `P`. -/
theorem coeff_shift_coeffMap (φ : R →+ ZMod 2) (a : σ → ZMod 2) (P : MvPolynomial σ R)
    (d : σ →₀ ℕ) :
    (shift a (coeffMap φ P)).coeff d = φ ((shift (fun i => iota R (a i)) P).coeff d) := by
  induction P using MvPolynomial.induction_on' with
  | monomial u c =>
    rw [coeffMap_monomial]
    have hm2 : shift a (monomial u (φ c)) = C (φ c) * shift a (monomial u 1) := by
      rw [show monomial u (φ c) = C (φ c) * monomial u 1 by rw [C_mul_monomial, mul_one],
        map_mul, shift_C]
    have hmR : shift (fun i => iota R (a i)) (monomial u c) =
        C c * shift (fun i => iota R (a i)) (monomial u 1) := by
      rw [show monomial u c = C c * monomial u 1 by rw [C_mul_monomial, mul_one],
        map_mul, shift_C]
    rw [hm2, hmR, coeff_C_mul, coeff_C_mul]
    have h1 : (monomial u (1 : R)) = map (iota R) (monomial u (1 : ZMod 2)) := by
      rw [map_monomial]
      simp
    rw [h1, ← map_shift, coeff_map, phi_mul_iota, mul_comm]
  | add P Q hP hQ =>
    rw [coeffMap_add, map_add, map_add]
    simp [hP, hQ]

omit [CharP R 2] in
theorem totalDegree_coeffMap_le (φ : R →+ ZMod 2) (P : MvPolynomial σ R) :
    (coeffMap φ P).totalDegree ≤ P.totalDegree := by
  apply Finset.sup_mono
  intro d hd
  rw [mem_support_iff] at hd ⊢
  intro h
  exact hd (by rw [coeff_coeffMap, h, map_zero])

theorem le_mult_coeffMap (φ : R →+ ZMod 2) (a : σ → ZMod 2) (P : MvPolynomial σ R) (k : ℕ)
    (h : (k : ℕ∞) ≤ mult (fun i => iota R (a i)) P) : (k : ℕ∞) ≤ mult a (coeffMap φ P) := by
  rw [coe_le_mult_iff] at h ⊢
  intro d hd
  rw [coeff_shift_coeffMap, h d hd, map_zero]

/-- An additive map `R → 𝔽₂` that is nonzero at a given nonzero element. -/
theorem exists_addHom_ne_zero {c : R} (hc : c ≠ 0) : ∃ φ : R →+ ZMod 2, φ c ≠ 0 := by
  let _ : Module (ZMod 2) R := Module.compHom R (iota R)
  have h := (Module.forall_dual_apply_eq_zero_iff (ZMod 2) c).not.2 hc
  push Not at h
  obtain ⟨φ, hφ⟩ := h
  exact ⟨φ.toAddMonoidHom, hφ⟩

theorem iota_zero_point {n : ℕ} : (fun i => iota R ((0 : Fin n → ZMod 2) i)) = 0 := by
  funext i; simp

/-- **Lower bound over a ring of characteristic two.** -/
theorem lower_bound_char_two {n k ℓ : ℕ} (hn : 1 ≤ n) (hℓ : ℓ < k) (P : MvPolynomial (Fin n) R)
    (hP : ∀ a : Fin n → ZMod 2, a ≠ 0 → (k : ℕ∞) ≤ mult (fun i => iota R (a i)) P)
    (h0 : mult 0 P = ℓ) : Phi n k ℓ ≤ P.totalDegree := by
  have hne : P ≠ 0 := by
    rintro rfl
    simp at h0
  obtain ⟨d, hd, hdeg⟩ := exists_coeff_ne_zero_degree_eq_mult (0 : Fin n → R) hne
  obtain ⟨φ, hφ⟩ := exists_addHom_ne_zero hd
  set Q := coeffMap φ P with hQ
  have hQa : ∀ a : Fin n → ZMod 2, a ≠ 0 → (k : ℕ∞) ≤ mult a Q :=
    fun a ha => le_mult_coeffMap φ a P k (hP a ha)
  have hQ0 : mult 0 Q = ℓ := by
    apply le_antisymm
    · have hc : (shift 0 Q).coeff d ≠ 0 := by
        rw [hQ, coeff_shift_coeffMap, iota_zero_point]
        exact hφ
      calc mult 0 Q ≤ d.degree := mult_le_degree 0 Q hc
        _ = ℓ := by rw [hdeg, h0]
    · apply le_mult_coeffMap φ 0 P ℓ
      rw [iota_zero_point, h0]
  calc Phi n k ℓ ≤ Q.totalDegree := (per_order_value hn hℓ).2 Q hQa hQ0
    _ ≤ P.totalDegree := totalDegree_coeffMap_le φ P

theorem coeff_shift_map (a : σ → ZMod 2) (P : MvPolynomial σ (ZMod 2)) (d : σ →₀ ℕ) :
    (shift (fun i => iota R (a i)) (map (iota R) P)).coeff d = iota R ((shift a P).coeff d) := by
  rw [← map_shift, coeff_map]

theorem mult_map_ge (a : σ → ZMod 2) (P : MvPolynomial σ (ZMod 2)) (k : ℕ)
    (h : (k : ℕ∞) ≤ mult a P) : (k : ℕ∞) ≤ mult (fun i => iota R (a i)) (map (iota R) P) := by
  rw [coe_le_mult_iff] at h ⊢
  intro d hd
  rw [coeff_shift_map, h d hd, map_zero]

theorem mult_zero_map {P : MvPolynomial σ (ZMod 2)} {ℓ : ℕ} (h0 : mult 0 P = ℓ) :
    mult 0 (map (iota R) P) = ℓ := by
  have hne : P ≠ 0 := by
    rintro rfl
    simp at h0
  have hz : (fun i => iota R ((0 : σ → ZMod 2) i)) = 0 := by funext i; simp
  apply le_antisymm
  · obtain ⟨d, hd, hdeg⟩ := exists_coeff_ne_zero_degree_eq_mult (0 : σ → ZMod 2) hne
    have hc : (shift 0 (map (iota R) P)).coeff d ≠ 0 := by
      rw [← hz, coeff_shift_map]
      exact fun h => hd ((ZMod.castHom_injective R).eq_iff.1 (h.trans (map_zero _).symm))
    calc mult 0 (map (iota R) P) ≤ d.degree := mult_le_degree 0 _ hc
      _ = ℓ := by rw [hdeg, h0]
  · rw [← hz]
    exact mult_map_ge 0 P ℓ (le_of_eq h0.symm)

theorem totalDegree_map_iota (P : MvPolynomial σ (ZMod 2)) :
    (map (iota R) P).totalDegree = P.totalDegree := by
  unfold totalDegree
  rw [support_map_of_injective P (ZMod.castHom_injective R)]

/-- **The per-order value over a ring of characteristic two** (`thm:per-order-value-char-two`).
For `n ≥ 1` and `ℓ < k`, `Φ(n, k, ℓ)` is the least total degree of `P ∈ R[x_1,…,x_n]` with
multiplicity `≥ k` at the nonzero points of `{0,1}^n` and exactly `ℓ` at the origin, and it is
attained. -/
theorem per_order_value_char_two {n k ℓ : ℕ} (hn : 1 ≤ n) (hℓ : ℓ < k) :
    (∃ P : MvPolynomial (Fin n) R,
        (∀ a : Fin n → ZMod 2, a ≠ 0 → (k : ℕ∞) ≤ mult (fun i => iota R (a i)) P) ∧
        mult 0 P = ℓ ∧ P.totalDegree = Phi n k ℓ) ∧
      ∀ P : MvPolynomial (Fin n) R,
        (∀ a : Fin n → ZMod 2, a ≠ 0 → (k : ℕ∞) ≤ mult (fun i => iota R (a i)) P) →
        mult 0 P = ℓ → Phi n k ℓ ≤ P.totalDegree := by
  refine ⟨?_, fun P hP h0 => lower_bound_char_two hn hℓ P hP h0⟩
  obtain ⟨⟨P, hP, h0, hdeg⟩, _⟩ := per_order_value hn hℓ
  exact ⟨map (iota R) P, fun a ha => mult_map_ge a P k (hP a ha), mult_zero_map h0,
    by rw [totalDegree_map_iota, hdeg]⟩

/-- **The least degree of a `k`-admissible polynomial over a ring of characteristic two** is
`degreeMin n k`, and it is attained. -/
theorem degree_complete_char_two {n k : ℕ} (hn : 1 ≤ n) (hk : 1 ≤ k) :
    (∃ P : MvPolynomial (Fin n) R,
        (∀ a : Fin n → ZMod 2, a ≠ 0 → (k : ℕ∞) ≤ mult (fun i => iota R (a i)) P) ∧
        mult 0 P < k ∧ P.totalDegree = degreeMin n k) ∧
      ∀ P : MvPolynomial (Fin n) R,
        (∀ a : Fin n → ZMod 2, a ≠ 0 → (k : ℕ∞) ≤ mult (fun i => iota R (a i)) P) →
        mult 0 P < k → degreeMin n k ≤ P.totalDegree := by
  obtain ⟨hle, ℓ0, hℓ0, heq⟩ := PerOrderMinimum.min_phi hn hk
  refine ⟨?_, ?_⟩
  · obtain ⟨⟨P, hP, h0, hdeg⟩, _⟩ := per_order_value_char_two (R := R) hn hℓ0
    refine ⟨P, hP, ?_, by rw [hdeg, heq]⟩
    rw [h0]
    exact_mod_cast hℓ0
  · intro P hP h0
    have hfin : mult 0 P ≠ ⊤ := ne_top_of_lt h0
    obtain ⟨ℓ, hℓ⟩ : ∃ ℓ : ℕ, mult 0 P = ℓ := ⟨(mult 0 P).toNat, (ENat.natCast_toNat hfin).symm⟩
    have hℓk : ℓ < k := by
      have := h0
      rw [hℓ] at this
      exact_mod_cast this
    exact (hle ℓ hℓk).trans (lower_bound_char_two hn hℓk P hP hℓ)

end

end MathResearch.PerOrderCharTwo

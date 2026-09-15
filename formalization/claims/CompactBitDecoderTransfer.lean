/-
Claim: lem:compact-bit-ordinary-PC-decoder
Source: https://kbr.is-a.dev/math-research/#lean-compact-bit-ordinary-PC-decoder
Scope: For ℓ≥2, original-degree NS axiom-image certificates and degree-preserving transfer of arbitrary compact-base PC consequences to the functional unary base. Uses the separately verified all-ℓ injective degree-preserving coordinate decoder.
Declarations: MathResearch.PolynomialCalculus.compactDecoder_boolean_ns MathResearch.PolynomialCalculus.compactDecoder_collision_ns MathResearch.PolynomialCalculus.compactDecoder_PC
-/
import claims.CompactBitDecoder
import claims.TwoRowInterpolation

namespace MathResearch.PolynomialCalculus
noncomputable section
open MvPolynomial
open scoped BigOperators

private theorem boolean_generator_degree {V : Type*} (v : V) :
    ((X v : Poly (ZMod 2) V)^2-X v).totalDegree = 2 := by
  rw [sub_eq_add_neg]
  apply (totalDegree_add_eq_left_of_totalDegree_lt ?_).trans
    (totalDegree_X_pow v 2)
  simp

private theorem binary_affine_pair_degree {V : Type*} [DecidableEq V] (x y : V)
    (hxy : x ≠ y) : (1 + (X x : Poly (ZMod 2) V) + X y).totalDegree = 1 := by
  apply Nat.le_antisymm
  · apply (totalDegree_add _ _).trans
    simp only [totalDegree_X, max_le_iff]
    exact ⟨(totalDegree_add _ _).trans (by simp), le_rfl⟩
  · have hc : (1 + (X x : Poly (ZMod 2) V) + X y).coeff (Finsupp.single x 1) ≠ 0 := by
      have hsingle : (Finsupp.single y 1 : V →₀ ℕ) ≠ Finsupp.single x 1 := by
        intro he
        have h := congrArg (fun d : V →₀ ℕ => d x) he
        simp [hxy] at h
      have hzero : (0 : V →₀ ℕ) ≠ Finsupp.single x 1 := by
        intro he
        have h := congrArg (fun d : V →₀ ℕ => d x) he
        simp at h
      simp [coeff_one, coeff_X, hsingle, hzero]
    have hm := le_totalDegree (mem_support_iff.mpr hc)
    simpa using hm

private theorem degree_finset_prod {V I : Type*} [DecidableEq I]
    (S : Finset I) (f : I → Poly (ZMod 2) V)
    (hf : ∀ i ∈ S, f i ≠ 0) :
    (∏ i ∈ S, f i).totalDegree = ∑ i ∈ S, (f i).totalDegree := by
  revert hf
  induction S using Finset.induction_on with
  | empty => intro _; simp
  | @insert i S hi ih =>
    intro hf
    have hfS : ∀ j ∈ S, f j ≠ 0 := fun j hj => hf j (Finset.mem_insert_of_mem hj)
    rw [Finset.prod_insert hi, Finset.sum_insert hi,
      totalDegree_mul_of_isDomain (hf i (Finset.mem_insert_self _ _))
        (Finset.prod_ne_zero_iff.mpr hfS), ih hfS]

private theorem compact_collision_degree {m ℓ : ℕ} (i i' : Fin m) (hii : i ≠ i') :
    (∏ t : Fin ℓ, (1 + (X (i,t) : Poly (ZMod 2) (Fin m × Fin ℓ)) + X (i',t))).totalDegree = ℓ := by
  have hf (t : Fin ℓ) : (1 + (X (i,t) : Poly (ZMod 2) (Fin m × Fin ℓ)) + X (i',t)).totalDegree = 1 :=
    binary_affine_pair_degree _ _ (by intro h; exact hii (congrArg Prod.fst h))
  rw [degree_finset_prod]
  · simp [hf]
  · intro t _ hz
    have h := hf t
    rw [hz, totalDegree_zero] at h
    omega

def localDecodedCollision (ℓ : ℕ) : TwoRowPoly (2^ℓ) :=
  ∏ t : Fin ℓ, (1 + decoderInput 2 ℓ (0,t) + decoderInput 2 ℓ (1,t))

private theorem localDecodedCollision_degree (ℓ : ℕ) :
    (localDecodedCollision ℓ).totalDegree ≤ ℓ := by
  apply (totalDegree_finsetProd _ _).trans
  calc
    _ ≤ ∑ _t : Fin ℓ, 1 := by
      apply Finset.sum_le_sum
      intro t _
      exact (totalDegree_add _ _).trans (max_le
        ((totalDegree_add _ _).trans (max_le (by simp) (decoderInput_degree 2 ℓ (0,t))))
        (decoderInput_degree 2 ℓ (1,t)))
    _ = ℓ := by simp

private theorem binaryIndicator (a : ZMod 2) : (if a = 1 then 1 else 0) = a := by
  split_ifs with ha
  · exact ha.symm
  · fin_cases a
    · rfl
    · exact False.elim (ha rfl)

private theorem eval_decoderInput_zero (ℓ : ℕ) (j k : Fin (2^ℓ)) (t : Fin ℓ) :
    eval (twoRowPoint j k) (decoderInput 2 ℓ (0,t)) = bitLabelEquiv ℓ j t := by
  simp [decoderInput, twoRowPoint, apply_ite]
  rw [Finset.sum_eq_single j]
  · simpa using binaryIndicator (bitLabelEquiv ℓ j t)
  · intro b _ hbj
    simp [hbj]
  · simp

private theorem eval_decoderInput_one (ℓ : ℕ) (j k : Fin (2^ℓ)) (t : Fin ℓ) :
    eval (twoRowPoint j k) (decoderInput 2 ℓ (1,t)) = bitLabelEquiv ℓ k t := by
  simp [decoderInput, twoRowPoint, apply_ite]
  rw [Finset.sum_eq_single k]
  · simpa using binaryIndicator (bitLabelEquiv ℓ k t)
  · intro b _ hbk
    simp [hbk]
  · simp

private theorem localDecodedCollision_eval (ℓ : ℕ) (j k : Fin (2^ℓ)) :
    eval (twoRowPoint j k) (localDecodedCollision ℓ) = if j = k then 1 else 0 := by
  simp only [localDecodedCollision, map_prod, map_add, map_one,
    eval_decoderInput_zero, eval_decoderInput_one]
  by_cases hjk : j = k
  · subst k
    have hz (a : ZMod 2) : a + a = 0 := by fin_cases a <;> decide
    simp [add_assoc, hz]
  · rw [ite_eq_right hjk]
    have hlabels : bitLabelEquiv ℓ j ≠ bitLabelEquiv ℓ k :=
      (bitLabelEquiv ℓ).injective.ne hjk
    obtain ⟨t, ht⟩ := Function.ne_iff.mp hlabels
    apply Finset.prod_eq_zero (Finset.mem_univ t)
    generalize bitLabelEquiv ℓ j t = a at ht ⊢
    generalize bitLabelEquiv ℓ k t = b at ht ⊢
    fin_cases a <;> fin_cases b
    all_goals first | exact False.elim (ht rfl) | decide

private theorem localDecodedCollision_interp (ℓ : ℕ) :
    twoRowInterp (2^ℓ) (localDecodedCollision ℓ) =
      ∑ j : Fin (2^ℓ), (X (0,j) : TwoRowPoly (2^ℓ)) * X (1,j) := by
  simp [twoRowInterp, localDecodedCollision_eval, ite_smul]

private theorem twoRowBase_subset_functional (n : ℕ) :
    twoRowBase n ⊆ functionalUnaryBase (K := ZMod 2) 2 n := by
  intro p hp
  rcases hp with (hb | ⟨r, rfl⟩) | ⟨r,j,k,hjk,rfl⟩
  · exact Or.inl (Or.inl (Or.inl hb))
  · exact Or.inl (Or.inl (Or.inr ⟨r, rfl⟩))
  · exact Or.inr ⟨r,j,k,hjk,rfl⟩

private theorem localDecodedCollision_ns (ℓ : ℕ) (hℓ : 2 ≤ ℓ) :
    localDecodedCollision ℓ ∈ nsSpace (functionalUnaryBase (K := ZMod 2) 2 (2^ℓ)) ℓ := by
  have h := nsSpace_mono (twoRowBase_subset_functional (2^ℓ))
    (max_le (localDecodedCollision_degree ℓ) hℓ) (twoRow_interpolation (localDecodedCollision ℓ))
  rw [localDecodedCollision_interp] at h
  have hs : (∑ j : Fin (2^ℓ), (X (0,j) : TwoRowPoly (2^ℓ)) * X (1,j)) ∈
      nsSpace (functionalUnaryBase (K := ZMod 2) 2 (2^ℓ)) ℓ := by
    apply Submodule.sum_mem
    intro j _
    have hg : (X (0,j) : TwoRowPoly (2^ℓ)) * X (1,j) ∈
        functionalUnaryBase (K := ZMod 2) 2 (2^ℓ) :=
      Or.inl (Or.inr ⟨0,1,j,by decide,rfl⟩)
    have hd : ((X (0,j) : TwoRowPoly (2^ℓ)) * X (1,j)).totalDegree ≤ ℓ :=
      (totalDegree_mul _ _).trans (by simpa using hℓ)
    simpa only [one_mul] using nsSpace_generator (q := (1 : TwoRowPoly (2^ℓ))) hg
      (by simpa only [one_mul] using hd)
  simpa only [sub_add_cancel] using Submodule.add_mem _ h hs

private theorem nsSpace_map {V W : Type*} {F : Set (Poly (ZMod 2) V)}
    {G : Set (Poly (ZMod 2) W)} (φ : Poly (ZMod 2) V →ₐ[ZMod 2] Poly (ZMod 2) W)
    (hdeg : ∀ p, (φ p).totalDegree ≤ p.totalDegree) (hF : ∀ f ∈ F, φ f ∈ G)
    {B : ℕ} {p : Poly (ZMod 2) V} (hp : p ∈ nsSpace F B) : φ p ∈ nsSpace G B := by
  induction hp using Submodule.span_induction with
  | mem p hp =>
    rcases hp with ⟨f,hf,q,rfl,hd⟩
    rw [map_mul]
    apply nsSpace_generator (hF f hf)
    rw [← map_mul]
    exact (hdeg _).trans hd
  | zero => simp
  | add p q _ _ ih jh => simpa only [map_add] using Submodule.add_mem _ ih jh
  | smul a p _ ih => simpa only [map_smul] using Submodule.smul_mem _ a ih

private def rowEmbedding {r m n : ℕ} (e : Fin r → Fin m) :
    Poly (ZMod 2) (Fin r × Fin n) →ₐ[ZMod 2] Poly (ZMod 2) (Fin m × Fin n) :=
  aeval (fun v => X (e v.1,v.2))

private theorem rowEmbedding_degree {r m n : ℕ} (e : Fin r → Fin m)
    (p : Poly (ZMod 2) (Fin r × Fin n)) : (rowEmbedding e p).totalDegree ≤ p.totalDegree := by
  simpa only [Nat.one_mul, rowEmbedding] using
    substitution_degree (fun v : Fin r × Fin n => (X (e v.1,v.2) :
      Poly (ZMod 2) (Fin m × Fin n))) 1 (by intro v; simp) p

private theorem rowEmbedding_base {r m n : ℕ} (e : Fin r → Fin m) (he : Function.Injective e)
    (p : Poly (ZMod 2) (Fin r × Fin n)) (hp : p ∈ functionalUnaryBase r n) :
    rowEmbedding e p ∈ functionalUnaryBase m n := by
  rcases hp with ((hb | ⟨i,rfl⟩) | ⟨i,i',j,hii,rfl⟩) | ⟨i,j,k,hjk,rfl⟩
  · obtain ⟨v,rfl⟩ := hb
    exact Or.inl (Or.inl (Or.inl ⟨(e v.1,v.2), by simp [rowEmbedding]⟩))
  · exact Or.inl (Or.inl (Or.inr ⟨e i, by simp [rowEmbedding]⟩))
  · exact Or.inl (Or.inr ⟨e i,e i',j,he.ne hii,by simp [rowEmbedding]⟩)
  · exact Or.inr ⟨e i,j,k,hjk,by simp [rowEmbedding]⟩

private def rowPair {m : ℕ} (i i' : Fin m) (r : Fin 2) : Fin m :=
  if r = 0 then i else i'

private theorem rowPair_injective {m : ℕ} (i i' : Fin m) (hii : i ≠ i') :
    Function.Injective (rowPair i i') := by
  intro r s h
  fin_cases r <;> fin_cases s <;> simp_all [rowPair, Ne.symm hii]

private theorem rowEmbedding_decoderInput {m ℓ : ℕ} (e : Fin 2 → Fin m) (v : Fin 2 × Fin ℓ) :
    rowEmbedding e (decoderInput 2 ℓ v) = decoderInput m ℓ (e v.1,v.2) := by
  simp [decoderInput, rowEmbedding, apply_ite]

private theorem rowEmbedding_collision {m ℓ : ℕ} (i i' : Fin m) :
    rowEmbedding (rowPair i i') (localDecodedCollision ℓ) =
      compactDecoder m ℓ (∏ t : Fin ℓ, (1 + X (i,t) + X (i',t))) := by
  simp only [localDecodedCollision, map_prod, map_add, map_one, rowEmbedding_decoderInput]
  simp [compactDecoder, rowPair]

theorem compactDecoder_collision_ns {m ℓ : ℕ} (i i' : Fin m) (hii : i ≠ i') (hℓ : 2 ≤ ℓ) :
    compactDecoder m ℓ (∏ t : Fin ℓ, (1 + X (i,t) + X (i',t))) ∈
      nsSpace (functionalUnaryBase (K := ZMod 2) m (2^ℓ)) ℓ := by
  rw [← rowEmbedding_collision i i']
  exact nsSpace_map (rowEmbedding (rowPair i i')) (rowEmbedding_degree _)
    (rowEmbedding_base _ (rowPair_injective i i' hii)) (localDecodedCollision_ns ℓ hℓ)

theorem compactDecoder_boolean_ns (m ℓ : ℕ) (v : Fin m × Fin ℓ) :
    compactDecoder m ℓ (X v^2-X v) ∈
      nsSpace (functionalUnaryBase (K := ZMod 2) m (2^ℓ)) 2 := by
  have h := polynomial_boolean_ns_bound (decoderInput m ℓ v) 1 (decoderInput_degree m ℓ v)
  have hbase : booleanBase ⊆ functionalUnaryBase (K := ZMod 2) m (2^ℓ) :=
    fun _ hf => Or.inl (Or.inl (Or.inl hf))
  simpa only [compactDecoder, map_sub, map_pow, aeval_X] using
    nsSpace_mono hbase (by decide : 2*1 ≤ 2) h

theorem compactDecoder_PC {m ℓ B : ℕ} (hℓ : 2 ≤ ℓ)
    {p : Poly (ZMod 2) (Fin m × Fin ℓ)} (hp : Derives (compactBitBase m ℓ) B p) :
    Derives (functionalUnaryBase (K := ZMod 2) m (2^ℓ)) B (compactDecoder m ℓ p) := by
  have h := hp.substitute_weighted (decoderInput m ℓ) 1 (decoderInput_degree m ℓ)
    (functionalUnaryBase (K := ZMod 2) m (2^ℓ)) 1 (by
      intro f hf hd
      simp only [totalDegree_one, Nat.add_zero, one_mul]
      apply nsSpace_le_pcSpace
      rcases hf with ⟨v,rfl⟩ | ⟨i,i',hii,rfl⟩
      · have hB : 2 ≤ B := by rwa [boolean_generator_degree] at hd
        exact nsSpace_mono (Set.Subset.refl _) hB (compactDecoder_boolean_ns m ℓ v)
      · have hB : ℓ ≤ B := by rwa [compact_collision_degree i i' (ne_of_lt hii)] at hd
        exact nsSpace_mono (Set.Subset.refl _) hB
          (compactDecoder_collision_ns i i' (ne_of_lt hii) hℓ))
  simpa only [Nat.one_mul, totalDegree_one, Nat.add_zero, one_mul, compactDecoder] using h

end
end MathResearch.PolynomialCalculus

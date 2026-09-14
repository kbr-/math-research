/-
Claim: third-party:augmented-chain-naturality
Source: https://kbr.is-a.dev/math-research/#lean-augmented-chain-naturality
Scope: Injective vertex relabeling and subcomplex inclusion commute with the finite augmented F₂ boundary; includes chessboard transpose and compatibility with the original incidence boundary.
Declarations: MathResearch.ThirdParty.Augmented.boundary_extend MathResearch.ThirdParty.Augmented.boundary_push MathResearch.ThirdParty.Augmented.push_supported MathResearch.ThirdParty.Augmented.chainMap MathResearch.ThirdParty.Augmented.differential_chainMap MathResearch.ThirdParty.Augmented.inclusion MathResearch.ThirdParty.Augmented.differential_inclusion MathResearch.ThirdParty.Augmented.chessboard_boundary_coordinate MathResearch.ThirdParty.Augmented.chessboard_differential MathResearch.ThirdParty.Augmented.chessboard_boundary MathResearch.ThirdParty.Augmented.chessboard_cycle_iff MathResearch.ThirdParty.Augmented.push_apply_map MathResearch.ThirdParty.Augmented.push_injective MathResearch.ThirdParty.Augmented.push_equiv MathResearch.ThirdParty.Augmented.push_equiv_inverse MathResearch.ThirdParty.Augmented.transpose_faces MathResearch.ThirdParty.Augmented.transposeChain MathResearch.ThirdParty.Augmented.differential_transpose MathResearch.ThirdParty.Augmented.transposeChain_inverse
-/
import «third-party-claims».AugmentedBoundarySquared
import Mathlib.Data.Finset.Preimage

namespace MathResearch.ThirdParty.Augmented
noncomputable section
open scoped BigOperators
variable {V W : Type*} [Fintype V] [DecidableEq V] [Fintype W] [DecidableEq W]

instance (K : Complex V) (k : ℕ) : Fintype (Face K k) := Fintype.ofFinite _

theorem boundary_extend (K : Complex V) (k : ℕ) (c : Face K (k + 1) → ZMod 2)
    (T : Face K k) : boundary (extend K (k + 1) c).val T.val =
      ∑ S : Face K (k + 1), if T.val ⊆ S.val then c S else 0 := by
  classical
  let f := fun v : V => if v ∈ T.val then (0 : ZMod 2) else
    (extend K (k + 1) c).val (insert v T.val)
  have good (v : V) (hv : f v ≠ 0) :
      insert v T.val ∈ K.faces ∧ (insert v T.val).card = k + 1 := by
    by_contra h
    exact hv (by simp [f, extend, h])
  change (∑ v : V, f v) = _
  apply Finset.sum_bij_ne_zero (fun v _ hv => ⟨insert v T.val, good v hv⟩)
  · intro v _ _; exact Finset.mem_univ _
  · intro v _ hv w _ hw he
    have hv' : v ∉ T.val := by intro h; exact hv (by simp [f, h])
    have hw' : w ∉ T.val := by intro h; exact hw (by simp [f, h])
    have hval := congrArg Subtype.val he
    change insert v T.val = insert w T.val at hval
    have : v ∈ insert w T.val := hval ▸ Finset.mem_insert_self v T.val
    simpa [hv'] using this
  · intro S _ hS
    have hsub : T.val ⊆ S.val := by
      by_contra hn
      simp [hn] at hS
    obtain ⟨v, hv, he⟩ := Finset.exists_eq_insert_iff.mpr
      ⟨hsub, by rw [T.property.2, S.property.2]⟩
    have hfv : f v = c S := by simp [f, hv, extend, he, S.property]
    have hne : f v ≠ 0 := by simpa [hsub, hfv] using hS
    exact ⟨v, Finset.mem_univ _, hne, Subtype.ext he⟩
  · intro v _ hv
    have hv' : v ∉ T.val := by intro h; exact hv (by simp [f, h])
    simp [f, hv', extend, good v hv, Finset.subset_insert]

def InRange (e : V ↪ W) (T : Finset W) : Prop :=
  ∀ w ∈ T, ∃ v, e v = w

def push (e : V ↪ W) (c : Coeff V) : Coeff W := by
  classical
  exact fun T => if InRange e T then c (T.preimage e e.injective.injOn) else 0

omit [Fintype V] [Fintype W] in
theorem preimage_insert (e : V ↪ W) (v : V) (T : Finset W) :
    (insert (e v) T).preimage e e.injective.injOn =
      insert v (T.preimage e e.injective.injOn) := by
  ext x
  simp [Finset.mem_preimage, e.injective.eq_iff]

omit [Fintype V] [DecidableEq V] [Fintype W] in
theorem inRange_insert (e : V ↪ W) (v : V) (T : Finset W) :
    InRange e (insert (e v) T) ↔ InRange e T := by
  simp [InRange]

theorem boundary_push (e : V ↪ W) (c : Coeff V) :
    boundary (push e c) = push e (boundary c) := by
  classical
  funext T
  by_cases hT : InRange e T
  · have hout (w : W) (hw : w ∉ Finset.univ.image e) :
        (if w ∈ T then 0 else push e c (insert w T)) = 0 := by
      have hr : ¬ InRange e (insert w T) := by
        intro h
        obtain ⟨v, hv⟩ := h w (Finset.mem_insert_self w T)
        exact hw (Finset.mem_image.mpr ⟨v, Finset.mem_univ _, hv⟩)
      simp [push, hr]
    calc
      boundary (push e c) T =
          ∑ w ∈ Finset.univ.image e, if w ∈ T then 0 else push e c (insert w T) := by
        symm
        apply Finset.sum_subset (Finset.subset_univ _)
        intro w _ hw
        exact hout w hw
      _ = ∑ v : V, if e v ∈ T then 0 else push e c (insert (e v) T) := by
        rw [Finset.sum_image]
        intro x _ y _ h
        exact e.injective h
      _ = push e (boundary c) T := by
        simp only [push, hT, ↓reduceIte, boundary]
        apply Finset.sum_congr rfl
        intro v _
        simp [inRange_insert, hT, preimage_insert, Finset.mem_preimage]
  · have hi (w : W) : ¬ InRange e (insert w T) := by
      intro h
      exact hT (fun x hx => h x (Finset.mem_insert_of_mem hx))
    simp [boundary, push, hT, hi]

omit [Fintype V] [DecidableEq V] [Fintype W] [DecidableEq W] in
theorem map_preimage (e : V ↪ W) (T : Finset W) (hT : InRange e T) :
    (T.preimage e e.injective.injOn).map e = T := by
  ext w
  simp only [Finset.mem_map, Finset.mem_preimage]
  constructor
  · rintro ⟨v, hv, rfl⟩; exact hv
  · intro hw
    obtain ⟨v, rfl⟩ := hT w hw
    exact ⟨v, hw, rfl⟩

omit [Fintype V] [DecidableEq V] [Fintype W] [DecidableEq W] in
theorem push_supported (e : V ↪ W) (K : Complex V) (L : Complex W)
    (he : ∀ S ∈ K.faces, S.map e ∈ L.faces) (k : ℕ) (c : Coeff V)
    (hc : Supported K k c) : Supported L k (push e c) := by
  intro T hT
  classical
  by_cases hr : InRange e T
  · simp only [push, hr, ↓reduceIte]
    apply hc
    have hmap := map_preimage e T hr
    rcases hT with hT | hT
    · left
      intro h
      exact hT (hmap ▸ he _ h)
    · right
      intro h
      apply hT
      rw [← hmap, Finset.card_map, h]
  · simp [push, hr]

def pushLinear (e : V ↪ W) : Coeff V →ₗ[ZMod 2] Coeff W where
  toFun := push e
  map_add' := by
    intro c d
    funext T
    classical
    by_cases hT : InRange e T <;> simp [push, hT]
  map_smul' := by
    intro a c
    funext T
    classical
    by_cases hT : InRange e T <;> simp [push, hT]

def chainMap (e : V ↪ W) (K : Complex V) (L : Complex W)
    (he : ∀ S ∈ K.faces, S.map e ∈ L.faces) (k : ℕ) :
    chains K k →ₗ[ZMod 2] chains L k :=
  (pushLinear e).restrict (fun c hc => push_supported e K L he k c hc)

theorem differential_chainMap (e : V ↪ W) (K : Complex V) (L : Complex W)
    (he : ∀ S ∈ K.faces, S.map e ∈ L.faces) (k : ℕ) (c : chains K (k + 1)) :
    differential L k (chainMap e K L he (k + 1) c) =
      chainMap e K L he k (differential K k c) := by
  apply Subtype.ext
  exact boundary_push e c.val

def inclusion (K L : Complex V) (h : K.faces ⊆ L.faces) (k : ℕ) :
    chains K k →ₗ[ZMod 2] chains L k where
  toFun := fun c => ⟨c.val, fun s hs => c.property s (hs.elim
    (fun hn => Or.inl (fun hk => hn (h hk))) Or.inr)⟩
  map_add' := by intros; rfl
  map_smul' := by intros; rfl

theorem differential_inclusion (K L : Complex V) (h : K.faces ⊆ L.faces)
    (k : ℕ) (c : chains K (k + 1)) :
    differential L k (inclusion K L h (k + 1) c) =
      inclusion K L h k (differential K k c) := rfl

theorem chessboard_boundary_coordinate (s N k : ℕ) (c : ChessboardChain s N (k + 1))
    (T : ChessboardFace s N k) :
    boundary (chessboardChainEquiv s N (k + 1) c).val T.val = chessboardBoundary c T := by
  classical
  change boundary (extend (chessboardComplex s N) (k + 1)
    (fun S => c ((chessboardFaceEquiv s N (k + 1)).symm S))).val T.val = _
  have hh := boundary_extend (chessboardComplex s N) k
    (fun S => c ((chessboardFaceEquiv s N (k + 1)).symm S))
    ⟨T.val, T.property.2, T.property.1⟩
  rw [hh]
  simp only [chessboardBoundary, Nat.add_eq_zero_iff, Nat.one_ne_zero, and_false, ↓reduceIte]
  symm
  apply Fintype.sum_equiv (chessboardFaceEquiv s N (k + 1))
  intro S
  rfl

theorem chessboard_differential (s N k : ℕ) (c : ChessboardChain s N (k + 1)) :
    differential (chessboardComplex s N) k (chessboardChainEquiv s N (k + 1) c) =
      chessboardChainEquiv s N k (chessboardBoundary c) := by
  apply (chessboardChainEquiv s N k).symm.injective
  funext T
  simp only [LinearEquiv.symm_apply_apply]
  exact chessboard_boundary_coordinate s N k c T

theorem chessboard_boundary (s N k : ℕ) (c : ChessboardChain s N k) :
    boundary (chessboardChainEquiv s N k c).val =
      (chessboardChainEquiv s N (k - 1) (chessboardBoundary c)).val := by
  cases k with
  | zero =>
    have hb : chessboardBoundary c = 0 := by funext T; simp [chessboardBoundary]
    rw [hb, map_zero]
    exact boundary_empty _ _ (chessboardChainEquiv s N 0 c).property
  | succ k => exact congrArg Subtype.val (chessboard_differential s N k c)

theorem chessboard_cycle_iff (s N k : ℕ) (c : ChessboardChain s N k) :
    chessboardBoundary c = 0 ↔ boundary (chessboardChainEquiv s N k c).val = 0 := by
  rw [chessboard_boundary]
  constructor
  · intro h; simp [h]
  · intro h
    apply (chessboardChainEquiv s N (k - 1)).injective
    rw [map_zero]
    exact Subtype.ext h

omit [Fintype V] [DecidableEq V] [Fintype W] [DecidableEq W] in
theorem push_apply_map (e : V ↪ W) (c : Coeff V) (S : Finset V) :
    push e c (S.map e) = c S := by
  classical
  have hr : InRange e (S.map e) := by
    intro w hw
    obtain ⟨v, _, rfl⟩ := Finset.mem_map.mp hw
    exact ⟨v, rfl⟩
  simp [push, hr, Finset.preimage_map]

omit [Fintype V] [DecidableEq V] [Fintype W] [DecidableEq W] in
theorem push_injective (e : V ↪ W) : Function.Injective (push e) := by
  intro c d h
  funext S
  simpa only [push_apply_map] using congrFun h (S.map e)

omit [Fintype V] [DecidableEq V] [Fintype W] [DecidableEq W] in
theorem push_equiv (e : V ≃ W) (c : Coeff V) (T : Finset W) :
    push e.toEmbedding c T = c (T.map e.symm.toEmbedding) := by
  classical
  have hr : InRange e.toEmbedding T := fun w _ => ⟨e.symm w, e.apply_symm_apply w⟩
  have hpre : T.preimage e.toEmbedding e.injective.injOn = T.map e.symm.toEmbedding := by
    ext v
    simp [Finset.mem_preimage]
  simp only [push, hr, ↓reduceIte]
  rw [hpre]

omit [Fintype V] [DecidableEq V] [Fintype W] [DecidableEq W] in
theorem push_equiv_inverse (e : V ≃ W) (c : Coeff V) :
    push e.symm.toEmbedding (push e.toEmbedding c) = c := by
  funext S
  rw [push_equiv, push_equiv]
  congr 1
  ext v
  simp

theorem transpose_faces (s N : ℕ) (S : Finset (Fin s × Fin N))
    (hS : S ∈ (chessboardComplex s N).faces) :
    S.map (Equiv.prodComm (Fin s) (Fin N)).toEmbedding ∈ (chessboardComplex N s).faces := by
  constructor
  · intro x hx y hy hxy
    obtain ⟨a, ha, rfl⟩ := Finset.mem_map.mp hx
    obtain ⟨b, hb, rfl⟩ := Finset.mem_map.mp hy
    exact congrArg Prod.swap (hS.2 ha hb hxy)
  · intro x hx y hy hxy
    obtain ⟨a, ha, rfl⟩ := Finset.mem_map.mp hx
    obtain ⟨b, hb, rfl⟩ := Finset.mem_map.mp hy
    exact congrArg Prod.swap (hS.1 ha hb hxy)

def transposeChain (s N k : ℕ) :
    chains (chessboardComplex s N) k →ₗ[ZMod 2] chains (chessboardComplex N s) k :=
  chainMap (Equiv.prodComm (Fin s) (Fin N)).toEmbedding
    (chessboardComplex s N) (chessboardComplex N s) (transpose_faces s N) k

theorem differential_transpose (s N k : ℕ) (c : chains (chessboardComplex s N) (k + 1)) :
    differential (chessboardComplex N s) k (transposeChain s N (k + 1) c) =
      transposeChain s N k (differential (chessboardComplex s N) k c) :=
  differential_chainMap _ _ _ _ _ _

theorem transposeChain_inverse (s N k : ℕ) (c : chains (chessboardComplex s N) k) :
    transposeChain N s k (transposeChain s N k c) = c := by
  apply Subtype.ext
  exact push_equiv_inverse (Equiv.prodComm (Fin s) (Fin N)) c.val

end
end MathResearch.ThirdParty.Augmented

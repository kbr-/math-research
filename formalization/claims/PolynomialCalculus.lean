/-
Claim: def:ordinary-polynomial-proof-foundations
Kind: interface
Source: https://kbr.is-a.dev/math-research/#ordinary-polynomial-proof-foundations
Scope: Ordinary polynomial PC and degree-truncated NS interfaces over a field, with Boolean, weak unary, functional unary, and binary compact bases. Natural total degree assigns degree zero to zero. No PC=NS assertion is made. Finite-variable applications instantiate V by a finite type; the core also permits infinite variable types.
Declarations: MathResearch.PolynomialCalculus.Derives MathResearch.PolynomialCalculus.degreeSpace MathResearch.PolynomialCalculus.pcSpace MathResearch.PolynomialCalculus.nsSpace MathResearch.PolynomialCalculus.booleanBase MathResearch.PolynomialCalculus.unaryBase MathResearch.PolynomialCalculus.functionalUnaryBase MathResearch.PolynomialCalculus.compactBitBase MathResearch.PolynomialCalculus.Derives.degree_le MathResearch.PolynomialCalculus.Derives.mono MathResearch.PolynomialCalculus.mem_pcSpace MathResearch.PolynomialCalculus.nsSpace_le_degreeSpace MathResearch.PolynomialCalculus.degreeSpace_eq_restrictTotalDegree MathResearch.PolynomialCalculus.nsSpace_mono MathResearch.PolynomialCalculus.nsSpace_generator
-/
import Mathlib.Algebra.MvPolynomial.CommRing
import Mathlib.LinearAlgebra.Span.Basic
import Mathlib.Algebra.Field.ZMod
import Mathlib.RingTheory.MvPolynomial.Basic

namespace MathResearch.PolynomialCalculus
noncomputable section
open MvPolynomial
open scoped BigOperators
variable {K V : Type*} [Field K]

abbrev Poly (K V : Type*) [Field K] := MvPolynomial V K

/-- A finite proof tree using only primitive ordinary PC rules. Shared previous
lines may be reused; joining trees represents concatenating their derivations. -/
inductive Derives (F : Set (Poly K V)) (B : ℕ) : Poly K V → Prop
  | zero : Derives F B 0
  | hyp {f} : f ∈ F → f.totalDegree ≤ B → Derives F B f
  | add {f g} : Derives F B f → Derives F B g → Derives F B (f + g)
  | smul (a : K) {f} : Derives F B f → Derives F B (a • f)
  | mul_var (v : V) {f} : Derives F B f → (X v * f).totalDegree ≤ B →
      Derives F B (X v * f)

theorem Derives.degree_le {F : Set (Poly K V)} {B : ℕ} {f : Poly K V}
    (h : Derives F B f) : f.totalDegree ≤ B := by
  induction h with
  | zero => simp
  | hyp _ h => exact h
  | add _ _ ih jh => exact (totalDegree_add _ _).trans (max_le ih jh)
  | smul a _ ih => exact (totalDegree_smul_le a _).trans ih
  | mul_var _ _ h _ => exact h

theorem Derives.mono {F G : Set (Poly K V)} {B C : ℕ} {f : Poly K V}
    (h : Derives F B f) (hFG : F ⊆ G) (hBC : B ≤ C) : Derives G C f := by
  induction h with
  | zero => exact .zero
  | hyp hf hd => exact .hyp (hFG hf) (hd.trans hBC)
  | add _ _ ih jh => exact .add ih jh
  | smul a _ ih => exact .smul a ih
  | mul_var v _ hd ih => exact .mul_var v ih (hd.trans hBC)

def degreeSpace (B : ℕ) : Submodule K (Poly K V) where
  carrier := {f | f.totalDegree ≤ B}
  zero_mem' := by simp
  add_mem' := fun hf hg => (totalDegree_add _ _).trans (max_le hf hg)
  smul_mem' := fun a _ hf => (totalDegree_smul_le a _).trans hf

theorem degreeSpace_eq_restrictTotalDegree (B : ℕ) :
    degreeSpace (K := K) (V := V) B = restrictTotalDegree V K B := by
  ext f
  exact (mem_restrictTotalDegree V B f).symm

def pcSpace (F : Set (Poly K V)) (B : ℕ) : Submodule K (Poly K V) where
  carrier := {f | Derives F B f}
  zero_mem' := .zero
  add_mem' := .add
  smul_mem' := fun a _ h => .smul a h

@[simp] theorem mem_pcSpace (F : Set (Poly K V)) (B : ℕ) (f : Poly K V) :
    f ∈ pcSpace F B ↔ Derives F B f := Iff.rfl

/-- Each ordinary axiom multiple is charged separately, before cancellation. -/
def nsSpace (F : Set (Poly K V)) (B : ℕ) : Submodule K (Poly K V) :=
  Submodule.span K {p | ∃ f ∈ F, ∃ q : Poly K V, p = q * f ∧ p.totalDegree ≤ B}

theorem nsSpace_le_degreeSpace (F : Set (Poly K V)) (B : ℕ) :
    nsSpace F B ≤ degreeSpace B := by
  apply Submodule.span_le.mpr
  rintro p ⟨f, _, q, _, hd⟩
  exact hd

theorem nsSpace_mono {F G : Set (Poly K V)} {B C : ℕ}
    (hFG : F ⊆ G) (hBC : B ≤ C) : nsSpace F B ≤ nsSpace G C := by
  apply Submodule.span_mono
  rintro p ⟨f, hf, q, heq, hd⟩
  exact ⟨f, hFG hf, q, heq, hd.trans hBC⟩

theorem nsSpace_generator {F : Set (Poly K V)} {B : ℕ} {f q : Poly K V}
    (hf : f ∈ F) (hd : (q * f).totalDegree ≤ B) : q * f ∈ nsSpace F B :=
  Submodule.subset_span ⟨f, hf, q, rfl, hd⟩

def booleanBase : Set (Poly K V) := {f | ∃ v, f = X v ^ 2 - X v}

def unaryBase (m n : ℕ) : Set (Poly K (Fin m × Fin n)) :=
  booleanBase ∪ {f | ∃ i, f = (∑ j : Fin n, X (i, j)) - 1} ∪
    {f | ∃ i i' j, i ≠ i' ∧ f = X (i, j) * X (i', j)}

def functionalUnaryBase (m n : ℕ) : Set (Poly K (Fin m × Fin n)) :=
  unaryBase m n ∪ {f | ∃ i j j', j ≠ j' ∧ f = X (i, j) * X (i, j')}

def compactBitBase (m ℓ : ℕ) : Set (Poly (ZMod 2) (Fin m × Fin ℓ)) :=
  booleanBase ∪ {f | ∃ i i' : Fin m, i < i' ∧
    f = ∏ t : Fin ℓ, (1 + X (i, t) + X (i', t))}

end
end MathResearch.PolynomialCalculus

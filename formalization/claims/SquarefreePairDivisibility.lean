/-
Claim: lem:squarefree-forbidden-pair-certificate
Source: https://kbr.is-a.dev/math-research/#lean-squarefree-forbidden-pair-certificate
Scope: Any squarefree monomial containing an explicitly supplied distinct forbidden pair has an ordinary NS certificate through its cardinality, over F₂.
Declarations: MathResearch.PolynomialCalculus.supportMonomial_pair_factor MathResearch.PolynomialCalculus.supportMonomial_pair_ns
-/
import claims.BooleanReduction
namespace MathResearch.PolynomialCalculus
noncomputable section
open MvPolynomial
open scoped BigOperators
variable {V : Type} [DecidableEq V]

theorem supportMonomial_pair_factor (S : Finset V) (x y : V)
    (hx : x ∈ S) (hy : y ∈ S) (hxy : x ≠ y) :
    supportMonomial S = supportMonomial ((S.erase x).erase y) *
      ((X x : Poly (ZMod 2) V)*X y) := by
  have hy' : y ∈ S.erase x := Finset.mem_erase.mpr ⟨Ne.symm hxy,hy⟩
  calc
    supportMonomial S = X x * supportMonomial (S.erase x) :=
      (Finset.mul_prod_erase S (fun i => (X i : Poly (ZMod 2) V)) hx).symm
    _ = X x * (X y * supportMonomial ((S.erase x).erase y)) :=
      congrArg (fun p => (X x : Poly (ZMod 2) V)*p)
        (Finset.mul_prod_erase (S.erase x) (fun i => (X i : Poly (ZMod 2) V)) hy').symm
    _ = _ := by ring

theorem supportMonomial_pair_ns (F : Set (Poly (ZMod 2) V)) (S : Finset V) (x y : V)
    (hx : x ∈ S) (hy : y ∈ S) (hxy : x ≠ y)
    (hF : (X x : Poly (ZMod 2) V)*X y ∈ F) :
    supportMonomial S ∈ nsSpace F S.card := by
  rw [supportMonomial_pair_factor S x y hx hy hxy]
  apply nsSpace_generator hF
  rw [← supportMonomial_pair_factor S x y hx hy hxy]
  exact supportMonomial_degree S
end
end MathResearch.PolynomialCalculus

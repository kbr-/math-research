/-
Claim: publication aggregate for the bit-PHP preprint, revision 1
Source: https://kbr.is-a.dev/math-research/#entry-2026-09-17-preprint-revision-1
Scope: Import-only module with no declarations of its own. It gathers the formal results cited by revision 1 of the preprint (the exponential theorem, the superpolynomial corollary, the generic proof-size criterion with its PC-level theorem and density form, and the short-proof control) so that one build, one axiom report, and one fresh kernel replay cover all of them and their imports. The listed declarations are proved in the imported modules.
Declarations: MathResearch.bitPHP_exponential MathResearch.bitPHP_exponential_base_two MathResearch.bitPHP_superpolynomial MathResearch.PolynomialCalculus.generic_CNF_subspace_criterion MathResearch.PolynomialCalculus.generic_CNF_density_bound_simple MathResearch.generic_affine_subspace_consequence MathResearch.PolynomialCalculus.no_separated_subspace_of_complementary_pair
-/
import claims.BitPHPExponential
import claims.BitPHPSuperpolynomial
import claims.GenericCNFDensityBound
import claims.ShortProofControl

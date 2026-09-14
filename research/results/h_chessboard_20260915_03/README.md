# H10 and branch handoff

Target: H08–H10, completed in three separately recorded checkpoints. The scope is classical chessboard star-cover combinatorics, exact augmented chain transport, and checked composition with H04/H05. No H12/H13 theorem is assumed or proved here.

## Interfaces (namespace MathResearch.ThirdParty.Augmented)

- firstRowStar a b j lives on Fin (a+1) × Fin b, apex (0,j).
- firstRowStars_cover a b requires a+1≤b; covers all faces, including empty.
- closedStar_subcomplex and closedStar_cone give exact inclusion and insertion closure; firstRowStar_exact a b j k composes H04 to fill every k-cycle in a star.
- star_intersection_faces a b J requires 2≤J.card: common matching iff row0 and all J columns absent.
- smallerBoardEmbedding sends Fin a × Fin (b-J.card) to the ambient board by row successor and inverse remainingColumns enumeration.
- starIntersectionChainEquiv a b J hJ k is an actual all-degree linear equivalence from the smaller board's supported chains to intersection chains; differential_starIntersectionChainEquiv proves compatibility.
- starIntersection_exactAt a b J hJ k transports ExactAt from the smaller board, including k=0. No extra side condition b>|J| is required for this transport.
- proper_star_intersection_vertex a b requires 1≤a and J≠univ; supplies a common vertex, including J empty.
- full_star_intersection_empty a b requires 2≤b: common face iff it is empty.
- firstRowStar_nerve_eq requires 1≤a,2≤b: actual equality with simplexBoundary univ.
- firstRowStar_nerve_exact k requires k+1<b; firstRowStar_nerve_acyclic n requires n<b. Cell count k corresponds to simplicial degree k−1. Top homology is excluded correctly.

## Claims, files, provenance

Classical attributable results are in third-party-claims/ChessboardStarCover.lean, ChessboardStarIntersections.lean, ChessboardStarNerve.lean. Independently reusable project-formulated interfaces are claims/FiniteComplexCover.lean (intersections, vertex-nonempty nerve, cover) and claims/AugmentedSubcomplexRelabeling.lean (support-exhaustive embedding chain equivalence and exactness transfer). All five are indexed, with complete notebook proofs/conventions. No novelty claim is made. Standard generic closed-star lemmas remain in the star-cover file for the parent provenance/splitting audit; no movement was made. Small finite-index and structural extensionality helpers remain local. Existing H08 extend_matching was exposed unchanged for H09 reuse.

Lean failures in this cycle concerned proof goal ordering, local-coordinate elaboration and structural equality only; no mathematical correction was needed. Full verification prints all theorem types and trusted axioms and is retained in verification.txt, with raw session logs archived. No push, main modification, subagent or out-of-scope formalization was performed.

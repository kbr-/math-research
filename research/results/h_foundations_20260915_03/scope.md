# H01–H03 assignment and scope

Assigned targets: H01, H02, H03 of BIT_PHP_FORMALIZATION_ROUTE.md, in that order.
No proof of H04–H13 or of the filling proposition H is part of this assignment.

H01 supplies finite augmented F₂ chains on downward-closed finite face families,
including the empty face, graded support, and a linear boundary. H02 proves
the boundary squares to zero. H03 supplies inclusions and injective relabeling,
including transpose and compatibility with the existing chessboard interface.

Representation choice: coefficient functions on all finite vertex subsets, with
support on k-element faces for k-cell chains (simplicial degree k−1). The boundary
at T sums coefficients on insertions of one vertex outside T. This automatically
includes augmentation and is zero on chains supported on the empty face.
Existing exact-face ChessboardChain functions must be linked by an explicit,
checked extension-by-zero bridge before downstream use.

Mathlib provides finite sums, finite sets, F₂, modules, and linear maps. No
topology theorem or filling existence is assumed. Boundary cases: empty vertex
type, empty-face-only complex, cell-count zero, vertex augmentation, and edges.

Initial policy/source reading occurred before the timing session was started;
subsequent context review and all proof development are instrumented.

H03 final scope: all support-preserving injective chain maps, same-vertex inclusions, inverse relabelings and transpose, and the exact original boundary bridge in every cell count including zero. H01 bf6b303 and H02 36ca623 are reused. H04–H13 remain separate assignments. Directory provenance review is deferred under the user’s coordination instruction.

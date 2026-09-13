# Old local targets and a complete matching-tree module certificate

The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-13-weighted-module-design-extension)
applies the existing old-consequence theorem to purely old source-local targets.
With the explicit functional PHP strengthening, L>=4, and N>=12L-1, a target H
of degree at most four has a base NS certificate through its own degree.
This is not a global design-extension theorem.

The computation refines the earlier exponential assignment-tree obstruction.
It gives an ordinary formal identity for the old target one using source OR
relations linear in selectors, with constant external gate coefficients.
The weak PHP base suffices for these refutations: no same-row exclusions are used.
There are Theta(n*n!) retained literal blocks. The polynomial-family regime
remains open, and the existing polynomial literal-family theorem is unaffected.

## Full local witnesses

The file <code>matching-tree-module-certificates.jsonl</code> begins with 26
complete local templates over F2, at h=1,2. Each saves its old input slots,
products, complete companion lists, prefix coefficients, actual fresh-variable
layout, target, and every nonzero NS axiom/cofactor pair.

Edge templates use k=0..6, with old prefix variables 0..k-1 and new literal x_k.
The parent A has inputs 0,1-x_0,...,1-x_(k-1), and C adds 1-x_k. The target
C-x_k*A has witness degree 4h+1, or 2h+1 for the constant parent.

Collision templates use k=0..5 rest variables. Old slots 0,1 are x,y, and
2..k+1 are the rest coordinates. A has inputs 0 and their complements;
C has inputs 1-x,1-y followed by A's inputs. Its target C-xy*A has witness
degree 4h+2, or 2h+2 for the constant rest. This is a genuine source
comparison after the standard collision-clause normalizer.

At k=0, A is the false constant with product one; it has no fresh variables
and no retained formal selector. The zero input is recorded explicitly.
This is not an invalid all-zero genuine block in the degree embedding.

All 26 ordinary polynomial identities pass. Omitting their field terms changes
the identity in every case. The general formulas and degree proofs are in the
notebook; the finite tests are not minimum-degree computations.

## Global family and certificate

For a registered nonempty cell set S, use the proper formula

    FALSE OR (OR of NOT p_e for e in S).

The product has inputs 0 followed by 1-x_e for the cells in canonical order.
Each genuine product has weight 2h. The empty set is the constant one.
Follow all choices of a hole for each next pigeon, stopping at the first
collision, and include the matching-rest helpers used at bad leaves.

| n | Internal matching nodes | Blocks including rest helpers | Edge modules | Collision modules |
| ---: | ---: | ---: | ---: | ---: |
| 2 | 5 | 12 | 10 | 6 |
| 3 | 16 | 63 | 48 | 33 |
| 4 | 65 | 360 | 260 | 196 |
| 6 | 1,957 | 17,208 | 11,742 | 9,786 |

Every case is checked at h=1 and h=2. The complete NS witness ceilings are
six and ten respectively. Local-module coefficients are one in F2. Row and
collision base coefficients are collected sums of formal selectors or constants.
The sum of all recorded formal axiom multiples is verified to be exactly one.

The largest case has 225,306 actual old/coefficient variables. It is represented
by complete local polynomial certificates and injective variable maps; global
expansion would duplicate each template thousands of times. No coefficient data
is truncated or left only in temporary files.

The asymptotic degree separation uses the proved tree formulas and existing
base degree/design theorems. These small boards do not numerically establish
that separation or test the polynomial-family research goal.

## Polynomial and variable encoding

Polynomials use [coefficient, [variable_index,...]] terms, with repeated
indices for powers and residues in F2. All identities use ordinary polynomials.

A global case has n*pigeons old variables, indexed by row*n+column.
There are two distinct coordinate spaces:

- Formal selectors have slots old_variable_count+block_id and weight 2h.
  These coordinates appear in formal targets and collected base cofactors.
- Actual coefficient variables start at each block's recorded coefficient_start.
  There are h consecutive rows, each of arity 1+number_of_cells. Slot zero
  is the false leaf; later slots follow the recorded cell order.

The two spaces may reuse integer labels; they are not one polynomial ring.
Substitution replaces each formal selector by its registered genuine product.

Each global module references a named local template and supplies a complete
local-actual-to-global-actual variable map. The checker verifies injectivity and
alignment of every input slot, including coefficient-row permutations when a
collision pair is moved to the front of a local tuple. Rename the template's
axioms and cofactors by that map, then add the listed original PHP base terms.
This reconstructs a full concrete NS certificate.

## Satisfiable and omission controls

At four pigeons and four holes, each h case has 192 blocks and 264 modules.
There are 24 surviving perfect-matching leaves. The verified target is one
minus the sum of those selectors, not one.

The identity matching gives all old coordinates: listed old_x_ones are one
and every other old variable is zero. Listed actual_coefficient_ones are one
and all other actual coefficients are zero. The first coefficient row chooses
one mismatching input whenever present; a fully matching tuple uses zero rows.
Products are evaluated from these assignments and saved in block order.

Both controls satisfy the old row/collision equations and all retained
companions, and make the surviving-frontier target zero. All field/Boolean
equations hold since all coordinates are bits. Every global case also verifies
that omitting one collision module changes the formal certificate identity.

## Reproduction and provenance

Use a new output path from the repository root:

~~~bash
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -std=c++17 -O2 -Wall -Wextra -pedantic \
  research/tools/check_weighted_source_modules.cpp \
  -o /tmp/check_weighted_source_modules
./compute.sh run TURN --threads 1 -- \
  /tmp/check_weighted_source_modules --out NEW_CERTIFICATES.jsonl
~~~

No random seed or dependency installation is used. Existing output paths are
refused. The source and shared exact-polynomial headers, this description, and
the complete result file are pinned by <code>provenance.json</code>. Timing and
full command outputs are preserved in the matching session archive.

# Collision-pruned compact bit assignment trees

The [full notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-13-compact-bit-assignment-tree)
applies the existing assignment-tree theorem to compact bit PHP and prunes
each branch at its first completed label collision.
The new leaf certificate costs 2h+ell, and the existing split costs 4h+1.
Thus 2h>=ell gives an NS refutation through 4h+1.

There are exactly 2(n-1) A_n blocks, where A_n=sum_(k=0)^n (n)_k.
The companion count is
2[ell(n-1) B_n + ((ell-1)n+1) A_n], with B_n=(n-1)A_n+1.
Coefficient count is h times companion count. Inventory is factorial,
not polynomial in n. The result demonstrates a limitation of the current
inventory-independent degree band, not a polynomial-size Frege proof.

## Complete finite factored certificates

<code>pruned-bit-trees.jsonl</code> retains two complete four-hole trees:

| Pigeons | Internal nodes | Blocks | Companions | Collision leaves | Open leaves |
| --- | ---: | ---: | ---: | ---: | ---: |
| 5 | 195 | 390 | 3,002 | 196 | 0 |
| 4 | 123 | 246 | 1,610 | 100 | 24 |

Each nonempty prefix is a block with all its mismatch inputs. Bits are
queried in pigeon-row order, least significant bit first. A branch stops
at a completed collision, or when all pigeons are assigned.
The input at position i is x_i plus the assigned prefix bit, over F2.

For each collision leaf, the output retains the repeated rows, their common
label, the complete equality polynomial, every old prefix cofactor in its
telescoping identity, and the associated leaf companion input indices.
The leaf certificate is

~~~text
P_sigma = P_sigma E_(i,i') + sum_t L_t (E_(sigma,it) + E_(sigma,i't)),
L_t = product_(s<t) (1+b_is+b_i's).
~~~

The checker verifies every old leaf identity exactly. Its mask products in
these identities use disjoint bit positions, so no Boolean reduction hides
an ordinary-degree cost. Accuracy h=1 or h=2 gives leaf costs 4 or 6.

Every internal node uses the existing general
[TREE-split witness](https://kbr-.github.io/math-research/#assignment-tree-split).
The full formal sum is collected with integer signs, giving one minus
the open-frontier sum. The generic witness was not re-expanded or rerun;
its full formula and prior exact checks are already in the notebook.
The two accuracies give total NS costs 5 and 9.

The satisfiable four-pigeon control has 24 permutation leaves. The saved
identity permutation and first-success coefficient assignments satisfy
the target with that frontier; omitting the frontier would give value one.
These cases test the factored construction and ledger, not an asymptotic
PHP degree separation.

## Namespaces and reconstruction

Node zero is the root constant one, with no ENS block. Nonroot node IDs
identify independent products. A node record contains its prefix length,
prefix-value mask, both children or -1, the earlier collision row or -1,
and its coefficient offset per unit of h.

At accuracy h, factor row u and input i of a depth-k node have variable ID

~~~text
old_variables + h*coefficient_offset_per_h + u*k + i.
~~~

This gives all coefficient variables disjoint namespaces. Reconstruct
P_sigma as product_u (1-sum_i r_(sigma,u,i) g_(sigma,i)).
Every nonroot product has original degree 2h and every companion degree
2h+1. The field equations are Booleanity for all variables.

Old polynomial lists use integer monomial masks with coefficient one in F2.
The leaf input indices are positions within the prefix, hence also old
variable IDs. Case summaries give all counts and both NS ceilings.
The target record gives its constant one and all negatively signed open
frontier node IDs.

In the satisfiable case, each node also gives its first nonzero mismatch
input on the saved old point, or -1 if none. Set that coefficient in factor
row zero to one and all others to zero; for -1 set them all to zero.
This specifies a complete satisfying coefficient assignment for either h.

## Reproduction

~~~bash
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -O2 -std=c++17 -Wall -Wextra \
  research/tools/check_compact_bit_tree.cpp -o /tmp/math-compact-bit-tree
./compute.sh run TURN --threads 1 -- \
  /tmp/math-compact-bit-tree --out NEW_OUTPUT.jsonl
~~~

The tool refuses existing outputs and installs no dependency. Compilation
and the single finite run passed on the first attempt. No exponential
large-n tree was constructed. Source, the shared header, this description,
and complete output are pinned by <code>provenance.json</code>.
The timing table and session archive preserve the measured work.

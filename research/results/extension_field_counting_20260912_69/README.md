# Multiplicative-order counting and prime-field coordinate degree

The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-12-extension-field-counting)
contains the full injection proof, exact function-degree argument, coordinate
bound, source equation ledger, and proper-domain scope control.

This cycle read Section 5.1, Theorem 5, and Definition 11 on printed pages 12-13
of Impagliazzo-Mouli-Pitassi, ECCC TR19-024 revision 2. Its exact PDF and text
hashes are preserved by the
[preceding source manifest](../affine_extension_audit_20260912_68/provenance.json).
No further source acquisition or conversion was needed. The full subsequent
proof-rule simulations have not been audited here.

The source operation represents an integer count as a power of a primitive
element of an extension field. Our direct argument uses the unique multilinear
representation on a Boolean cube: each active weight contributes a nonzero
factor to the top coefficient. Decomposing that coefficient in any prime-field
basis leaves some coordinate of the same full degree.

The resulting comparison keeps sparse size, field dimension, and ordinary joint
degree separate. The source product equation has two monomials but degree equal
to its full arity. The bound concerns exact polynomials in old variables and
does not exclude auxiliary ENS implementations with suitable certificates.

The scope control contrasts cells within one column, where collision reduction
can make the encoding affine, with occupancies in separate columns, which are
independent on the product of proper column domains. The latter model argument
does not impose the unsatisfiable full PHP row system.

No numerical run or historical suite repetition was needed. The proof is an
algebraic identity and uniqueness argument. A short outline of the next
selector-only dependency step was also measured in this cycle's mathematics
phase. The timing fragment, source-manifest link, and archived session retain
the exact measurement and provenance scope.

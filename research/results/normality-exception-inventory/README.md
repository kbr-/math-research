# Generic normality exception inventory

An empty set is recorded only when a cited working proof covers every degree. Unresolved entries are **not** empty sets. This inventory does not supply a stopping algorithm.

Scope: dimensions 1–10; odd primes through 97.

| Dimension | Complete empty sets | Unresolved pairs |
|---:|---:|---:|
| 1 | 24 | 0 |
| 2 | 24 | 0 |
| 3 | 24 | 0 |
| 4 | 24 | 0 |
| 5 | 24 | 0 |
| 6 | 24 | 0 |
| 7 | 24 | 0 |
| 8 | 24 | 0 |
| 9 | 0 | 24 |
| 10 | 0 | 24 |

Total: **192 complete**, **48 unresolved**.

Evidence:

- `thm:cube-eight-all-odd-normality`: [Complete dimension-eight normality](https://kbr.is-a.dev/math-research/branches/binary-multiplicity-degree/#entry-2026-10-06-cube-eight-all-degrees) (working_proof).
- `cor:cube-nine-ternary-filter`: [Exception coefficient filter](https://kbr.is-a.dev/math-research/branches/binary-multiplicity-degree/#entry-2026-10-07-cube-exception-coefficient-filter) (working_proof).
- `cor:cube-nine-torsion-families`: [Frobenius cup certificate](https://kbr.is-a.dev/math-research/branches/binary-multiplicity-degree/#entry-2026-10-07-cube-frobenius-cup-certificate) (working_proof).
- `cor:nine-first-bulk-progression`: [First bulk progression](https://kbr.is-a.dev/math-research/branches/binary-multiplicity-degree/#entry-2026-10-08-cube-first-bulk-progression) (working_proof).

For n=9, p=3, certified normal degrees: {"intervals": [[2, 6]], "residue_classes": {"minimum_degree": 7, "modulus": 729, "residues": [50, 68, 124, 181, 218, 349, 367, 368, 386, 517, 554, 611, 667, 685]}}. The complete exception set remains unresolved.

For n=9, p=3, certified normal degrees: {"first_degree": 1120878158380954709673208311740178314035203, "frobenius_families": {"e_min": 1, "e_not_divisible_by": 3, "exponent_offset": 5, "exponent_period": 10862102160, "formula": "d = offset + multiplier * prime^(exponent_offset + exponent_period*j) * e", "j_min": 0, "multiplier": 4612667318440142838161351077120075366400, "offset": 3, "prime": 3}}. The complete exception set remains unresolved.

For n=9, p=3, certified normal degrees: {"intervals": [[2, 7]], "residue_classes": {"minimum_degree": 7, "modulus": 373626052793651569891069437246726104678400, "residues": [7]}}. The complete exception set remains unresolved.

The pairwise machine-readable inventory is in `inventory.json`. Bounds may be reduced according to measured cost, as requested by the user.

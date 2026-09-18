# Cycle 218: refutation degree of the small functional PHP augmented by blocks on dense forms

Session `augmented_php_degree_20260918_218`. Supports the notebook entry
`entry-2026-09-18-augmented-php-degree`.

## Tool

`research/tools/augmented_php_degree.py --N N --d d [--blocks 3,3] [--affine] [--seed s]
[--fake-control] --out FILE`. Base: functional PHP over F_2 on `N+1` rows and `N` holes.
An accuracy-one block with inputs `L_1..L_rho` (dense forms) has fresh Boolean variables
`r_1..r_rho`, product `P = 1 - sum r_j L_j` and companions `L_i P`. Monomials are pairs
(partial matching, set of new variables) of total degree `<= d`, ordered by total degree.
The tool computes the degree-`d` polynomial-calculus closure of the row axioms and the
companions, reports whether it contains 1, and (later runs) the dimension of the closure's
intersection with the old polynomials, by a second elimination that removes the monomials
carrying new variables first. `--fake-control` replaces the companions of a one-input block
by the non-conservative axioms `r = 1`, `r (1 + X_00) = 0`.

## Files

- `degrees.jsonl`, `runs.log`: six holes at degree 3 and 4; eight holes at degree 4
  (first batch; records written before the old-only count was added lack that field).
- `degrees_old_only.jsonl`, `runs_N6_old.log`, `runs_N8_old.log`: the same cases with the
  old-only dimension, the base closures, and the fake control.

- `block_forms_images.jsonl`, `degrees_followup.jsonl`, `runs_followup.log`: reviewer
  follow-ups: the image test of `php_relative_image_check.py` on the exact block forms
  (`research/tools/block_forms_image_check.py`), infeasible at `s = 1, 2` in both systems
  for all four blocks; and the base closure on eight holes with its part of degree at most
  three, 12729 = dim V_3.

## Relation to recorded results

The blocks are the fresh blocks of cycles 167 to 170; the substitution, the dual criterion
and the level-one conservativity conjecture are recorded there. This check is an instance of
that conjecture on the functional PHP base, at one degree of slack (low power).

## Results

Base closures: six holes, degree 3: 2793 of 4873; degree 4: all of 17473 (refutation degree
4); eight holes, degree 4: 143643 of 241993 (refutation degree 5 by the recorded bound).

Eight holes, degree 4: with one block of 3 inputs (uniform half-sets, seeds 1 and 2; affine
half-spaces), one block of 4 inputs, or two blocks of 3 inputs, 1 is not in the closure
(closure dimensions 183680, 198150, 228838). For the blocks with 3 and 4 inputs the old-only
part has dimension 143643, equal to the base closure: fully conservative at degree 4. The
2-input control is conservative (171314, old-only 143643). Six holes, degree 3: conservative
in all cases (old-only 2793), a weak test since companions enter unmultiplied. Fake control:
old-only 4403 against 2793, so the count detects a non-conservative axiom.

## Reproduction

```
python3 research/tools/augmented_php_degree.py --N 8 --d 4 --blocks 3 --out degrees.jsonl
python3 research/tools/augmented_php_degree.py --N 6 --d 3 --blocks 1 --fake-control \
  --out degrees_old_only.jsonl
```

Each eight-hole run takes 30 to 50 seconds and 4 to 7 GB in CPython (bitset elimination on
Python integers); two blocks of three inputs need 6.6 GB.

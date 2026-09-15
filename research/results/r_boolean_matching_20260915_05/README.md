# R14 prerequisite: disjoint coordinate pairs

Completed lem:disjoint-binary-coordinate-pairs, not R14 itself. Full MathJax proof in entry-2026-09-15-lean-disjoint-coordinate-pairs. Actual bitLabelEquiv from R12 is reused. flipColumn changes exactly one coordinate, is a fixed-point-free involution; coordinate_pair_avoiding uses |F∪flip(F)|≤2|F|. Greedy exists_disjoint_coordinate_pairs applies to any finite subset of an arbitrary index type, with exact union cardinality2|S|. coordinatePair_bit_sum isolates the specified bit.

cube_residual_parameters proves both residual-column positivity and N−2t≥2(B−t)−1 under the exact R14 parameter range, including t=0 and t=B. It uses divisibility of2^ell by4 and retains ordinary degreeB/t distinctions. All nine audited public declarations pass with standard axioms only. No custom predicate replaces the required residual design; R10 will supply it next.

Dependencies: checked R12 decoder coordinates, elementary Mathlib finite-set/finite-field arithmetic. No packages installed or versions changed. Failed checks were index substitution/elaboration and arithmetic tactic setup errors; no mathematical counterexample. Complete outputs/timing are archived, with verification.txt canonical. A notebook excerpt read failed transiently during parent integration; the paper and bounded exact notebook source lines were read, and parent confirmed parser recovery afterward.

R14 remains open: actual cube/residual annihilation throughB, coefficient isolation for complete rowLinearSpace and final PC exclusions. Parent retains living-section/route ownership; none were edited. The later post-all-Rxx generalization sweep has not started.

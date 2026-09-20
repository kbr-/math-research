# Cubic conflict-space dimension checks

The notebook entry `entry-2026-09-20-cubic-dimension-barrier` proves the formulas.
This exact binary checker is an independent finite control, not the proof.

```bash
./compute.sh g++ -std=c++20 -O2 research/tools/check_conflict_cubic_dimension.cpp -o /tmp/check_conflict_cubic_dimension
./compute.sh /tmp/check_conflict_cubic_dimension --out /tmp/cubic-dimensions-new.jsonl
```

`dimensions.jsonl` preserves every result: eight three-row tensor spaces for
N=5..12 and two complete exterior conflict spaces for N=5,6 with N+1 rows.
The row basis removes the final hole coordinate using the row-sum relation.
Quadratic generators are same-row pairs, cross-row diagonal pairs and one
cross-row all-ones tensor. The full check wedges every generator with every
basis coordinate and computes exact GF(2) rank. Local tensor checks construct
all three pair modules independently. The bounded ranges are hard-coded.

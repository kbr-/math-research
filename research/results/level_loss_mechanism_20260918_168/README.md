# Rank-dependent fresh-block loss

The [notebook entry](https://kbr.is-a.dev/math-research/#entry-2026-09-18-rank-dependent-fresh-block-loss)
states the finite claims, the witness shape, and the scope. The checker and its encoding are
described in `../fresh_block_conservativity_20260917_167/README.md`; this cycle added three suites.

- `level-loss.jsonl` (`--suite cycle168`): second-level and third-level bases on 2+2 old variables
  with one to three rank-two helpers, and the 3+3 base with one rank-three helper plus membership
  queries for parts of the degree-seven relation. Each record also has `loss_histogram`, mapping
  (least base degree minus D) to the number of new consequences, and `queries`.
- `rank4-helper.jsonl` (`--suite cycle168-rank4`): the 3+3 base with the rank-four helper
  (x1+y1, x2+y2, x3+y3, x1+y2) at degrees 6 and 7.
- `degree-seven-witness.jsonl` (`--suite cycle168-witness`): an explicit ordinary NS identity for
  E(g1g2g3+x1x2x3+y1y2y3) in the extended 3+3 source at degree 7, as one cofactor per generator
  (generators in creation order: x_iA, y_iB, (1+A)E, (1+B)E, g_iG), re-multiplied and verified.
  Variables 0–5 are x1,x2,x3,y1,y2,y3; then a1..a3, b1..b3, e1,e2, s1..s3.

## Reproduction

```bash
./compute.sh --threads 1 --category local_processing \
  g++ -O2 -std=c++17 -Wall -Wextra -Wno-misleading-indentation \
  research/tools/check_fresh_block_conservativity.cpp -o /tmp/math-fresh-block
./compute.sh --threads 1 --timeout 3000 /tmp/math-fresh-block --out /tmp/a.jsonl --suite cycle168
./compute.sh --threads 1 --timeout 5400 /tmp/math-fresh-block --out /tmp/b.jsonl --suite cycle168-rank4
./compute.sh --threads 1 --timeout 3000 /tmp/math-fresh-block --out /tmp/c.jsonl --suite cycle168-witness
```

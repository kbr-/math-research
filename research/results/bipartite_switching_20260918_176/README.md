# Bipartite matching switching lemma: encoding round-trip test

The [notebook entry](https://kbr.is-a.dev/math-research/#entry-2026-09-18-bipartite-switching-lemma)
states and proves the lemma. `encoding-roundtrip.jsonl` records seven exact runs of
`research/tools/check_bipartite_switching_encoding.py`: for a random r-disjunction on the
(n+1) x n board (terms listed in the record, seed given), every partial matching of size n-l is
enumerated, the canonical matching decision tree is built, and for every restriction of height >= s
the trimmed lexicographically first long path is encoded and decoded. Fields: restriction count,
bad count and fraction, `round_trip_failures` (all zero), `sigma_size_range_ok` (ceil(s/2) <= |sigma|
<= 2s), height histogram, the lemma's A, and the bound when A <= 1/2 (vacuous at these sizes).

```bash
./compute.sh --threads 1 python3 research/tools/check_bipartite_switching_encoding.py \
  --n 7 --l 3 --r 3 --s 3 --terms 16 --seed 9 --out /tmp/roundtrip.jsonl
```
The other runs use (n,l,r,s,terms,seed) = (5,2,2,2,8,20260918), (5,2,2,2,12,7), (6,3,2,2,10,20260918),
(6,3,3,3,10,3), (6,3,2,3,14,11), (6,3,3,3,20,5).

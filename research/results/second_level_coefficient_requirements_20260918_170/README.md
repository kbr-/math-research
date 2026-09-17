# Level-one base conservativity checks

The [notebook entry](https://kbr.is-a.dev/math-research/#entry-2026-09-18-level-one-conservativity-conjecture)
lists the cases, the conjecture they support, and the dual reading of the coefficient criterion.

`level-one-bases.jsonl` is the output of suite `cycle170-level-one` of
`research/tools/check_fresh_block_conservativity.cpp` (encoding in
`../fresh_block_conservativity_20260917_167/README.md`). Every record is conservative
(`full_interface_conservative` true, product interface preserved, no new consequences).

```bash
./compute.sh --threads 1 --category local_processing \
  g++ -O2 -std=c++17 -Wall -Wextra -Wno-misleading-indentation \
  research/tools/check_fresh_block_conservativity.cpp -o /tmp/math-fresh-block
./compute.sh --threads 1 --timeout 5400 /tmp/math-fresh-block --out /tmp/l1.jsonl --suite cycle170-level-one
```

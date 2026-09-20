# NS versus PC endpoint control

The updated bounded checker accepts `--pc-rhs C`. After the shared NS calculation,
it reconstructs that right-hand side's complete degree-three NS space and closes
it under multiplication of every degree-at-most-two basis vector by every free
variable, with exact Boolean reduction. New lower-degree pivots join the queue;
higher-degree pivots are never multiplied. The queue is exhausted, not stopped
on the first refutation. This is a finite computed closure, not a stored proof DAG.

```bash
./compute.sh g++ -std=c++20 -O2 research/tools/check_php_rhs_residue.cpp -o /tmp/check_php_rhs_residue
./compute.sh /tmp/check_php_rhs_residue --holes 6 --constraints 5 --seed 1 --pc-rhs 0 --out /tmp/five-PC-new.json
./compute.sh /tmp/check_php_rhs_residue --holes 6 --constraints 6 --seed 1 --pc-rhs 0 --out /tmp/six-PC-new.json
```

Every pre-existing NS/RHS field agrees exactly with the preceding checkpoint's
corresponding report; only `pc_closure` is added. PC is checked for RHS zero only,
not all 64 constants. The initial NS ranks are verified against the independently
assembled leading rank, quadratic rank and fall rank. Original affine elimination
maps and the complete RHS tables remain in each output.

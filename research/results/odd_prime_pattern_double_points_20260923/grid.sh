#!/bin/bash
# Maximal-rank grid for the pattern algebra on general R x L boards (induction runs over R at fixed L).
D=$(dirname "$0")
for L in 4 5 6 7; do for R in 3 4 5 6 7 8 9; do
  python3 $D/pieces_P.py --R $R --L $L --Mmax 0 --out $D/grid/pieces_R${R}_L${L}.json | grep uniform
done; done

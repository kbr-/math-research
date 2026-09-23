#!/bin/bash
# Small row counts at larger label counts: does maximal rank at R = 4, 5, 6 persist as L grows?
D=$(dirname "$0")
for RL in "4 8" "4 9" "5 8" "5 9" "5 10" "6 9" "6 10"; do set -- $RL
  python3 $D/pieces_P.py --R $1 --L $2 --Mmax 0 --out $D/grid/pieces_R$1_L$2.json | grep uniform
done

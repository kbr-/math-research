#!/bin/bash
# Reruns of the defective small boards with other seeds: true defects persist, unlucky F_3 draws do not.
D=$(dirname "$0")
for RL in "3 5" "3 6" "4 4" "4 7" "5 4"; do set -- $RL; for s in 2 3 4; do
  python3 $D/pieces_P.py --R $1 --L $2 --Mmax 0 --seed $s --out $D/grid/pieces_R$1_L$2_s$s.json | grep uniform
done; done

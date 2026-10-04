#!/bin/sh
# Local lengths of (F, m1) and (F, m1) : k at a two-pair point, for the recorded d = 3 plane (control: 44 and 8 from
# the recorded collision totals) and a fresh d = 4 plane (cycle bmd-20261009-kgv; conj:cube-two-pair-colon-excess).
# Env: OUT (directory), BIN (directory with the compiled plane_minors).
# Usage: env OUT=dir BIN=dir sh research/tools/bmd_two_pair_length_series.sh
set -e
python3 research/tools/bmd_two_pair_length.py research/results/bmd-20261009-dh/plane-d3-k.m2 32003 "$OUT/d3.sing"
echo "d = 3:"; Singular -q "$OUT/d3.sing"
[ -f "$OUT/plane-d4-p32003.m2" ] || "$BIN/plane_minors" 32003 4 1 "$OUT/plane-d4-p32003.m2"
python3 research/tools/bmd_two_pair_length.py "$OUT/plane-d4-p32003.m2" 32003 "$OUT/d4.sing"
echo "d = 4:"; Singular -q "$OUT/d4.sing"

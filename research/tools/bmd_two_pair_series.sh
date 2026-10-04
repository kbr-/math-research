#!/bin/sh
# Tangent cones of F, m1 and k at a two-pair and a triple point of a random plane, at one degree d (cycle
# bmd-20261009-kgu): bmd_plane_minors p d seed -> stripped minors; the file is cut to the two last minors (F, m1),
# extraK and the collision forms, since Macaulay2 parses each long sum with roughly quadratic cost and the 29 minors
# at d = 4 took minutes; bmd_two_pair_local.m2 -> orders and cones.
# Env: P (prime), D (degree), SEED, OUT (directory), BIN (directory with the compiled plane_minors).
# Usage: env P=32003 D=4 SEED=1 OUT=dir BIN=dir sh research/tools/bmd_two_pair_series.sh
set -e
[ -f "$OUT/plane-d$D-p$P.m2" ] || "$BIN/plane_minors" "$P" "$D" "$SEED" "$OUT/plane-d$D-p$P.m2"   # reuse a finished plane
awk '/^minorList = \{/ {print; inlist = 1; next}
     inlist && /^\};/ {sub(/,$/, "", prev); print prevprev; print prev; print; inlist = 0; next}
     inlist {prevprev = prev; prev = $0; next}
     {print}' "$OUT/plane-d$D-p$P.m2" > "$OUT/plane-d$D-p$P-cut.m2"
M2 --script research/tools/bmd_two_pair_local.m2 "$OUT/plane-d$D-p$P-cut.m2" "$P" 0

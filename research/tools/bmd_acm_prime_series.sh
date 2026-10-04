#!/bin/sh
# The first-step ACM comparison at d = 3 at one prime (cycle bmd-20261009-kgp; check:cube-first-step-acm-degree-dichotomy,
# ex:cube-first-step-not-acm-three-mod-p).  Steps: (1) bmd_plane_minors p 3 seed -> the stripped minors F, m1 and k on a random
# plane; (2) bmd_plane_polar_colon.m2 -> lengths of the complete intersection and the colon (F, m1) : k, and the colon section's
# Betti numbers; (3) bmd_first_step_kernel 3 p seed 53..57 -> dim (T_3)_c (for c >= 55 subtract the (A, G) defect).
# Env: P (prime), SEED, OUT (directory), BIN (directory with the compiled plane_minors and fsk).
# Usage: env P=65521 SEED=2 OUT=dir BIN=dir sh research/tools/bmd_acm_prime_series.sh
set -e
"$BIN/plane_minors" "$P" 3 "$SEED" "$OUT/plane-d3-k-p$P.m2"
M2 --script research/tools/bmd_plane_polar_colon.m2 "$OUT/plane-d3-k-p$P.m2" "$P"
"$BIN/fsk" 3 "$P" "$SEED" 53 54 55 56 57

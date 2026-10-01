#!/bin/sh
# Build research/tools/bmd_eval_kernel.cpp (6 October 2026) into the ignored scratch binary path given as $1.
# Winograd's fast multiplication is disabled by raising its thresholds: its temporaries took a 4.56 GB system to a
# 7.67 GB peak (cycle bmd-20261006-b), which the 10 GB budget cannot afford for the larger systems.
set -e
out=${1:?output path}
g++ -O3 -march=native -fopenmp -D__FFLASFFPACK_WINOTHRESHOLD=100000000 -D__FFLASFFPACK_WINOTHRESHOLD_FLT=100000000 \
    -D__FFLASFFPACK_WINOTHRESHOLD_BAL=100000000 -D__FFLASFFPACK_WINOTHRESHOLD_BAL_FLT=100000000 \
    $(pkg-config --cflags fflas-ffpack) research/tools/bmd_eval_kernel.cpp -o "$out" -lgivaro -lflint -lgmpxx -lgmp -lopenblas

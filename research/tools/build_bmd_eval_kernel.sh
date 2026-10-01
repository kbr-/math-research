#!/bin/sh
# Build research/tools/bmd_eval_kernel.cpp (6 October 2026) into the ignored scratch binary path given as $1.
set -e
out=${1:?output path}
g++ -O3 -march=native -fopenmp $(pkg-config --cflags fflas-ffpack) research/tools/bmd_eval_kernel.cpp -o "$out" \
    -lgivaro -lgmpxx -lgmp -lopenblas

#!/bin/bash
# Runs the direct-sum kernel on each chain input; prints "<case> <kernel JSON>" per line.  Usage: run_chains.sh BIN INDIR
set -e
for f in "$2"/chain_*.in; do
  c=$(basename "$f" .in); OMP_NUM_THREADS=12 "$1" < "$f" > "$2/$c.out"; echo "$c $(tail -1 "$2/$c.out")"
done

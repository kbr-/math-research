#!/bin/sh
# Exact elimination series for conj:cube-triple-window-full-rank (cycle bmd-20261009-kfx, 9 October 2026).
# For each m in $MS: export the ten minors with the Rabinowitsch generator (bmd_triple_window_export_m.gp) and run msolve over
# Q for the reduced Groebner basis; {1} means full rank at every admissible point for that m. Prints per-m export and msolve
# wall times. Usage: env MS="10 11 12" OUT=research/results/bmd-20261009-kfx THREADS=8 sh bmd_triple_window_exact_series.sh
set -e
for m in $MS; do
  t0=$(date +%s)
  rm -f "$OUT/triple-minors-m$m.ms"  # PARI's write appends: a stale file would be doubled
  env M=$m OUT="$OUT" gp -q research/tools/bmd_triple_window_export_m.gp
  t1=$(date +%s)
  msolve -g 2 -t "$THREADS" -f "$OUT/triple-minors-m$m.ms" -o "$OUT/triple-gb-m$m.txt"
  t2=$(date +%s)
  echo "m = $m: export $((t1 - t0)) s, msolve $((t2 - t1)) s, basis: $(grep -A1 'length of basis' "$OUT/triple-gb-m$m.txt" | tr '\n' ' ')"
done

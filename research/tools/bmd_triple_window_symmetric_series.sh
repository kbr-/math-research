#!/bin/sh
# Series driver for the symmetric form of the triple window (cycle bmd-20261009-kga; prop:cube-triple-window-symmetric-factorization).
# CHECKS: m values for the factorization control (MODE=check); MS: m values for chart A (msolve over Q) and chart B;
# NEGM: m for the negative control (two minors only; msolve must not return {1}); OUT, THREADS as in the exact series driver.
# Usage: env CHECKS="1 2 3" MS="9 10" NEGM=9 OUT=dir THREADS=8 sh bmd_triple_window_symmetric_series.sh
set -e
G=research/tools/bmd_triple_window_symmetric_export.gp
for m in $CHECKS; do env MODE=check M=$m gp -q $G 2>/dev/null; done
run() {  # $1 = m, $2 = file suffix, $3 = NEG
  rm -f "$OUT/sym-A-m$1$2.ms" "$OUT/sym-A-m$1$2-gb.txt"
  t0=$(date +%s); env MODE=A M=$1 OUT="$OUT" NEG=$3 gp -q $G 2>/dev/null; t1=$(date +%s)
  /usr/bin/time -f "%M" -o "$OUT/.mem" msolve -g 2 -t $THREADS -f "$OUT/sym-A-m$1$2.ms" -o "$OUT/sym-A-m$1$2-gb.txt"; t2=$(date +%s)
  echo "m = $1$2: export $((t1 - t0)) s, msolve $((t2 - t1)) s, max RSS $(cat "$OUT/.mem") kB, basis: $(sed -n '6p' "$OUT/sym-A-m$1$2-gb.txt"), first element: $(sed -n '8p' "$OUT/sym-A-m$1$2-gb.txt" | cut -c1-40)"
  rm -f "$OUT/.mem"
}
if [ -n "$NEGM" ]; then run "$NEGM" -neg2 2; fi
for m in $MS; do run $m "" ""; done

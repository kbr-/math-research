#!/bin/bash
set -e
for v in c1 c0 c2 base; do
  OMP_NUM_THREADS=12 /home/kbr/.claude/jobs/d56a25e2/tmp/direct_sum < /home/kbr/.claude/jobs/d56a25e2/tmp/pair_N24_$v.in > /home/kbr/.claude/jobs/d56a25e2/tmp/pair_N24_$v.out
  echo "$v $(tail -1 /home/kbr/.claude/jobs/d56a25e2/tmp/pair_N24_$v.out)"
done

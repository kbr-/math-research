# Matching avoidance with slack

The notebook entry `entry-2026-09-20-matching-avoidance-repair` gives the complete
argument and the corrected dense-label threshold. `source-audit.json` records
attribution and the limits of source access; no third-party full text is included.

Reproduce the finite control through the protected launcher:

```bash
./compute.sh g++ -std=c++20 -O2 research/tools/check_matching_avoidance.cpp -o /tmp/check_matching_avoidance
./compute.sh /tmp/check_matching_avoidance --out /tmp/matching-avoidance-new.jsonl
```

`all-boards.jsonl` contains all 66,066 forbidden boards for m=1,2,3,4.
Bit i*m+j of `forbidden_mask` represents pair (i,j). The exact avoidance
probability is `avoiding/permutations`. The checked integer inequality is
`avoiding^m * 2^edges <= permutations^m`; no numerical approximations are used.
All integers fit in 64 bits for this hard-coded range. This finite check does
not replace the universal proof. In particular, the two-by-two diagonal board
attains equality and rules out any larger universal exponential constant.

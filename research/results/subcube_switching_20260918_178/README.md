# Subcube switching lemma: encoding round-trip test

The [notebook entry](https://kbr.is-a.dev/math-research/#entry-2026-09-18-subcube-switching-lemma)
states and proves the lemma for the slack subcube family Phi_e. `roundtrip.jsonl` records eight
exact runs of `research/tools/check_subcube_switching_encoding.py`: labels are `0..n-1` with
`n = 2^L`, the residual subcube is `0..N-1` with `N = 2^L2`, and every restriction of Phi_e
(residual pigeon set of size N+1+e, injection of the other pigeons into the outside labels) is
enumerated for a random ordered disjunction of bit terms (`terms`, listed in each record, seed
given). The canonical tree of the residual instance (holes: the subcube plus the e free outside
labels) is built; for every restriction with a path of length >= s whose encoder finds a consistent
free outside label for each moved row (`rich_bad`), the trimmed lexicographically first long path is
encoded as (code restriction in Phi_{e-s}, star vectors, holes) and decoded. Fields: family size
(`restrictions`), `bad`, `rich_bad`, `round_trip_failures` (all zero). The run with e = 1 is
vacuous (no rich bad restriction). The tool prints the family size and refuses cases above
`--max-restrictions` (default 5e6).

```bash
./compute.sh --threads 1 python3 research/tools/check_subcube_switching_encoding.py \
  --L 4 --L2 2 --e 10 --r 3 --s 4 --terms 10 --seed 4 --out /tmp/roundtrip.jsonl
```
The runs use (L,L2,e,r,s,terms,seed) = (3,1,2,2,2,6,20260918), (3,1,2,2,2,10,5), (3,1,3,2,2,8,3),
(3,1,3,3,3,8,3), (3,2,1,2,2,8,11), (3,1,4,2,3,8,7), (4,1,12,3,3,12,2), (4,2,10,3,4,10,4).
A first tool version without star vectors failed 1,348 of 7,234 round trips on the first case;
that output is not retained. `provenance.json` lists the hashes of the results file and the tool.

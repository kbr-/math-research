# Random flats and the skip rule: encoding round-trip tests

The [notebook entry](https://kbr.is-a.dev/math-research/#entry-2026-09-18-random-flat-switching)
records the results. `roundtrip.jsonl` holds ten exact runs of
`research/tools/check_subcube_switching_encoding.py` (same enumeration and encoding as in
`../subcube_switching_20260918_178/`, fields as there plus `flat`, `Q`, `skip_dead`):

- `--flat random` draws the residual set Q as a uniformly random affine subspace of dimension L2
  (random independent vectors plus a translate; Q is listed in the record). Three runs without
  `--skip-dead` have zero round-trip failures over 54,713 rich bad restrictions: the light-row
  encoding does not depend on the position of the flat.
- `--skip-dead` makes the tree, the encoder, and the decoder skip a term that has an uncovered row
  with no consistent hole of Q unused by the path. Seven runs (three on the coordinate subcube, four
  on random flats) show 114, 0, 1,206, 108, 0, 883, and 359 failures; the two zero runs have too few
  rich bad restrictions to exercise the rule. The tool exits with status 1 on failures by design.
  The mechanism (a moved row's code label revives a skipped term) is documented in the entry.

An eleventh run (`--L 4 --L2 2 --e 9 --r 3 --s 3 --terms 14 --seed 8 --flat random --skip-dead`,
897,600 restrictions) was stopped before finishing; it is not in the file.

```bash
./compute.sh --threads 1 python3 research/tools/check_subcube_switching_encoding.py \
  --L 4 --L2 2 --e 10 --r 3 --s 4 --terms 10 --seed 4 --flat random --out /tmp/roundtrip.jsonl
```
The runs use (L,L2,e,r,s,terms,seed,flat,skip) = (3,1,2,2,2,6,20260918,subcube,skip),
(3,1,3,3,3,8,3,subcube,skip), (4,2,10,3,4,10,4,subcube,skip), (3,1,2,2,2,6,20260918,random,-),
(4,1,12,3,3,12,2,random,-), (4,2,10,3,4,10,4,random,-), (3,1,3,2,2,8,3,random,skip),
(3,1,4,2,3,8,7,random,skip), (4,2,10,3,4,10,4,random,skip), (4,1,12,3,3,12,2,random,skip).
`provenance.json` lists the hashes of the results file and the tool.

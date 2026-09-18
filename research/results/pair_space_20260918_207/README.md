# Pair-space round trips (cycle 207, session pair_space_decoder_20260918_207)

Tool: `research/tools/check_pair_space_encoding.py` (new). It enumerates every pair (rho, rho'') of a slack
restriction rho in Phi_e and a filling rho'' (an injection of e residual rows onto the e free labels), builds the
restricted slack tree T' (the complete-term slack tree restricted by the filling), finds the lexicographically
first path with at least h real queries, encodes it and decodes it. G is the event that no free label is pinned
by any term (E n X empty). Runs are appended to `roundtrip_pairs.jsonl`; `runs.log` holds the console output of
every invocation in order. Modes (flags): `--hole-always` queries the hole after every pigeon answer other than
the pin (the entry's rule; the default queries it only after an answer in Q); `--encoding node` (default) is the
first design (per-node record, filled tail rows moved to code labels, filled pinned rows marked OUT);
`--encoding entry` is the encoding of the entry's Section 2 (no per-node record; one bit per round and a
position plus last-of-node bit per moved row; filled rows never moved and recorded by nothing); `--fill-domain
notail` restricts the filling to rows outside every tail (the entry's pair space; default `any`); `--pin-test`
resolves a pin at a free outside label by a pin test and chooses code labels outside the pinned labels (the
entry's slack tree; the default queries the pigeon alone).

History, all under `./compute.sh run`: six runs at N = 2 found no rich bad pair on G (one free label rarely
consistent with a pattern) and a decoder crash on a wrong term (KeyError), then counted as a failure; six runs at
N = 4 with the decoder rejecting a current term that looks satisfied in the code failed on G, a decoder bug
(a moved row at a consistent code label makes the current term look satisfied; the light lemma's decoder accepts
it); the corrected first design then gave batches 1 and 2 below. The entry encoding was first tried without the
moved rows' positions (a smoke test outside compute.sh, not recorded in the jsonl): 966 of 9834 rich bad pairs
on G failed, the decoder skipping a moved row that sits at a code label as if it were matched; positions were
added to beta. Its first recorded invocation looped on a lost state off G (aborted after ten minutes; a
no-progress guard was added), and four invocations of batch 3 crashed on a lost state (ValueError, now counted
as a failure) and were rerun. Records of every invocation remain in the jsonl in order; superseded ones are
marked as such by the batch headings in runs.log.

Valid batch 1 (first design, hole query only after a pigeon answer in Q), n = 8, N = 4, all L = 3, L2 = 2:

| e | w | h | labels | seed | pairs | on G | rich bad on G | failures on G | rich bad off G | failures off G |
|---|---|---|--------|------|-------|------|---------------|---------------|----------------|----------------|
| 1 | 1 | 2 | 2 | 1 | 12096 | 12096 | 9168 | 0 | 0 | 0 |
| 2 | 1 | 3 | 1 | 2 | 18144 | 9072 | 0 | 0 | 1806 | 1257 |
| 2 | 1 | 3 | 2 | 3 | 18144 | 18144 | 196 | 0 | 0 | 0 |
| 2 | 1 | 3 | 0 (all) | 4 | 18144 | 3024 | 1080 | 0 | 4356 | 922 |
| 2 | 2 | 3 | 2 | 5 | 18144 | 9072 | 2658 | 0 | 4002 | 478 |
| 2 | 1 | 3 | 1 | 6 | 18144 | 18144 | 9900 | 0 | 0 | 0 |

Valid batch 2 (first design, `--hole-always`):

| e | w | h | labels | seed | pairs | on G | rich bad on G | failures on G | rich bad off G | failures off G |
|---|---|---|--------|------|-------|------|---------------|---------------|----------------|----------------|
| 1 | 1 | 2 | 2 | 1 | 12096 | 12096 | 9732 | 0 | 0 | 0 |
| 2 | 1 | 3 | 2 | 3 | 18144 | 18144 | 212 | 0 | 0 | 0 |
| 2 | 1 | 3 | 0 (all) | 4 | 18144 | 3024 | 1172 | 0 | 4770 | 895 |
| 2 | 2 | 3 | 2 | 5 | 18144 | 9072 | 2744 | 0 | 4193 | 637 |
| 2 | 1 | 3 | 1 | 6 | 18144 | 18144 | 9646 | 0 | 0 | 0 |
| 2 | 1 | 4 | 2 | 7 | 18144 | 9072 | 370 | 0 | 1508 | 216 |

Batch 3 (`--hole-always --encoding entry --fill-domain notail`: the entry's encoding on the entry's pair space,
pins at free labels queried as pigeons; the pairs number fewer since the filling avoids tail rows):

| e | w | h | labels | seed | terms | pairs | on G | rich bad on G | failures on G | rich bad off G | failures off G |
|---|---|---|--------|------|-------|-------|------|---------------|---------------|----------------|----------------|
| 1 | 1 | 2 | 2 | 1 | 6 | 6720 | 6720 | 5034 | 0 | 0 | 0 |
| 2 | 1 | 3 | 2 | 3 | 6 | 5040 | 5040 | 152 | 0 | 0 | 0 |
| 2 | 1 | 3 | 0 (all) | 4 | 6 | 7560 | 1260 | 580 | 0 | 2135 | 433 |
| 2 | 2 | 3 | 2 | 5 | 8 | 3024 | 1512 | 432 | 0 | 713 | 197 |
| 2 | 1 | 3 | 1 | 6 | 7 | 7560 | 7560 | 4762 | 0 | 0 | 0 |
| 2 | 1 | 4 | 2 | 7 | 8 | 5040 | 2520 | 114 | 0 | 300 | 116 |
| 2 | 2 | 4 | 3 | 8 | 9 | 3024 | 504 | 0 | 0 | 154 | 55 |

Controls for batch 3: the same encoding with `--fill-domain any` (seed 3 configuration) failed on G on 20 of 3062
rich bad pairs, the nodes at filled tail rows that the encoding does not record; without `--hole-always` (seed 3
configuration, notail) it decoded all 136 rich bad pairs on G, but there the count of the entry does not charge
the nodes whose only query is a filled pigeon without a hole query, so this run is not evidence for the entry.

Batch 4 (`--hole-always --encoding entry --fill-domain notail --pin-test`: the entry's slack tree with the pin
test and code labels outside the pinned labels; richness' is checked by the encoder, so rich counts exclude
pairs where some code label would have to be a pinned label):

| e | w | h | labels | seed | terms | pairs | on G | rich bad on G | failures on G | rich bad off G | failures off G |
|---|---|---|--------|------|-------|-------|------|---------------|---------------|----------------|----------------|
| 1 | 1 | 2 | 2 | 1 | 6 | 6720 | 6720 | 5034 | 0 | 0 | 0 |
| 2 | 1 | 3 | 2 | 3 | 6 | 5040 | 5040 | 152 | 0 | 0 | 0 |
| 2 | 1 | 3 | 0 (all) | 4 | 6 | 7560 | 1260 | 580 | 0 | 1006 | 0 |
| 2 | 2 | 3 | 2 | 5 | 8 | 3024 | 1512 | 432 | 0 | 78 | 0 |
| 2 | 1 | 3 | 1 | 6 | 7 | 7560 | 7560 | 4762 | 0 | 0 | 0 |
| 2 | 1 | 4 | 2 | 7 | 8 | 5040 | 2520 | 114 | 0 | 0 | 0 |
| 2 | 2 | 4 | 3 | 8 | 9 | 3024 | 504 | 0 | 0 | 0 | 0 |
| 2 | 1 | 3 | 3 | 9 | 8 | 3024 | 504 | 0 | 0 | 40 | 0 |
| 2 | 1 | 3 | 0 (all) | 10 | 7 | 5040 | 840 | 520 | 0 | 795 | 0 |

Reading: batch 4 is the positive control for Lemma B of the entry (no failure on or off G on every rich' bad
pair); batch 3 off G and the `--fill-domain any` control are the negative controls exhibiting the two failure
modes the entry names (a pin at a code label; a filled tail row). The probability bounds of the entry are not
tested; the boards are too small.

`count_check.py` / `count_check.txt` (under `./compute.sh run`): enumeration of |Phi_k(S)| on boards with n <= 9, N <= 3,
e <= 3 against the formula C(n+1-e, N+1+k-e) C(n-N, k) (n-N-k)! and of the ratio |Phi_(e-s)(S)| / |Phi_e(S)| against the
product prod (N+1-i)(e-i)/(n-N-e+1+i) and theta_A^s of Lemma C; all cases agree (ALL OK).

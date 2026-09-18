# Spectra of near-injective labelings (Spin cycle 225, 18 September 2026)

Notebook entry: `entry-2026-09-18-parity-tree-subspace`.

`research/tools/near_injective_spectrum.py --l L --maxcodim 4 --top 40 --out FILE` computes the
Walsh transform of the indicators of S_j (labelings of n = 2^L rows by L-bit labels with image
size n - j, j = 0, 1, 2) on F_2^(n L), lists the 40 largest coefficients (normalized by the size
of the set) with the character written as one functional per row, and searches the 24 largest
characters exhaustively for the best density boost on an affine subspace of codimension 1 to 4.
The search is a lower bound on the maximal boost; 1 + (sum of the 2^s - 1 largest normalized
coefficients) is an upper bound.

- `spectrum_l2.json`: four holes (2^8 points).
- `spectrum_l3.json`: eight holes (2^24 points).

Both runs went through `./compute.sh run parity_tree_subspace_20260918_225 --threads 1`.

`birthday_codim.py` (output `birthday_codim.txt`) evaluates the exact boost of the birthday
subspace of Section 4 of the entry and the codimension at which it reaches beta_2.

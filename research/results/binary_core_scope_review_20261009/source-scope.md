# Source scope for the scheduled core review

These readings establish the precise interfaces being compared, not full-paper
certification of every external result. All new control proofs are in the notebook.

- Fomin, Lokshtanov, Panolan and Saurabh, *Efficient Computation of Representative
  Families with Applications in Parameterized and Exact Algorithms*, author PDF:
  https://sites.cs.ucsb.edu/~daniello/papers/efficientRepSetJ.pdf
  Read the representative-family definition, Theorems 1.1 and 3.7, the exterior-
  product/column-basis proof, and the larger-rank truncation discussion. Our control
  concerns the extension-preserving property, not a refutation of the theorem's
  rank-p+q construction. No weighted-algorithm implementation was audited.
- Alweiss, Lovett, Wu and Zhang, *Improved bounds for the sunflower lemma*, ECCC
  TR19-110, 23 August 2019:
  https://eccc.weizmann.ac.il/report/2019/110/download
  Read Definitions 1.1, 2.1–2.2, Theorem 1.4 and the robust-sunflower statement,
  including the elementary disjointness/robust-to-ordinary proofs. The review tests
  what this displayed bound and a sunflower structure imply for a core cover; it
  claims neither a full-proof audit nor that this is the latest quantitative bound.
- Gowers, Green, Manners and Tao, *On a conjecture of Marton*, v2:
  https://arxiv.org/pdf/2311.05762v2
  Read the exact covering formulation (Conjecture 1.1, established by Theorem 1.2)
  and stated hypotheses. No full entropy-proof or Lean replay certification. The
  basis-set calculation tests a missing source hypothesis and does not contradict
  the published small-doubling theorem or its later algorithmic versions.
- Bodlaender, Cygan, Kratsch and Nederlof, *Solving weighted and counting variants
  of connectivity problems parameterized by treewidth deterministically in single
  exponential time*:
  https://arxiv.org/pdf/1211.1505
  Read the connection/cut matrices, Lemmas 3.13–3.14 and Appendix B.1's full parity
  factorization proof. The review proves its own analogous subspace-join formula;
  no entire dynamic-programming algorithm or source-to-state map is imported. An
  initial institutional PDF URL failed; the arXiv source supplied the proof.
- Gottesman, *Stabilizer Codes and Quantum Error Correction*, Section 3.2:
  https://arxiv.org/pdf/quant-ph/9705052
  Read the stabilizer definition, exclusion of negative identity and code-space
  dimension statement. The projector trace proof and parity control are written
  directly in the review. No stabilizer-simulation theorem is transferred to the
  binary charged quotient.

Internal reading includes the six completed entries, paid copying/core-sharing
identities, and the exact current binary CNF/unbalanced-PC boundary record. The
reviewer first saw only blind-brief.md; route-brief.md and the preferred direction
were delivered after its independent verdict. Its initial copy-identity suggestion
was corrected using already proved source relations before selecting the next test.

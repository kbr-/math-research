# A genuine obstruction to universal Boolean-domain normalization

The [notebook entry](https://kbr.is-a.dev/math-research/#entry-2026-09-14-Boolean-domain-profile-obstruction)
contains the full argument. Approximate majority has no nonzero certifying
polynomial of degree at most its Hamming-ball radius, over any field. A
polynomial-size three-level evaluation source for that function therefore rules
out a universal old-only map with Booleanity-only source-image certificates at
the degree required by the current PHP endpoint.

The same argument gives a quantitative lower bound for Boolean-domain-valid
representations over one old-affine ENS family. It does not rule out profiles
whose witnesses use the PHP axioms, or a proved restriction on the source of a
short PHP proof. No short PHP proof or new Frege lower bound is constructed.

The entry also preserves the earlier free-parameter interface obstruction and
its exact scope, and the distinction between selector-valued polynomials and
raw coefficient values. These are separate from the genuine source example.

## Reproduce the finite control

With resource controls and an active timing session, from the repository root:

~~~sh
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -O2 -std=c++17 -Wall -Wextra \
  research/tools/check_profile_certifier_obstruction.cpp -o /tmp/math-profile-certifier
./compute.sh run TURN --threads 1 --timeout 180 -- \
  /tmp/math-profile-certifier --out NEW_OUTPUT_PATH
~~~

The checker refuses to replace an existing output. It installs no dependencies.

`profile-certifier-obstruction.jsonl` contains:

- the complete depth-three circuit on eight old bits: eight DNFs with 1,231
  terms each, sampled width nine, and seed 1490001;
- all 9,848 term masks, retaining repeated terms and removing repeated variables
  inside each AND, which leaves the represented function unchanged;
- all 256 truth-table values in increasing bit-mask order;
- six 37-by-37 evaluation matrices and verified two-sided inverses, for the two
  Hamming balls over F2, F3, and F5;
- two nonzero higher-degree certifiers, in exact factored form with every point
  of their supports, as positive controls;
- the three-level original source-weight ledger at accuracies one, two, and six.

The matrices certify that no nonzero polynomial of degree at most two has
monochromatic support for this circuit. The finite fixture is a local Boolean
function, not PHP. The weight ledger is symbolic: this run does not expand the
entire large ENS source or enumerate its coefficient assignments.

Compilation and the exact run passed. The general obstruction is proved
symbolically in the notebook; these finite controls do not replace that proof.

## Source attribution and evidence

The certifying-polynomial idea and the binary approximate-majority obstruction
are attributed to Swastik Kopparty and Srikanth Srinivasan, *Certifying Polynomials
for AC0[Parity] Circuits, with Applications to Lower Bounds and Circuit Compression*,
Theory of Computing 14(12), 2018, DOI 10.4086/toc.2018.v014a012.
See `source-audit.json` for exact passages and reading limits.

The unchanged journal PDF and its identified text conversion are retained under
CC BY 3.0, with author attribution in THIRD_PARTY_NOTICES.md. The repository's
license does not replace the paper's license.

`check-metadata.json` records the focused evidence and touched-link review.
`provenance.json` hashes the source files, checker, and research evidence.
The timing fragment and full session journal are archived under this session in
`research/provenance/session-records/`.

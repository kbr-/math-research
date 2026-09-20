# First-jet proof of the finite-field double-cover value

Research cycle: `odd_cover_source_audit_20260920`, 20 September 2026.
The complete general argument is in the side notebook's
`entry-2026-09-20-double-cover-first-jets`, with registered lemma
`lem:finite-field-punctured-first-jet-degree` and theorem
`thm:odd-field-double-cover-exact`.

The theorem gives f_q(n,2,1)=(q-1)(n+1) for every finite field and n>=1;
the origin may be covered zero or once. The latter case requires one extra
plane. The degree proof uses monic grid division, reduced-value uniqueness and
first derivatives, not an unproved preservation of multiplicity under reduction.
The nonvanishing-origin bound is known from Ball–Serra; no novelty claim is made
for the full application, and independent review remains outstanding.

`check_jets.py` is an exact falsification/control check, not a proof of the general
result. It uses NumPy table arithmetic over GF(2), GF(3), GF(5) and GF(9), the last
represented by GF(3)[a]/(a^2+1). No floating-point rank, overflow-prone large sums,
dependency installations or uncontrolled enumeration occur. The largest matrix
has 243 rows and 378 columns. All six cases pass at three adjacent degree levels,
and the known construction covers every nonzero point twice while missing zero.

Reproduce through the protected launcher (choose a new output filename to preserve
accepted results):

```sh
./compute.sh --threads 1 python3 research/results/odd_cover_source_audit_20260920/check_jets.py \
  --out /tmp/odd-cover-jet-checks.json
```

`jet-checks.json` retains every rank, matrix dimension and input-matrix hash.
`sources.json` retains the bounded literature queries, primary-source links and
reading scope. Third-party full text is not included. Timing and full command
output are archived with the checkpoint, including repaired metadata validation
errors from initially missing external-source locators.

Stop-condition audit: the branch goal ranges over all fixed odd prime powers at
sufficiently large dimension. The recorded theorem covers every prime power and
every positive dimension, with the exact multiset and origin conventions. Its
proof handles both origin cases and matches a construction. This reaches the
solved branch of the user-specified stop condition after one research cycle;
it does not certify novelty, formal verification, or any case k>=3.

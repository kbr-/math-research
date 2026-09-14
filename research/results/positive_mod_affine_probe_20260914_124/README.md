# Complete shared-probe transfer for positive MOD inputs

The [notebook proof](https://kbr.is-a.dev/math-research/#entry-2026-09-14-positive-MOD-affine-probe)
handles inputs 1-(a_i*t+q_i+c_i)^(p-1), with one shared old affine probe t and
individual old Boolean literals q_i. The probe may involve those same literal
variables. Residue selection maps the entire coefficient system to at most p
affine blocks at degree pD, preserving accuracy and original axiom accounting.

## Reproduce

~~~sh
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -O2 -std=c++17 -Wall -Wextra research/tools/check_positive_mod_probe.cpp \
  -o /tmp/math-positive-mod-probe
./compute.sh run TURN --threads 1 -- \
  /tmp/math-positive-mod-probe --out NEW_OUTPUT_PATH
~~~

Run from the repository root with active resource controls. The output must be
new. The exact C++ checker uses the existing sparse polynomial and typed-domain
certificate helpers. No dependencies are installed.

## Complete evidence

NS-probe-images.jsonl has three fixtures:

- F3, h=1, one shared probe and three literal inputs: 16 NS certificates,
  11 retained-system models.
- F3, h=2, varied slopes including a domain-only zero input: 19 certificates,
  11 models.
- F5, h=1: 22 certificates, 19 models.

In every fixture the probe is the sum of all old bits and overlaps all literal
variables, including a complemented literal. Every field residue is attained.
All 32 old Boolean states are checked. Wrong-branch and omitted-residue controls
fail companions on otherwise valid retained-system models. A mapped coefficient
with value two is explicitly exercised.

Every polynomial, axiom, map, cofactor, and model is retained. Polynomials use
[coefficient,[variable IDs with repetitions]], so powers are ordinary powers.
Each NS target is checked against the sum of its generator multiples and its
degree ceiling, with original source degrees recorded for axiom images.
Product differences leave new coefficient variables formal and use old Boolean
equations only; coefficient-field images use actual Fp domains.

The final checker caches fixed companion images during model evaluation.
A protected rerun was compared byte-for-byte with the canonical output and
matched. Its temporary output duplicates the retained file.

The local systems are satisfiable typed-domain tests, not PHP refutations.
The source-class lower bound uses the notebook's all-prime affine theorem,
not an extrapolation from the finite fixtures.

## Dependencies and source scope

This cycle read the notebook's common-bit positive-MOD transfer, older
small-probe extraction/realization, and row-profile normalization. Their
hypotheses differ from the new complete coefficient map; the entry states
those distinctions and links the original records. No new external paper was
needed. One guessed navigation anchor was absent, and the indexed anchors
were used instead.

All builds and mathematical checks passed. Exact source/dependency hashes,
command evidence, and measured timing accompany the checkpoint.

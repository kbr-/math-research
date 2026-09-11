# Shared survivors and private cuts

11 September 2026. The [full notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-11-survivor-sharing)
proves the survivor quotient and the stronger hybrid simulation: identify only
eventual survivors, keep every planned cut private, and obtain literal MP
comparisons. Signed MOD multiplicities then cancel in coherent scalars. No
small bound on the essential surviving canonical family is claimed.

## Reproduce

With the shared resource controls active, from the repository root:

```bash
mkdir -p research/tmp
./compute.sh --threads 1 c++ -std=c++17 -O2 -Wall -Wextra -Werror -pedantic \
  research/tools/check_survivor_resharing.cpp -o research/tmp/check_survivor_resharing
./compute.sh --threads 1 research/tmp/check_survivor_resharing \
  --out research/results/survivor_resharing_20260911_21/checks-REPRO.jsonl
./compute.sh --threads 1 c++ -std=c++17 -O2 -Wall -Wextra -Werror -pedantic \
  research/tools/check_private_survivor.cpp -o research/tmp/check_private_survivor
./compute.sh --threads 1 research/tmp/check_private_survivor \
  --out research/results/survivor_resharing_20260911_21/private-controls-REPRO.jsonl
```

Use new output paths; both tools create their parent directory. The accepted
runs used GCC 11.4.0, C++17, one thread, and the existing exact sparse polynomial
and ENS kernels without changes. No dependencies were installed. Both
compilations and all 16 cases passed. The outputs are complete:

- `checks-01.jsonl`: 939,657 bytes, eight quotient cases.
- `private-controls-01.jsonl`: 166,299 bytes, eight focused private-root cases.

## Quotient cases and encoding

Each prime p=2,3,5,7 is tested at accuracies one and two. Base variable IDs
0,1,2,3 denote Boolean x,y,z,w; subsequent IDs are field-valued coefficients.
There are p+1 independent copies of I=P_(x,y), Q=P_(I,1-z), plus another
inner copy and the distinct root Q_w=P_(I_w,1-w). These represent the source
expansion of (X AND Y) OR Z and its W variant.

The already-pruned forest includes a marked removed ancestor as metadata only;
it has no block or coefficient family in the system. Three canonical classes
have live witnesses: the common inner formula and the two distinct outer
formulas. All their inputs, products, prefixes, companions, and coefficient
coordinates are saved, together with the complete variable-identification map.
Canonical blocks are reconstructed from mapped inputs and witness coefficients
before checking every image. Degree does not increase.

Polynomial terms use `[coefficient, [sorted repeated variable IDs]]`. This is
the sparse kernel encoding, not the exponent-pair encoding of pc_boundary.hpp.
The scalar-image array is ordered as p-fold sum, p-fold sum plus one, signed
complementary pair, and p+1-fold sum. Their images are 0,1,0,Q. Original MOD
values need not be expanded: the complete scalar and its known exponent p-1
determine them exactly.

The upper-only identification leaves a nonzero scalar error because inner
copies differ. Merging the Z and W formulas leaves a different nonzero error.
An artificial missing inner descendant is rejected as a violation of the
theorem's sufficient closure hypothesis, not as a universal impossibility
result for every quotient. Exact models give Q both values 0 and 1 while all
canonical companions hold, and their lifted assignments satisfy every original
companion. The argument is not a constantly true formula or a zero product.

## Private-root controls

These use Boolean x,y,z as IDs 0,1,2. Allocate a retained inner/root pair and
another inner/root pair of the same syntax. Only the other inner family is
identified with its retained counterpart. The other outer root is designated
for removal and keeps its private coefficients. Its input tuple becomes
literally canonical, but its product and companions retain those private
parameters. Every private field equation is unchanged.

The checker confirms that the retained target and axioms contain no private
coefficient. It also tests the forbidden extra merge of the selected root
with the retained root: the mapped selected family then occurs in the old
target and retained companions, invalidating the claimed removal freshness.
These focused controls were added after the stronger hybrid result was proved;
the completed quotient suite was not rerun.

## Provenance, timing, and scope

`provenance.json` hashes both tools, the shared sparse/ENS kernels, and both
complete outputs. The mathematical dependencies are the notebook's inherited
live-forest, scalar MP, and substitution arguments. No new source paper was
read or downloaded. These are local exact image checks, not a compiler for
arbitrary Frege proofs.

`timing.html` is embedded in the notebook. Initial preparation includes the
previous checkpoint's archive, publication audit, and authorized push. A timing
workflow issue was identified: in this cycle and cycles 18-20, coding markers
were bundled with the code patches in the same tool calls. Argument drafting
therefore occurred before the marker executed, and computation design/code
drafting remains partly mixed into mathematics. The coding rows do not measure
its full duration. No retrospective split is invented and prior tables remain
unchanged. Future phase changes will execute in separate calls before the work.
The small policy correction is committed separately after this research entry.

No rendering build or historical mathematical suite was repeated. Complete
command evidence is archived under
`research/provenance/session-records/survivor_resharing_20260911_21/`.

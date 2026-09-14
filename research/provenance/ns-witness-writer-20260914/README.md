# Shared ordinary NS witness verification

The joint-selector and shared-bit-source checkers now use one small helper,
[ns_witness.hpp](../../tools/ns_witness.hpp), to reconstruct each NS identity,
charge the degree of every generator multiple, and serialize its terms.
Case metadata and source-specific original-degree checks remain with callers.

The helper verifies the witness before emitting its term suffix. It does not
reduce Boolean or field equations implicitly. Cancellation between multiples
does not lower the charged witness degree.

## Validation

- Both complete affected research outputs reproduced byte for byte: the
  50-certificate joint-selector record and 82-certificate shared-bit record,
  including their models.
- Six legal F2/F3 witnesses were accepted.
- Six corrupt or over-budget witnesses were rejected before a suffix was
  emitted, including a zero target whose cancelling multiples exceed the budget.

The complete small checks are in [validation.jsonl](validation.jsonl).
Reproduction commands and the compared canonical paths are recorded in
[reproduction.json](reproduction.json); source and evidence hashes are in
[provenance.json](provenance.json). No historical matching suites were rerun.

Compile and run through the protected launcher, with a fresh output path:

~~~sh
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -O2 -std=c++17 -Wall -Wextra research/tools/check_ns_witness.cpp \
  -o /tmp/math-ns-writer-check
./compute.sh run TURN --threads 1 -- \
  /tmp/math-ns-writer-check --out NEW_OUTPUT_PATH
~~~

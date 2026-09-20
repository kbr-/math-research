# Compact-code trace-rank controls

The authoritative statement and proof are in notebook entry
`entry-2026-09-20-compact-trace-list-rank`.

The bounded C++ tool checks the **pin-free core**, not heavy-round decoding or
large-parameter probability bounds. It fixes n=8, N=2, at most two slots and six
slot bits. It enumerates every candidate ordered moved-row tuple for each of 130
readers (128 seeded readers and two explicit controls). There are 2,340 candidates,
so neither the search size nor memory use depends on unbounded input parameters.

The accepted output is `pin-free-fibers-reviewed.json`: 31 accepted preimages,
27 fibers, nontrivial fibers of sizes two and four. All exact F2 diagonal,
triangularity and rank checks pass. The output retains every reader and accepted
fiber, with its raw advice, slot labels, trace, monomial list and evaluation rows.
A monomial integer is the bitmask of variables; slot k uses bits 3k through 3k+2.
An evaluation-row integer is its bitmask of values on the ordered fiber.
The fixed code assignment is [-1,-1,-1,5,6,1,2,3,7], with -1 denoting residual,
and the residual flat is {0,4}. For s slots the filling rows are 0,...,s-1.

Reproduction from the repository root, with the required controls already active:

```bash
./compute.sh g++ -std=c++17 -O2 -Wall -Wextra -Werror \
  research/tools/check_tail_code_list.cpp -o /tmp/check_tail_code_list
./compute.sh /tmp/check_tail_code_list --out /tmp/pin-free-fibers-reviewed.json
```

The final checker stops when any term is satisfied. The separate initial output
`pin-free-fibers.json` used selected-term stopping (the convention in the historical
pair-space checker) and did not yet include the four-preimage control. It had 2,310
candidates and 48 accepted preimages. It is a diagnostic under that convention,
not the output of the final source. The argument permits both stopping conventions;
any supplied round bound must concern the same tree. The initial compiler failure
was only a misleading-indentation diagnostic promoted to an error; the accepted
build passed with all warnings treated as errors.

These finite checks do not prove the theorem, test pinned readers, or establish
a switching probability or a Frege lower bound. The general argument and the
separate pin-status reasoning are given in full in the notebook.

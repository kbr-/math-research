# Pin-peeling and trace-list controls

See notebook entry `entry-2026-09-20-pin-peeling-composition` for the complete
working proof, probability accounting and the full-single-row application.

The C++ checker is deliberately bounded: n=8, N=2, at most two slots, six slot
bits and 131 readers. It considers 2,370 ordered candidate inputs. Every pin is
outside Q={0,4}, so these controls have **no heavy rounds**. They test false code
matches, early revelation, greedy current-term code-label exclusions and the
triangular polynomial argument after fixing a peeling/advance word.

The accepted output `pin-peeling-fibers.json` preserves every reader and accepted
fiber. It contains 37 preimages in 35 raw-code/event-word groups, two with size
two. The raw-code maximum fiber before the event word is four. Five peeling events
occur, including one revealing slot two before the first move. All diagonal,
triangularity and exact F2 rank checks pass. The explicit controls are:

- Crossed pins: the two raw preimages have different event words.
- Crossed pins plus a hidden tail: a size-two fiber remains within each of two words.
- A false pin on the second moved row: slot two is revealed before move one.

The code assignment is [-1,-1,-1,5,6,1,2,3,7], where -1 denotes residual; filling
rows are 0,...,s-1. Pattern triples are [row, bitmask, value], and pin pairs are
[row,label], with row=-1 for no pin. Polynomial monomial integers encode variable
subsets, with slot k occupying bits 3k through 3k+2. Evaluation-row integers are
bitmasks of their values on the ordered fiber. Extended traces interleave priority
(0 for matched pin, 1 for pin-free) with term index. Advice words use A for advance
and Pk for revealing the zero-based slot k. Every source parameter is fixed, and
there is no unbounded search-size input.

Reproduce from the repository root with existing resource controls active:

```bash
./compute.sh g++ -std=c++17 -O2 -Wall -Wextra -Werror \
  research/tools/check_pin_peeling_list.cpp -o /tmp/check_pin_peeling_list
./compute.sh /tmp/check_pin_peeling_list --out /tmp/pin-peeling-fibers.json
```

These are finite controls of the mechanism, not a proof of the general theorem,
a test of heavy-round cases, or a numerical verification of its asymptotic bound.
The theorem's initial-match flags and heavy-node arguments are reviewed in prose.

# Empty-aware bipartite switching: exact encoding controls

The full proof and its scoped all-prime source consequence are in the notebook
[entry](https://kbr.is-a.dev/math-research/#entry-2026-09-21-empty-aware-bipartite-switching).
This report checks finite encoding/decoding instances, not the asymptotic bound.

Reproduce from the repository root, with a fresh report path:

    ./compute.sh g++ -std=c++17 -O2 -Wall -Wextra -Werror research/tools/check_empty_hole_switching.cpp -o /tmp/check_empty_hole_switching
    ./compute.sh /tmp/check_empty_hole_switching --out /tmp/empty-switching.jsonl

The fixed suite uses boards (n,N,s)=(4,2,2) and (5,3,3), with 12 ordered formulas
per board. There are 120 and 300 original restrictions per formula. Cases include
column guards plus diagonals, diagonal graphs, and seeded width-one/two terms.
The seed is 20260921. The report records every formula and all aggregate results,
including the charge histogram and an explicit empty-answer code when present.

Every canonical bad prefix of length s is checked, including multiple prefixes
from one restriction. The asymptotic injection may select just the first such
prefix. Cross-restriction code collisions are checked across the entire finite
set. The decoder must recover the exact original occupied matching and remove
all added empty markers. A corrupted empty-answer code is tested as a negative
control. First-surviving terms, rather than a search for later true terms, govern
the deterministic canonical order.

An action [p,h] occupies an edge; [-1,h] declares hole h empty. Vertices and edge
positions are zero-based. In an answer word, the special symbol n+1 means empty;
other integers index the decoder's currently known sorted partner list. The
numeric gap before that special symbol does not enlarge the alphabet: the
partner sets have sizes at most N+1 and N, giving at most N+2 possible symbols.
The beta masks select original-term edges, and endpoint masks use pigeon then
hole for each selected edge in term order.

Results: 11,081 prefixes checked, 3,688 with empty answers, 3,827 with multiple
rounds, zero round-trip failures or cross-restriction collisions, and all charge
bounds respected. The search visited 82,708 nodes, under its 5,000,000-node cap.
The small-board probability bounds are vacuous; no numerical confirmation of
an asymptotic tail estimate is asserted. One strict compile attempt failed on
misleading indentation; after that formatting fix the build and suite passed.
No dependencies were installed. Complete command output and timing are archived.

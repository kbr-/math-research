# Bit relations below the label width

The [full notebook proof](https://kbr-.github.io/math-research/#entry-2026-09-13-bit-low-degree-rigidity)
shows that, for n=2^ell and ell>=2, every transported relation in J_d with
d<ell is a bit Booleanity consequence. Compact equality polynomials give
non-Boolean relations at degree exactly ell.

The proof reduces a putative relation to its top occupied-row set in the
functional unary NS quotient. Its coefficient must be a sum of functions
each missing a row. Disjoint coordinate cubes then isolate a leading bit
monomial and annihilate every missing-row potential, giving a contradiction.

## Complete geometric checks

<code>coordinate-cubes.jsonl</code> contains every ordered nonempty family
of nonempty coordinate-axis sets with total dimension below ell, for ell=2..6.
For each family, the program greedily chooses the first available canonical
coset in increasing representative order. It enumerates every product tuple,
checks pairwise distinct labels, and evaluates the mixed finite difference of
the monomial containing exactly the specified axes in each row.

It also checks every point-indicator basis function of every missing-row
potential. The saved parity arrays are complete, including their zero entries.
At total dimension ell, the two complementary axis sets {0} and {1,...,ell-1}
give a negative control: every pair of their cosets intersects exactly once.

| ell | Ordered families | Product tuples | Boundary pairs |
| --- | ---: | ---: | ---: |
| 2 | 2 | 4 | 4 |
| 3 | 15 | 54 | 8 |
| 4 | 142 | 1,024 | 16 |
| 5 | 1,855 | 27,310 | 32 |
| 6 | 31,601 | 945,304 | 64 |
| Total | 33,615 | 973,696 | 124 |

All checks passed. These are exact F2 geometric/coefficient checks, not
computations of the full higher-degree PHP NS or PC consequence spaces.
The theorem uses the separately proved old functional-base filtration.
Historical quotient computations were not rerun.

## Data encoding

The first record gives schema version 1 and field 2. Labels and axis sets
are integer bit masks; coordinate zero is the least significant bit.
A coset representative has zero entries on its cube's axes.
Cube points are listed in increasing submask order.

Each family record includes ell, a zero-based ID within ell, all axes,
dimensions, total degree, representatives, complete cube point lists,
product-tuple count, the leading coefficient (one), and one full parity
array for each omitted row. An array index chooses a tuple on all remaining
cubes, with the first remaining row's cube index least significant.
Each entry is the F2 sum of that tuple's indicator over the entire cube product.
All these sums are zero.

Boundary records give both axes, coset representatives, full point lists,
and the unique intersection point. Each ell has a summary, followed by one
overall summary. No random choices or external libraries are used.
The program streams records and refuses existing output paths.

## Reproduction

Use a fresh output path:

~~~bash
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -O2 -std=c++17 -Wall -Wextra \
  research/tools/check_bit_coordinate_cubes.cpp \
  -o /tmp/math-bit-coordinate-cubes
./compute.sh run TURN --threads 1 -- \
  /tmp/math-bit-coordinate-cubes --out NEW_OUTPUT.jsonl
~~~

Optional <code>--min-ell</code> and <code>--max-ell</code> select a subrange
of 2..6. The source, this description, and complete output are pinned by
<code>provenance.json</code>. The notebook contains the measured timing;
the session archive retains the journal and full command output.

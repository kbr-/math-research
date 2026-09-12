# Occupancy probes: exact low-degree feasibility

The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-12-occupancy-probe-feasibility)
contains the full proof. For n>=3, add sigma_j=0 for columns 1 through n-1
to the weak PHP base, leaving column zero unprobed. The augmented system has
PC refutation degree two over every prime field. Its NS degree is two when
p does not divide n, and three when p divides n.

The one-row normalizer consequence concerns affine coefficients whose factor H
has a base certificate through degree two. Its nonexistence when p divides n
does not exclude general all-companion normalizers through degree three.

## Checked upper certificates

The n=3 cases over F2, F3, and F5 record:

- Completed PC degree-two refutations, including corrupted-line controls.
- NS degree-two certificates for two unprobed-row consequences and an NS
  degree-three refutation obtained by multiplying a completed consequence.
- For F2 and F5, the sharper NS degree-two refutation and the actual one-row
  ENS product, companion, and coefficient-field images.

All 21 NS certificates and three PC traces passed. Three saved affine-subsystem
points satisfy all degree-one generators and violate a collision, verifying
the degree-one controls without claiming full PHP models.

## Complete normalized designs

| n | p | Tested degree-two generator multiples |
| -: | -: | -: |
| 3 | 3 | 108 |
| 4 | 2 | 228 |
| 5 | 5 | 415 |

All 751 values are zero. The designs have value one on the constant polynomial.
Each complete moment matrix includes the constant, first moments, and every
quadratic moment. Its index zero is the constant; index `1+i*n+j` represents
the variable x_i_j. These are linear functionals, not probability measures or
multiplicative assignments.

The same recipes at (n,p)=(4,3),(3,2),(4,5), where p does not divide n, fail
recorded generator equations. Every nonzero value is saved. These three
divisibility controls complement the three affine-subsystem controls above.

The symbolic polynomial records use x_i_j at index 3*i+j for n=3; the two own
ENS coefficients use indices 12 and 13. This differs from the explicitly labeled
moment-matrix indexing. Polynomial records use coefficient/exponent pairs, with
the empty list denoting zero. Full source polynomials and trace lines are saved.

## Reproduce

```bash
./compute.sh run CHECK --threads 1 --category local_processing --timeout 90 -- \
  g++ -O2 -std=c++17 -Wall -Wextra -pedantic \
  research/tools/check_occupancy_probe_feasibility.cpp -o /tmp/check_occupancy_probe_feasibility
./compute.sh run CHECK --threads 1 --category computation --timeout 90 -- \
  /tmp/check_occupancy_probe_feasibility --out PATH-TO-NEW-OUTPUT.jsonl
```

Output is not overwritten. The saved result is `checks-01.jsonl`; all
mathematical checks passed. `provenance.json`, the timing fragment, and the
archived session preserve source hashes, command output, and measured intervals.

Several patch submissions were rejected for JavaScript quoting or an HTML-escaped
context mismatch and corrected without file changes from the rejected calls.
The first compilation reported one indentation warning; a whitespace fix compiled
cleanly. It did not alter the checked algorithm, so the mathematical suite was
not repeated solely for that formatting change.

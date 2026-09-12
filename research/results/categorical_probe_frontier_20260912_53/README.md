# Unequal scalar alphabets and their coordinate cost

The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-12-categorical-probe-frontier)
contains the exact heterogeneous frontier, its constructive proof, the native
coordinate comparison, and the separate vector-profile and full-row scope controls.

## Reproduce

From the repository root with active resource controls:

```bash
./compute.sh run CHECK --threads 1 --category local_processing --timeout 90 -- \
  g++ -O2 -std=c++17 -Wall -Wextra -pedantic \
  research/tools/check_categorical_probe_frontier.cpp -o /tmp/check_categorical_probe_frontier
./compute.sh run CHECK --threads 1 --category computation --timeout 90 -- \
  /tmp/check_categorical_probe_frontier --out PATH-TO-NEW-DEFAULT-OUTPUT.jsonl
./compute.sh run CHECK --threads 1 --category computation --timeout 90 -- \
  /tmp/check_categorical_probe_frontier --out PATH-TO-NEW-MIXED-OUTPUT.jsonl --mixed-only
```

The saved session is `categorical_probe_frontier_20260912_53`. The first three
cases are in `checks-01.jsonl`; the added heterogeneous case is in `mixed-01.jsonl`.
The latter runs independently and did not rerun the completed cases. Existing
outputs are never replaced. No random choices are used.

## Mathematical scope

There is one scalar probe per independent column, with k_j prescribed nonzero
values and an available zero state. The nonzero state indicators are actual old
Boolean coordinates, mutually exclusive within their column.

For accuracy h and coefficient degree T, let q=max(0,N-hT), where N is the probe
count. Normalization over the proper state ideal exists exactly when the q
smallest k_j values sum to at most h. The upper construction assigns one row per
nonzero value of each selected center and at most T side columns per row.

For equal alphabet sizes k this is `h_min=ceil(k*N/(k*T+1))`.
For bare scalar coordinates with their stated alphabet equations the frontier
instead is `ceil(sum(k_j)/(T+1))`. Indicator interpolation can change ordinary
degrees, so these representations cannot be conflated.

The F7 conic-profile example and the full-PHP weighted-row normalizer are analytic
scope controls in the notebook. They were not part of these numerical runs.

## Exact cases and outputs

All computed cases use F5 and coefficient degree one:

| Case | Old coordinates | Accuracy | Original companion degree | Models |
| --- | ---: | ---: | ---: | ---: |
| Four three-value encoded columns | 12 | 3 | 7 | 256 |
| One four-value encoded column | 4 | 1 | 3 | 5 |
| One native field variable | 1 | 2 | 5 | 5 |
| Encoded alphabet sizes 1,1,4,4 | 10 | 2 | 5 | 100 |

The first output has 24 NS certificates and 266 complete source models.
The second adds 13 NS certificates and 100 models. Total: 37 NS certificates
and 366 models. Both builds and all mathematical checks succeeded.

Encoded variables are grouped by column and then ascending nonzero label.
The single-field case uses variable zero. Every output records all input and
coefficient polynomials, the selector identity, every companion and coefficient
field image certificate, and the original budget. Sparse polynomial records use
the `pc_boundary.hpp` format.

Full old states and source coefficient values are stored separately; concatenating
them gives the complete source assignment. The source product and every companion
and coefficient field equation are checked directly at each assignment. This
permits source assignments wider than the image-polynomial kernel's variable count.

No expanded certificate for the large product's squared-minus-itself polynomial
and no full source PC trace is emitted. The proved proper-ideal theorem gives its
Booleanity bound; expanding that polynomial was unnecessary for the tested image
and model claims.

The working context was consolidated to the general frontier. Timing includes
forward planning for a separate Frobenius kernel optimization and the next
projection. `provenance.json`, `timing.html`, and the archived session preserve
the actual sources, commands, complete outputs, and measured intervals.

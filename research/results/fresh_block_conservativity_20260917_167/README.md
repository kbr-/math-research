# Fresh-block conservativity test

The [notebook entry](https://kbr.is-a.dev/math-research/#entry-2026-09-18-fresh-block-conservativity)
contains the statements, the proof of the single-block loss bound, the result table, and the scope.

## What is computed

Over F2, every block has accuracy one and fresh disjoint coefficients. Variables are numbered in
creation order: old variables first, then one coefficient per block input, block by block. Boolean
equations of all variables are applied by multilinear reduction. For each source and degree D the
checker enumerates every squarefree multiple of every original companion within its original degree
`deg(g_i) + 1 + max_j deg(g_j)`, for the base alone and for the base plus the fresh blocks.

Exact elimination orders monomials containing a fresh coefficient first. Pivot rows without fresh
monomials span the intersection of the extended NS space with the existing-variable polynomials;
its rank is compared with the base rank. The product interface lists old monomials times genuine
retained whole products of weighted degree at most D (the constant included) and is reduced jointly
with each ideal basis. Each new consequence is evaluated on every model of the base source, and its
least base NS degree is found by rebuilding the base space at D+1, D+2, and so on.

`conservativity.jsonl` has one record per case and degree: matrix sizes, ranks, interface quotient
ranks, gained interface relations as (old-variable mask, product mask) pairs, and all monomials of
every new consequence. The `retained-ABC-plus-G0` case at D=5 is the control reproducing source rank
1450 and interface quotient rank 79 from `../retained_interface_test_20260915_166/`.

Two earlier runs of this session are not retained as results: the first lacked the interface and
witness analysis, and the second overcounted interface quotient ranks because remainders were not
reduced jointly with the ideal basis. Their complete outputs remain in the archived session record.

## Reproduction

```bash
./compute.sh --threads 1 --category local_processing \
  g++ -O2 -std=c++17 -Wall -Wextra -Wno-misleading-indentation \
  research/tools/check_fresh_block_conservativity.cpp -o /tmp/math-fresh-block
./compute.sh --threads 1 --timeout 3000 /tmp/math-fresh-block --out /tmp/fresh-block-replay.jsonl
```

The checker refuses to overwrite an existing output. The run takes a few minutes on one CPU.

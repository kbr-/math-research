# Functional PHP base controls for fresh affine helpers

The [notebook entry](https://kbr.is-a.dev/math-research/#entry-2026-09-18-rank-two-conservativity)
records the exact coefficient criterion, the rank-two conservativity statement (a rediscovery of the
existing rank-two normalization lemma, with a second proof), and why a larger PHP composition test
was not run.

`php-base-helpers.jsonl` (`--suite cycle169-php` of `research/tools/check_fresh_block_conservativity.cpp`)
uses the functional unary PHP base with n=2,3 holes and n+1 pigeons (rho_i-1, x_ij x_i'j, x_ij x_ik,
Boolean equations by multilinear reduction) plus one accuracy-one affine helper of rank two or three
on distinct variable pairs (x_{r,1}+x_{r+1,2}). At every degree from n+1 to n+3 the extended NS space
restricted to existing variables equals the base space; the refutation degree is unchanged.

```bash
./compute.sh --threads 1 --category local_processing \
  g++ -O2 -std=c++17 -Wall -Wextra -Wno-misleading-indentation \
  research/tools/check_fresh_block_conservativity.cpp -o /tmp/math-fresh-block
./compute.sh --threads 1 --timeout 3000 /tmp/math-fresh-block --out /tmp/php.jsonl --suite cycle169-php
```

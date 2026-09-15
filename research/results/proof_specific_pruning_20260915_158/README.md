# Pruning reuse and matrix normalization controls

The [notebook entry](https://kbr.is-a.dev/math-research/#entry-2026-09-15-pruning-reuse-and-matrix-control)
records the audit and full matrix arguments.

## Reused pruning results

- `local-zero-cofactor-pruning` already covers zero collected companion
  coefficients, including occurrences in later inputs and other cofactors.
- `ports-removal` covers isolated Booleanity ports with its actual
  information-flow and image hypotheses.
- `binary-source-companion-support-cleanup` removes binary companion use
  arising solely from Booleanity.
- `proper-OR-union-complete-support` retains nonzero local companion
  coefficients and a domain-only countermodel.

No new pruning coverage was obtained. Nonzero local support is not asserted
to survive every alternative global proof.

## Matrix scope

For a rank-r old coordinate flat, a complete matrix companion normalizer
whose coefficient entries have degree T and whose product has h factors
requires h(T+1) >= r. The matrix product is the identity at the zero input
and zero everywhere else, so each diagonal has the rank-r zero-flat indicator
as its Boolean function.

For the complete approximate-majority evaluation source, old scalar inputs
and a scalar Boolean-nonzero weight force the top matrix to equal the actual
Boolean output times the identity on the weight's support. The existing
partial-representation barrier applies to a diagonal entry.

These necessary conditions allow arbitrary matrix dimension. They do not
construct a valid matrix homomorphism, discard field/commutation requirements
for proof transfer, cover arbitrary matrix-valued weights, or exclude
PHP-relative image certificates.

## Review and evidence

No numerical run was needed. The review checks both pointwise matrix
arguments, the degree of the diagonal polynomial, the scalar-weight scope,
and the original pruning hypotheses.

The preceding checkpoint initially ran a whitespace check over the whole
working tree. An unrelated modification of `.codex/config.toml` stopped it.
The check was narrowed to the reviewed research paths and the local config
edit was not staged. Future checkpoint checks use the relevant path scope.

`check-metadata.json` and `provenance.json` retain focused review and hashes;
timing and full local command outputs are archived under the session label.

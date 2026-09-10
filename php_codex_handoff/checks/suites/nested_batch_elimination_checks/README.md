# Nested-span batch elimination: proof-level checks

## Claim checked

Over F_p, let a single level of ENS blocks have nested input spans
V_1 <= ... <= V_s, and input degrees at most delta. A degree-D
polynomial-calculus refutation of the augmented system can be transformed
into a refutation without these blocks of degree at most D+(p-1)delta.
The base contains Boolean or F_p field equations for every old variable.

The transformation replays the ORIGINAL refutation at each stage. It learns
the inputs of each successive span, then reuses their previously constructed
PC derivations. It does not charge the same selector degree again to all
previous derivations.

For a target f in the current span and nonzero alpha, put
chi_alpha(f) = 1-(f-alpha)^(p-1). In each current/later block, select constant
coefficients in its first extension factor that express f in that block's
input span, and set all other fresh variables to zero. Earlier blocks get
the zero specialization. Multiply each specialized proof line by chi_alpha(f).
Later extension axioms become old field-ideal elements because
chi_alpha(f)(1-f/alpha) = (f^p-f)/alpha. Earlier extension axioms become
chi_alpha(f) times an already learned input. Reuse that input's PC derivation,
then multiply the derived polynomial; DO NOT multiply its entire derivation.
The final line derives chi_alpha(f). Summing alpha*chi_alpha(f) derives f.
Once all inputs have been learned, replay the source proof with all fresh
variables zero to derive 1 from the old axioms alone.

## Test cases

The final suite contains 14 cases over F_2, F_3, and F_5, with 3-5 nested
prefix blocks, accuracies h=1 or h=2, and input degree 1 or 2. The degree-2
cases use g_i=1-x_(2i)*x_(2i+1), genuinely nonlinear functions on the Boolean
domain. The degree-1 cases use g_i=1-x_i.

Base contradictions are unsatisfiable propagation systems: the first truth
polynomial is forced to 1, subsequent truths follow from their predecessors,
and the last truth is forced to 0. Source ENS refutations are constructed by
exact telescoping identities between prefix blocks. Their certificates use
the extension axioms; they are not tests of a proof that simply ignores all
extensions.

Every polynomial-calculus source line and transformed line is independently
replayed using ONLY these primitive rules:
- introduction of an allowed axiom;
- an F_p-linear combination of previous lines;
- multiplication of a previous line by one variable.

The test also verifies each transformed line equals the prescribed selector
times its specialization. Field-ideal identities are implemented by explicit
bounded-degree division by old Boolean equations and then expanded into PC
inferences. The final proof has NO extension axioms among its allowed axioms.

Negative controls verify that earlier learned inputs cannot simply be treated
as elements of the Boolean field ideal. The implementation deliberately
retains and reuses their derivations.

## What is not tested or established

These tests do not prove the theorem in general; the general argument is
mathematical. They do not compute an augmented PHP design, establish a small
chain cover for arbitrary Frege-derived systems, test the optional
bounded-consequence quotient extension of the theorem, or prove an AC0[p]
Frege lower bound. The test base systems have easy PC refutations; no
optimality of the output degree is asserted.

## Implementation and reproducibility

Run `python check_chain.py`. Requires NumPy and Python 3.10+.
Sparse polynomial operations use sorted uint64 Kronecker monomial keys and
vectorized exact integer coefficients modulo p. The exponent base is chosen
above the full degree budget, and its capacity is checked. Independent cases
run in a four-process pool. No floating-point rank tests are used.

`chain_results.json` and `summary.json` contain the final run. An earlier run
used formally quadratic inputs 1-x_i^2; the final run replaces those cases
with the genuinely nonlinear inputs above. Both runs completed without
failure. Both runtimes are included in the timing log.

Timing limitations: the log starts at the first container timestamp and ends
before final-answer generation. Web windows include request, server, network,
and orchestration time together; pure network latency is not observable.
Process-run wall times include startup and worker-pool overhead. Summed
worker elapsed times overlap and must not be added to batch elapsed time.
The overall residual includes reasoning, reading, drafting, and unisolated
orchestration overhead, not a measurement of pure internal reasoning.

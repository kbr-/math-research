# Core-chain / residual-rank batch-elimination checks

This archive accompanies a mathematical derivation in the conversation. It does
not establish a general AC0[p]-Frege lower bound.

## Mathematical statement being checked in special cases

Let extension blocks in one level have input spans V_a and accuracy h_a. Choose
nested subspaces U_1 <= ... <= U_s with U_a <= V_a. Suppose every U_a is generated
by polynomials of degree at most gamma. Let v_(a,1),...,v_(a,r_a) represent a basis
of V_a/U_a, with degrees at most eta_a. Set

    T_a = max(1, eta_a * max(ceil((p-1)*r_a / h_a) - 1, 0)),
    T = max_a T_a.

The derivation in the conversation transforms a degree-D polynomial-calculus
refutation of the extended system into one for the old system of degree at most
T*D + (p-1)*gamma. Old variables must have Boolean or finite-field equations.
The new extension variables must be fresh for this batch.

The tests here concern T=1, including genuinely affine (not just constant)
substitutions and nonlinear inputs. They do not test every parameter regime of
the more general statement or the extension modulo a supplied consequence space.

## Test construction and scope

There are seven independently checked cases over F_2 and F_3, with two or three
blocks. All literal input spans in each case are pairwise incomparable. Their
cores form a chain and their quotients have dimension one.

The source proofs use unsatisfiable propagation systems with additional private
residual variables constrained to zero. Those residual constraints are used by
the SOURCE proof. The new absorption derivations deliberately do not use them:
they use only the previously learned core polynomials and Boolean equations.
Thus these are proof-transformation tests, not PHP degree lower-bound tests.

The checker verifies every primitive polynomial-calculus line (axiom, field-
linear combination, multiplication by one variable), every mapped source line,
and the final extension-free refutation. Negative controls confirm that the
specialized core companions do not vanish modulo Boolean equations alone.

## Files and running

- check_residual_batch.py: current optimized test implementation.
- pc_engine.py: exact sparse-polynomial and primitive PC proof checker, reused
  from the earlier nested-chain test archive.
- results.json / summary.json: results of the final seven-case suite.
- timing.jsonl / timing_report.json: timestamped research-turn intervals.
- test_stdout.txt / test_stderr.txt: final command output and Unix time result.

Run with Python and NumPy:

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python check_residual_batch.py

The implementation vectorizes sparse-polynomial arithmetic and scalar
specialization with NumPy, uses integer modular arithmetic (not floating-point
rank), and runs independent cases in four worker processes.

## Performance history

The first command attempt timed out and yielded no accepted result. Its observed
bracket was about 42 seconds; the requested tool timeout was not the observed
runtime. No workers were left running afterwards. Scalar substitutions were
then moved to a vectorized preprocessing step, before expanding the few affine
substitutions. The next six-case run completed in about 3.18 seconds including
startup. A final seven-case run, adding a high-degree residual/low-degree core
case, completed in about 3.33 seconds including startup. Both successful suites
passed. The timing log includes the unsuccessful attempt.

# Historical checks and local execution

All eleven original archives and their unpacked files are preserved. None was rerun merely to prepare this handoff. The count/scope statements below come from the source manuscript and original reports, not from fresh executions.

| ID | Package | Entry point |
|---|---|---|
| A01 | [annihilating_functional_checks](suites/annihilating_functional_checks/) | `check_generic_functional.py` |
| A02 | [ens_lifting_checks](suites/ens_lifting_checks/) | `ens_lifting_checks/verify_lifting.py` |
| A03 | [factor_packing_lift_checks](suites/factor_packing_lift_checks/) | `factor_packing_lift_checks/checks.py` |
| A04 | [shared_conditioning_packing_checks](suites/shared_conditioning_packing_checks/) | `shared_conditioning_packing/check_packing.py` |
| A05 | [base_aware_lifting_checks](suites/base_aware_lifting_checks/) | `base_aware_lifting_checks/check.py` |
| A06 | [joint_moment_lifting_checks](suites/joint_moment_lifting_checks/) | `joint_moment_lifting/checks.py` |
| A07 | [two_block_lifting_checks](suites/two_block_lifting_checks/) | `checks.py` |
| A08 | [batch_lifting_attack_checks](suites/batch_lifting_attack_checks/) | `batch_lifting_attack/check_prefix_certificate.py` |
| A09 | [nested_batch_elimination_checks](suites/nested_batch_elimination_checks/) | `check_chain.py` |
| A10 | [core_residual_batch_elimination_checks](suites/core_residual_batch_elimination_checks/) | `check_residual_batch.py` |
| A11 | [decomposition_optimization_checks](suites/decomposition_optimization_checks/) | `decomposition_attack/check_decomposition.py` |

## Scope is part of the result

Read the source supplement notes before selecting a suite. A01 checks non-Boolean generic witnesses. A02--A05 mainly check finite-domain nonlinear constructions. A06/A07 include some truncated designs on other unsatisfiable bases, with the restrictions detailed in their notes. A08 checks explicit prefix-pebbling certificates. A09/A10 check primitive-PC transformations on synthetic propagation systems. A11 checks finite-field subspace/decomposition calculations; it does not computationally verify affine rigidity or establish a PHP/ENS refutation.

The complete recorded counts and limitations are in [Appendix B](../manuscript/chapters/11_appendices.md#app-computations). Passing finite cases does not replace the proofs or the imported lower bounds.

## Safe local runner

```bash
python tools/run_check.py --list
python tools/run_check.py --suite A11 --workers 4 --timeout 180
python tools/run_check.py --suite A09 --workers 4 --timeout 180
```

The runner copies the selected suite into `.runs/`, never overwrites historical reports, and writes stdout, stderr, and a structured command/adaptation report. It uses AST-preserving rewrites in disposable copies to cap `ProcessPoolExecutor` workers. For A01 it also replaces the three scripts' obsolete `/mnt/data/research_work` paths with the working-copy directory. Original code and results remain byte-preserved. Timeouts are logged and process groups are terminated where supported.

Use `--prepare-only` to inspect the working copy before execution. A01 has three separate scripts; run the alternatives with `--script check_degree3_binary.py` or `--script check_determinant_chart.py`. The default A01 entry does not automatically run the other two.

NumPy is required for all suites. A01 additionally uses Numba. Independent processes are capped by the runner; BLAS/OMP thread environment variables are set to one. The wrapper does not change the mathematical algorithms, certify the original code as bug-free, or install dependencies.

The main export testing checks the new utilities and format/integrity preservation; it is not a rerun of A01--A11.

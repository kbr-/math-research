# Exact tests for the prefix-block obstruction to generic ENS batching

## What is tested

For a topologically ordered DAG on N vertices with indegree at most two, put

- b_k = 1 - x_k;
- f_k = b_k times the product of x_j over predecessors j of k;
- include the sink axiom x_N and Boolean axioms.

For every prefix {1,...,k}, introduce a fresh accuracy-h ENS block with
inputs b_1,...,b_k. Write

A_k = product_u (1 - sum_{j<=k} r_{k,u,j} b_j),
E_{k,j} = b_j A_k, and A_0 = 1.

Let

U_{k,j} = sum_u r_{k,u,j} product_{v<u}
          (1 - sum_{l<=k} r_{k,v,l} b_l).

Then 1 - A_k = sum_j U_{k,j} b_j. The script substitutes the exact local
identity

b_k A_{k-1} = A_{k-1} f_k
 + b_k sum_{j in pred(k)} (product of earlier predecessor x variables)
   E_{k-1,j}

into

A_{k-1} - A_k =
  sum_{j<k} U_{k,j} E_{k-1,j}
  + U_{k,k} b_k A_{k-1}
  - sum_{j<k} U_{k-1,j} E_{k,j}.

The sum telescopes. The endpoint A_N = A_N x_N + E_{N,N} gives an exact
refutation with certificate degree at most 4h+2. These are identities in
the ordinary polynomial ring; neither Boolean nor field reduction is
used in checking them.

## Verification modes

1. Formal polynomial expansion in 16 small cases over F_2, F_3, F_5,
   and F_7. Packed exponent vectors and coefficient aggregation use
   NumPy arrays and exact modular arithmetic. All summand degree bounds
   are checked. Removing either of two essential terms is checked to
   invalidate the identity (32 negative controls).
2. Batched exact modular evaluation in 16 larger cases, on 8192 arbitrary
   assignments, including non-Boolean old-variable values over odd
   fields. These cover 393216 individual step-identity checks.

The tests do NOT establish the literature lower bound for pebbling,
a lower bound for PHP, or the separately derived PC-based lifting lemma.

## Running

Requires Python 3.10 or later and NumPy. No network access is used.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
    python check_prefix_certificate.py --workers 4 --out results.json

Independent cases are process-parallel; within each case polynomial
products and assignment evaluations are vectorized. The included JSON
records the actual run, including its scope and all case parameters.

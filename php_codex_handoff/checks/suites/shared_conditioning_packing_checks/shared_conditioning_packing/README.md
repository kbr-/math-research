# Shared-conditioning packing checks

This archive tests the following construction for leveled ENS extension systems.
All input polynomials are functions of a common collection of old-variable
features and earlier extension variables. Choose one joint feature cell with
nonzero mass under an old linear functional; let W be its indicator polynomial.
Specialize every level's extension variables to scalars, recursively, so that
all its companion polynomials vanish on that same cell. Then

    Lambda(P) = lambda(W * P(x, beta)) / lambda(W)

annihilates the augmented axioms at degree D when the old design is available
through degree D + deg(W).

Two feature families are checked:

* F_p-valued polynomial features f_j, with indicator
  1 - (f_j - alpha_j)^(p-1) and weight-degree bound
  (p-1) * sum_j deg(f_j).
* Complete states of selected PHP columns. Their indicators are x_ij for an
  occupied column and 1 - sum_i x_ij for an empty column. Conditioning on q
  columns has weight degree q, not q times the number of rows.

The 48 test cases use primes 2, 3, 5, and 7. Each has four levels and eight blocks
per level, including dependence on earlier extension variables. Greedy cell
selection makes no enumeration of all joint feature-value combinations.
Computations use NumPy-vectorized exact modular integer arithmetic and six
independent worker processes; BLAS threading is limited to prevent
oversubscription. Run:

    python check_packing.py

IMPORTANT SCOPE: The tests use signed finite-field combinations of evaluations
on a satisfiable column-exclusive Boolean domain, also satisfying one row-sum
equation. They test the lifting identities, preservation of this old axiom, and
normalization. They do NOT construct a design for the full unsatisfiable PHP
system, show that every BIKPRS family has a small common feature description,
or establish a Frege lower bound. Degree bounds are justified symbolically in
the mathematical argument; exhaustive values check ideal membership in the
finite-domain ideal, not a general truncated-ideal degree theorem.

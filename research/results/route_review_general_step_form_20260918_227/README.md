# Small computations behind the route review of cycle 227 (18 September 2026)

Notebook entry: `entry-2026-09-18-route-review-general-step-form`.

- `quotient_dimension_degree_two.py` (output `.txt`): exact dimension c_2 of polynomials of degree
  at most two modulo the degree-two Nullstellensatz space of the functional unary PHP base over
  F_2, on six, seven and eight holes (435, 861, 1540; the first and last agree with the quotient
  dimensions in the table of the Question H entry), and the working prediction c_2 - 2 c_1 + 3
  for the next step. c_1 = N^2.
- `window_upper_edge_reviewer.py` (output `.txt`): written by the standing reviewer; evaluates the
  recorded dimension criterion M b_k(v - r) < u_k - t_k in logarithms for three parameter sets
  with M = N^2 and reports the least covered rank against the first formulation
  2 D (N+1) ln(4M). Coarse grid in k at the two larger sizes, so those edges are upper estimates.

Both ran through `./compute.sh run route_review_general_step_form_20260918_227 --threads 1`.

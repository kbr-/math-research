# Exterior channel collision cost: correctness review

One fresh-context Codex reviewer, explicitly at medium reasoning, read the complete
stable draft and exact matrix/cofactor/cross-criterion/extraction dependencies.
No other reviewer or new computation was used.

Verdict: PASS on the mathematical argument, with a scope clarification incorporated.

- The divided row's leading coefficient and its nonzero slope difference are correct.
- Both determinant degree arguments and the beta leading-coefficient ratio are correct.
- All four cofactors are nonzero; removing their homogeneous gcd gives the full
  polynomial kernel line.
- The augmented determinant proves valuation zero of the primitive generator's
  moment at the collision. Relabeling covers all three pairs.
- The cross/internal criterion gives exactly V^(2M-2) A w; the polynomial excess
  bound follows.
- Actual extraction at r+1+nu gives a smaller polynomial first-step witness of
  excess nu, proving the original branch inequality.
- No full exterior-row repair or fixed-highest-coordinate condition is silently
  imposed on the original goal.

Scope clarification: M>=5 in the original-witness clause is retained as the
established range of the cited extraction theorem. The channel and moment results
hold for every M>=3. Extending the smaller-size dictionary is not needed for this
checkpoint. No other gap or substantive unused hypothesis was found.

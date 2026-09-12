# MOD recursion with current PC value interfaces

The full analytic proof is in the
[12 September notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-12-virtual-mod-recursion).
This extends the previous conditional Boolean-frame compiler to the recorded
MOD recursion and empty cases. It does not construct a normalized coefficient
assignment, remove the six schema blocks, or supply strict leaf support.

## Exact result and accounting

Choose current representatives a,b,c,m for the final argument and the three
MOD formulas in the recorded unsimplified schema. Their values have degree at
most L; all unit, annihilator, copy, and domain witnesses hold in one retained
system Gamma. Put B=max(A*,U*+L,2L) and R=max(A*,U*+2L,3L).

Use the actual scalar t from the b occurrence. Summing argument-copy proofs
aligns the other scalars with t-1 and t+a-1 through B. The canonical power
(t+a-1)^(p-1) may have degree up to (p-1)L, even if the actual m has degree at
most L; this possible loss of cancellation is kept in the bound.

The recorded interpolation identity and final-argument PC Booleanity give
J=m-ab-(1-a)c through E=max(B,(p-1)L). The computed Boolean disjunction value
q satisfies m-q=J+(a^2-a)(1-b)(1-c). Completed-polynomial reuse then gives
the two direction polynomials through max(E,B,5L), and their equivalence frame
through max(E,B,10L). The actual source root differs from that computed frame
by a proof through max(R,10L), using its current interfaces and copy proofs.

Thus the MOD axiom value fits max(A*,U*+2L,10L,(p-1)L). Including a fixed Boolean
basis of maximum frame leaf count M and MP gives the conditional common bound
max(A*,U*+2L,max(M,10,p-1)L). It adds no proof-height or MOD-arity factor.
The source inputs, current value definitions, and complete witnesses remain
hypotheses; no new ENS family is introduced by the proof itself.

The only non-domain Booleanity request in the scalar interpolation is that of
the final argument. The other MOD value Booleanity comes from its literal field
power. Argument-copy proofs and the exact scalar dependencies cannot be dropped.
The notebook gives explicit analytic countermodels for independently chosen
MOD scalars and for omitting the final argument's Booleanity.

## Evidence and measurement

No new mathematical suite or paper import was needed. The exact six-node
expansion and interpolation are reused from the recorded cycles 08 and 25;
the prior complete accuracy-two evidence retains its original specialization
and NS scope. The present proof permits any supplied current interfaces and
does not claim that the previous NS image certificates automatically survive.
The already checked copy and weighted-unit mechanisms are also reused.

`provenance.json` hashes the complete cycle-25 and cycle-38 evidence, the cycle-39
result record, this README, and the claim index. The notebook contains the full
new argument and its final timing. Command evidence is archived under
`research/provenance/session-records/virtual_mod_recursion_20260912_40/`.

The initial marked reading window also includes the first derivation of the
scalar/degree argument; the phase switch was late and no retrospective split
was invented. Preparation includes the previous checkpoint's archival, audit,
and push. No new dependency, rendering check, or framework rule was introduced.

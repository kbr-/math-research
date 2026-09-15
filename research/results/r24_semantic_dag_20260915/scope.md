# R24 dependency: finite affine DAG registry

Represent a finite DAG by a topological node list Fin S, permitting repeated
references to earlier nodes. Explicit rules: initial clause, semantic weakening,
complementary-parity resolution, and arbitrary binary semantic consequence.
Compress every node to an equivalent subclause of width≤numberoldvariables+1.
Use the checked binary semantic cover to normalize each binary step to one
weakening or two weakenings and one complementary resolution.

One fixed registry uses initialindex J plus FinS×Fin3: one primary clause and
at most two auxiliary clauses per source node. Prove exact slot count|J|+3S,
width/inventory bounds, and primitive PC replay at every D≥4h+1 from actual
initial-value proofs, by induction on original node index with noheightfactor.
Initial clauses are supplied as a family covering the source axiom set by
semantic entailment. This is an explicitly conditional reusable controller;
R24 is complete only after instantiating the actual bit-PHP initial family,
its proved2h+ℓ certificates, paircount binom(m,2), and emptyfinalvalue1.
Previously verified R19–R21 are reused, not formalized anew.
Preliminary source/API reading and broad planning preceded instrumentation.

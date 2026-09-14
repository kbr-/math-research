# H07 exact dependency and scope

Prove the finite F₂ homological cover lemma using H06's supported double chains.
Hypotheses: L_i are subcomplexes covering K; nerve is AcyclicThrough n;
for nonempty J in the nerve, intersection(L,J) is ExactAt r whenever |J|+r≤n.
Conclusion: AcyclicThrough K n. This is the paper's q-acyclicity statement with
n=q+2, and also handles n=0,1 without truncated negative degree conventions.
The empty-face-only intersection is excluded from the nerve, not assumed exact.

Use a direct double-chain chase in place of the appendix spectral sequence.
Induct on b to solve Hu=d, Vu=0 for a horizontally and vertically closed d(a,b),
with a+b<n. At b=0 use nerve exactness. For b>0, H06 gives Hx=d. Inductively
solve Hy=Vx, Vy=0; intersection exactness gives Vz=y. Set u=x+Hz, so Hu=d
and Vu=0. The bound for the vertical filler is (a+2)+(b-1)=a+b+1≤n.
For a K cycle c in cell count k<n, embed it at a=0 and obtain u(1,k).
Use singleton-intersection exactness to fill u vertically; its horizontal image
is the required K filler. H12/H13 and board-specific induction remain excluded.

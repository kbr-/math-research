-- Tree saturation (7 October 2026; cycle bmd-20261007-i).  Tested statement: a boundary point of M_(0,N+1)-bar,
-- given by roots that are polynomials in node-smoothing variables z_1..z_k (all z = 0 at the point, distinct roots
-- for z off the coordinate hyperplanes), lies outside the closure of the contact locus K = {rank A_(R+1) < R},
-- R = binom(N,2).  Test: the saturation of the ideal of maximal minors of A_(R+1) (columns 0..R+1) by z_1...z_k
-- is not contained in (z_1, ..., z_k).  Containment would give an arc of separated configurations inside K tending
-- to the point (curve selection); non-containment means some element of the saturation is a unit at the point, so
-- near the point every configuration off the hyperplanes has full rank.  lambda = 3/2.
-- Usage: M2 --script bmd_tree_saturation.m2 'k' 'list of N root expressions in z_1..z_k' 'label'
-- One run may give several cases separated by ';;' in the second argument, with labels separated by ';;' in the third.
args := drop(scriptCommandLine, 1);
k := value args#0;

S = QQ[z_1..z_k]; use S;
b := n -> if n < 0 then 0_QQ else product(0..n-1, i -> (-3/2 - i) / (i + 1));
H := (X, Y, m) -> sum(0..m, n -> b(n) * b(m - n) * X^n * Y^(m - n));
cases := separate(";;", args#1);
labels := separate(";;", args#2);
for t from 0 to #cases - 1 do (
    pts := value cases#t;
    N := #pts;
    nr := binomial(N, 2);
    prs := flatten apply(N, i -> apply(toList(i+1..N-1), j -> (i, j)));
    A := matrix apply(prs, p -> apply(nr + 2, c -> H(sub(pts#(p#0), S), sub(pts#(p#1), S), c)));
    I := minors(nr, A);
    Is := saturate(I, product(1..k, i -> z_i));
    print(labels#t | ": N = " | toString N | ", roots " | cases#t);
    print("  saturated minor ideal contained in the maximal ideal: " | toString isSubset(Is, ideal(apply(1..k, i -> z_i))));
    print("  codim " | toString codim Is | ", degree " | toString degree Is);
)

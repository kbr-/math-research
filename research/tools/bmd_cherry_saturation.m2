-- Cherry saturation (7 October 2026; cycle bmd-20261007-i).  Tested statement: for a fixed generic cluster D of M
-- roots scaled by x and a cherry {1, 1+e}, the common zero set of all maximal minors of the pair matrix on columns
-- 0..R+1 (R = binom(M+2,2)), off the axes x e = 0, does not accumulate at (x,e) = (0,0).  Equivalently the
-- saturation I : (x e)^oo of the minor ideal is not contained in (x, e).  If it is contained, some arc of
-- separated configurations tends to the cherry point inside the contact locus K.  lambda = 3/2.
-- Usage: M2 --script bmd_cherry_saturation.m2 M d1 ... dM
args := drop(scriptCommandLine, 1);
M := value args#0;
ds := apply(1..M, i -> value args#i);
R := QQ[x, e];
b := k -> if k < 0 then 0_QQ else product(0..k-1, i -> (-3/2 - i) / (i + 1));
H := (X, Y, k) -> sum(0..k, n -> b(n) * b(k - n) * X^n * Y^(k - n));
pts := join(apply(toList ds, d -> x * d), {1_R, 1 + e});
nr := binomial(M + 2, 2);
ncol := nr + 2;
prs := flatten apply(#pts, i -> apply(toList(i+1..#pts-1), j -> (i, j)));
A := matrix apply(prs, p -> apply(ncol, c -> H(pts#(p#0), pts#(p#1), c)));
I := minors(nr, A);
Is := saturate(I, x * e);
inOrigin := isSubset(Is, ideal(x, e));
print("M = " | toString M | ", D = " | toString toList ds | ", minors: " | toString numgens I);
print("  codim of saturated minor ideal: " | toString codim Is | ", degree: " | toString degree Is);
print("  saturated ideal contained in (x,e): " | toString inOrigin);
print("  generators of saturation: " | toString numgens trim Is);
if numgens trim Is <= 6 then print("  " | toString trim Is);

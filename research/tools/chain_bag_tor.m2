-- Route-review test (sequential line review 2, treewidth bridge): chain of three members
-- M_i = F3[x_i,y_i]/(cubes, x_i y_i^2), sharing relations r1 = y1 - x2, r2 = y2 - x3.
-- Computes Tor_1^A(A/J, A/(R)) = Tor_1^{T(R)}(F3, tensor M_i) (lem:relation-space-tor) by degree,
-- for the full chain and for each bag (one relation, the third member's top kept),
-- and the Hilbert functions of the quotients against the product formula.
R = ZZ/3[x1,y1,x2,y2,x3,y3];
A = R/ideal(x1^3,y1^3,x2^3,y2^3,x3^3,y3^3);
J = matrix{{x1*y1^2, x2*y2^2, x3*y3^2}};
tor1 = rels -> (
  C := res(coker J, LengthLimit => 2);
  H := prune HH_1(C ** coker rels);
  apply(toList(0..12), d -> hilbertFunction(d, H)));
hf = rels -> apply(toList(0..12), d -> hilbertFunction(d, coker(J | rels)));
print("full chain Tor_1 by degree 0..12: " | toString tor1(matrix{{y1-x2, y2-x3}}));
print("bag {1,2} (r1) Tor_1:           " | toString tor1(matrix{{y1-x2}}));
print("bag {2,3} (r2) Tor_1:           " | toString tor1(matrix{{y2-x3}}));
print("full quotient HF:               " | toString hf(matrix{{y1-x2, y2-x3}}));
-- product formula: HS(M)/(1+t+t^2)^2 with HS(M_i) = 1+2t+3t^2+t^3
T = ZZ[t];
p = (1+2*t+3*t^2+t^3)^3;
q = (1+t+t^2)^2;
-- power-series division up to degree 12
c = new MutableList from toList(13:0);
pc = apply(toList(0..12), d -> coefficient(t^d, p + t^13));
qc = {1,2,3,2,1};
scan(toList(0..12), d -> c#d = pc#d - sum(toList(1..min(d,4)), j -> qc#j * c#(d-j)));
print("product formula coefficients:   " | toString toList c);
exit 0

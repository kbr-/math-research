-- Test a named possible uniform mechanism against the actual d=2 coefficient:
-- could the first-step ideal be the 3x3-minor ideal of the Hankel matrix of
-- coefficients of (1+c2*T^2+c3*T^3+c4*T^4+c5*T^5)^u, for some exponent u?
-- Necessary condition: its degree-12 minor must equal the recorded unique F12
-- up to scalar.  Test this for ALL u by exact polynomial coefficient equations.
-- First convert F12 to the 10 centered S5-invariant monomials of weight 12.
-- No new cube kernel or degree sweep is run. Full rational output is retained.
B=QQ[e_1..e_4,Degrees=>{1,2,3,4}];
certificateLines=separate("\n",get "research/results/cube-weighted-first-step-resolution-20260926/resolution-qq.txt");
key="TOP_GENERATORS=";
hits=select(certificateLines,l -> substring(0,#key,l)==key);
assert(#hits==1);
gi=matrix value substring(#key,hits#0);
f12=first select(first entries gi,f -> first degree f==12);
es={1_B,e_1,e_2,e_3,e_4,0_B};
mu=e_1/5;
centered=apply(toList(2..5),k -> sum(toList(0..k),j -> binomial(5-j,k-j)*(-mu)^(k-j)*es#j));
C=QQ[x2,x3,x4,x5,Degrees=>{2,3,4,5}];
toB=map(B,C,centered);
mb=basis(12,B); mc=basis(12,C);
coefM=sub(last coefficients(toB mc,Monomials=>mb),QQ);
coefF=sub(last coefficients(matrix{{f12}},Monomials=>mb),QQ);
sol=coefF//coefM;
assert(coefM*sol==coefF);
assert(numcols mc==10 and rank coefM==10);
F12=(mc*sub(sol,C))_(0,0);
assert(toB F12==f12);
<< "PASS centered invariant conversion; basis_size=" << numcols mc << endl;
<< "CENTERED_F12=" << toString F12 << endl;
U=QQ[u];
A=U[c2,c3,c4,c5,Degrees=>{2,3,4,5}];
polyC={1_A,0_A,c2,c3,c4,c5};
h={1_A};
for k from 1 to 7 do h=append(h,sum(toList(1..min(5,k)),j -> ((u+1)*j-k)*polyC#j*h#(k-j))/k);
H=matrix table(3,3,(i,j) -> h#(2+i+j));
minor12=det H;
assert(minor12%u^3==0);
primitiveMinor=minor12//u^3;
toA=map(A,C,{c2,c3,c4,c5});
ma=basis(12,A);
vh=sub(last coefficients(matrix{{primitiveMinor}},Monomials=>ma),U);
vf=sub(last coefficients(matrix{{toA F12}},Monomials=>ma),U);
cross=flatten apply(toList(0..numrows vh-1),i -> apply(toList(i+1..numrows vh-1),j -> vf_(i,0)*vh_(j,0)-vf_(j,0)*vh_(i,0)));
exponentIdeal=ideal cross;
<< "PRIMITIVE_HANKEL_MINOR=" << toString primitiveMinor << endl;
<< "EXPONENT_PROPORTIONALITY_IDEAL=" << toString gens gb exponentIdeal << endl;
<< "DEGREE12_COEFFICIENT_BASIS=" << toString entries ma << endl;
<< "ACTUAL_COEFFICIENTS=" << toString entries vf << endl;
<< "HANKEL_COEFFICIENTS=" << toString entries vh << endl;
if exponentIdeal==ideal(1_U) then (<< "FALSIFIED: no exponent u over the algebraic closure gives the required degree-12 generator" << endl) else (<< "CANDIDATE_EXPONENTS: " << toString factor first first entries gens gb exponentIdeal << endl);
exit 0;

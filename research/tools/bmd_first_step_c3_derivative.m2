-- Test uniform candidate: dF_N/dc3 is in the original first-post-boundary ideal.
-- The existing N5 object is enough to falsify it. Compare two weight12 vectors
-- in its10-dimensional centered space; no new kernel, dimension, or resolution.
B=QQ[e_1..e_4,Degrees=>{1,2,3,4}];
srcLines=separate("\n",get "research/results/cube-four-reflexive-hull-test-20260927/boundary-perfection.txt");
srcKey="BOUNDARY_VECTOR=";
srcHits=select(srcLines,l->substring(0,#srcKey,l)==srcKey);
assert(#srcHits==2);
srcG=matrix apply(value substring(#srcKey,srcHits#1),row->apply(row,f->sub(f,B)));
srcF=srcG_(12,0);
C=QQ[c2,c3,c4,c5,Degrees=>{2,3,4,5}];
es={1_B,e_1,e_2,e_3,e_4,0_B};
cm=map(B,C,apply(toList(2..5),k->sum(toList(0..k),j->binomial(5-j,k-j)*(-e_1/5)^(k-j)*es#j)));
mb=basis(15,B); mc=basis(15,C);
lhs=sub(last coefficients(cm mc,Monomials=>mb),QQ);
rhs=sub(last coefficients(matrix{{srcF}},Monomials=>mb),QQ);
sol=rhs//lhs; assert(lhs*sol==rhs);
fc=(mc*sub(sol,C))_(0,0); assert(cm fc==srcF);
oldLines=separate("\n",get "research/results/cube-first-step-moment-presentation-20260926/centered-hilbert-burch.txt");
oldKey="CENTERED_GENERATOR_12=";
oldHits=select(oldLines,l->substring(0,#oldKey,l)==oldKey);assert(#oldHits==1);
g12=sub(value substring(#oldKey,oldHits#0),C);
cand=diff(c3,fc);assert(degree cand=={12});
bb=basis(12,C);assert(numcols bb==10);
cols=sub(last coefficients(matrix{{g12,cand}},Monomials=>bb),QQ);
rk=rank cols;
<< "CENTERED_BOUNDARY=" << toString fc << endl;
<< "ACTUAL_FIRST_GENERATOR=" << toString g12 << endl;
<< "C3_DERIVATIVE=" << toString cand << endl;
<< "COEFFICIENT_BASIS=" << toString entries bb << endl;
<< "COEFFICIENT_COLUMNS=" << toString entries cols << endl;
<< "RANK=" << rk << endl;
if rk==2 then (
    pair=first select(subsets(10,2),ij->det(submatrix(cols,ij,{0,1}))!=0);
    << "NONZERO_MINOR_ROWS=" << pair << "; VALUE=" << det(submatrix(cols,pair,{0,1})) << endl;
    << "FALSIFIED uniform c3-derivative membership on the existing N5 object." << endl
) else (assert(rk==1); << "PASSED fixed derivative membership; no all-N claim follows." << endl);
exit 0;

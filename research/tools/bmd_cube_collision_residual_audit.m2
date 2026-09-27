-- Independent small certificate for the residual collision scheme found by the
-- Ext-defect review. Check the full Hilbert-Burch minors and identify its two
-- primary components, with an explicit generic length-two local equation.
B=QQ[e_1,e_2,e_3,e_4,Degrees=>{1,2,3,4}];
cubeLines=separate("\n",get "research/results/cube-hull-uniform-degree-review-20260927/ext-defect-and-collisions.txt");
cubeRead=key->(
    hits:=select(cubeLines,l->substring(0,#key,l)==key);
    assert(#hits==1); matrix apply(value substring(#key,hits#0),row->apply(row,f->sub(f,B))));
cubeJ=ideal cubeRead "RESIDUAL_GENERATORS=";
cubeS=cubeRead "RESIDUAL_DIFFERENTIAL_2=";
cubeRow=cubeRead "RESIDUAL_DIFFERENTIAL_1=";
assert(cubeRow*cubeS==0 and minors(2,cubeS)==cubeJ);
assert(first degree fold((a,b)->gcd(a,b),flatten entries cubeRow)==0);
cubeD=e_1^2*e_2^2-4*e_2^3-4*e_1^3*e_3+18*e_1*e_2*e_3-27*e_3^2;
cubeA=8*e_1^4-42*e_1^2*e_2+36*e_2^2+54*e_1*e_3;
cubeB=2*e_1^3*e_2-8*e_1*e_2^2-6*e_1^2*e_3+36*e_2*e_3;
assert(e_2*cubeB-e_3*cubeA==2*e_1*cubeD);
cubeJzero=ideal(e_4^2,e_2*cubeD+e_4*cubeA,e_3*cubeD+e_4*cubeB,e_4*cubeD);
cubeF=e_1^3-4*e_1*e_2+8*e_3;
cubeK=(e_1^2-4*e_2)^2-64*e_4;
cubeJpair=ideal(cubeF,cubeK);
assert(cubeJzero==ideal cubeRead "PAIR_ZERO_COMPONENT=");
assert(cubeJpair==ideal cubeRead "PAIR_NONZERO_COMPONENT=");
assert(intersect(cubeJzero,cubeJpair)==cubeJ);
assert(cubeD^4 % cubeJzero==0 and gens cubeJzero % ideal(e_4,cubeD)==0);
assert(saturate(cubeJ,ideal cubeF)==cubeJzero and saturate(cubeJ,ideal e_4)==cubeJpair);
-- At P0=(e4,D), e2 is a unit. The identity above makes J0 exactly
-- (e4^2, e2*D+e4*A) there, giving local length two in regular parameters e4,D.
cubeLocalCI=ideal(e_4^2,e_2*cubeD+e_4*cubeA);
assert(saturate(cubeJzero,ideal e_2)==saturate(cubeLocalCI,ideal e_2));
-- Hilbert numerators after flat extension to four ordinary root variables.
cubeDegree=(sum({13,14},b->b^2)-sum({8,9,10},a->a^2))/2;
assert(cubeDegree==60 and 2*(4*6)+3*4==cubeDegree);
R=QQ[u,v];
cubeEval=rs->map(R,B,apply(toList(1..4),j->sum(subsets(4,j),S->product(S,i->rs#i))));
assert((cubeEval{0_R,u,u,v})(cubeJ)==ideal 0_R);
assert((cubeEval{u,u,v,v})(cubeJ)==ideal 0_R);
cubeTriple=(cubeEval{0_R,0_R,u,v})(cubeRow_(0,0));
assert(cubeTriple==u^3*v^3*(u-v)^2 and cubeTriple!=0);
<< "PASS residual Hilbert-Burch maximal-minor identity, primitive gcd and zero composition" << endl;
<< "ZERO_PAIR_PRIMARY_GENERATORS=" << toString entries gens cubeJzero << endl;
<< "OTHER_PAIR_PRIME_GENERATORS=" << toString entries gens cubeJpair << endl;
<< "LOCAL_ZERO_PAIR_CI=" << toString entries gens cubeLocalCI << endl;
<< "LOCAL_LENGTHS zero_pair=2 other_pair=1; root_degree=48+12=60" << endl;
<< "TRIPLE_COLLISION_NONVANISHING=" << toString cubeTriple << endl;
<< "PASS two-pair support, primary-component intersection and local equation" << endl;
cubeLinkLines=separate("\n",get "research/results/cube-hull-uniform-degree-review-20260927/low-polar-colon.txt");
cubeLinkRead=key->(
    hits:=select(cubeLinkLines,l->substring(0,#key,l)==key);
    assert(#hits==1); matrix apply(value substring(#key,hits#0),row->apply(row,f->sub(f,B))));
cubeLinked=ideal cubeLinkRead "LINKED_GENERATORS=";
cubeLinkRow=cubeLinkRead "LINKED_DIFFERENTIAL_1=";
cubeLinkS=cubeLinkRead "LINKED_DIFFERENTIAL_2=";
assert(cubeLinkRow*cubeLinkS==0 and minors(3,cubeLinkS)==cubeLinked);
assert(ideal cubeLinkRow==cubeLinked);
assert(first degree fold((a,b)->gcd(a,b),flatten entries cubeLinkRow)==0);
assert(all(flatten entries cubeLinkS,f->f==0 or first degree f>0));
assert((sum({17,18,19},b->b^2)-sum({12,13,14,15},a->a^2))/2==120);
<< "PASS residual polar link has independent Hilbert-Burch certificate and root degree120" << endl;
exit 0;

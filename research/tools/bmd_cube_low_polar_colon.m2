-- Test the ALL-DEGREE formula T=(F,delta F):Q on the retained n4,d2 object,
-- Q=r(r-1)G_(r-2)-delta^2F. The proof uses squarefreeness/transversality,
-- the Abel identity and the old scalar congruence lemma, not this control.
-- Also inspect its actual residual link; no genericity or CM assumption about
-- the three-generator ideal (F,deltaF,Q) is made.
B=QQ[e_1,e_2,e_3,e_4,Degrees=>{1,2,3,4}];
cubeLines=separate("\n",get "research/results/cube-four-reflexive-hull-test-20260927/boundary-perfection.txt");
cubeKey="BOUNDARY_VECTOR="; cubeHits=select(cubeLines,l->substring(0,#cubeKey,l)==cubeKey); assert(#cubeHits==2);
cubeG=matrix apply(value substring(#cubeKey,cubeHits#1),row->apply(row,f->sub(f,B)));
cubeDvals={2*e_2-e_1^2,3*e_3-e_1*e_2,4*e_4-e_1*e_3,-e_1*e_4};
cubeDelta=f->sum(toList(0..3),j->diff(B_j,f)*cubeDvals#j);
cubeF=cubeG_(12,0); cubeDF=cubeDelta cubeF; cubeQ=12*11*cubeG_(10,0)-cubeDelta cubeDF;
assert(first degree gcd(cubeF,cubeDF)==0);
assert(degree cubeF=={15} and degree cubeDF=={16} and degree cubeQ=={17});
cubeOldLines=separate("\n",get "research/results/cube-weighted-first-step-resolution-20260926/resolution-qq.txt");
cubeOldKey="TOP_GENERATORS="; cubeOldHits=select(cubeOldLines,l->substring(0,#cubeOldKey,l)==cubeOldKey);assert(#cubeOldHits==1);
cubeTideal=ideal matrix apply(value substring(#cubeOldKey,cubeOldHits#0),row->apply(row,f->sub(f,B)));
cubeCI=ideal(cubeF,cubeDF);
<< "START low polar colon degrees15,16 by17" << endl << flush;
cubeClock=cpuTime(); cubePolarColon=cubeCI:ideal cubeQ;
assert(cubePolarColon==cubeTideal);
<< "PASS exact low polar colon equals first-step ideal; cpu=" << cpuTime()-cubeClock << endl;
<< "POLAR_EQUATIONS=" << toString entries gens cubeCI << endl;
<< "CORRECTED_SECOND_COEFFICIENT=" << toString cubeQ << endl << flush;
cubeLinked=cubeCI:cubeTideal;
<< "LINK_EQUALS_ORIGINAL=" << (cubeLinked==cubeTideal) << endl;
<< "LINKED_GENERATOR_DEGREES=" << degrees source mingens cubeLinked << endl;
<< "LINKED_GENERATORS=" << toString entries mingens cubeLinked << endl;
<< "POLAR_IS_INTERSECTION=" << (intersect(cubeTideal,cubeLinked)==cubeCI) << endl;
<< "DOUBLE_COLON_RETURNS_ORIGINAL=" << ((cubeCI:cubeLinked)==cubeTideal) << endl;
<< "CORRECTION_IN_ORIGINAL=" << (cubeQ % cubeTideal==0) << endl;
<< "CORRECTION_IN_LINK=" << (cubeQ % cubeLinked==0) << endl << flush;
cubeLinkedRes=res coker gens cubeLinked;
<< "LINKED_BETTI=" << betti cubeLinkedRes << endl;
for j from 1 to length cubeLinkedRes do (
    << "LINKED_DIFFERENTIAL_" << j << "_SOURCE_DEGREES=" << degrees source cubeLinkedRes.dd_j << endl;
    << "LINKED_DIFFERENTIAL_" << j << "=" << toString entries cubeLinkedRes.dd_j << endl;
);
<< "PASS low polar-colon control and residual-link diagnostics complete" << endl;
exit 0;

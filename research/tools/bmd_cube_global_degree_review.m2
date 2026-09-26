-- Route-review falsification tests on retained exact d=2 certificates.
-- (1) Collision-hyperplane gcd: detects all curve components in one plane;
--     full S5 invariance makes all ten collision planes conjugate.
-- (2) Actual normalized reflexive-sheaf sections versus Euler characteristic.
-- No new threshold matrix, no extra parameter cases, no modular lifting.
C=QQ[c2,c3,c4,c5,Degrees=>{2,3,4,5}];
sourceLines=separate("\n",get "research/results/cube-first-step-moment-presentation-20260926/centered-hilbert-burch.txt");
cubeGenerators=apply(toList(12..15),wt -> (
    key:="CENTERED_GENERATOR_"|toString wt|"=";
    hit:=select(sourceLines,l -> substring(0,#key,l)==key);
    assert(#hit==1); value substring(#key,hit#0)));
R=QQ[u,v,w];
cubeRoots={0_R,0_R,u,v,w};
meanRoot=sum cubeRoots/5;
centered=apply(cubeRoots,a -> a-meanRoot);
toCollision=map(R,C,apply(toList(2..5),j -> sum(subsets(5,j),S -> product(S,i -> centered#i))));
cubeRestrictions=apply(cubeGenerators,f->toCollision f);
assert(all(cubeRestrictions,f->f!=0));
cubeCommon=fold(gcd,cubeRestrictions);
<< "COLLISION_ROOTS=(0,0,u,v,w)" << endl;
<< "COLLISION_RESTRICTION_DEGREES=" << apply(cubeRestrictions,degree) << endl;
<< "COLLISION_COMMON_FACTOR=" << factor cubeCommon << endl << flush;
<< "COLLISION_GCD_DEGREE=" << degree cubeCommon << endl << flush;
for j from 0 to 3 do << "COLLISION_GENERATOR_" << j+12 << "=" << toString cubeRestrictions#j << endl;
-- Two codimension-two collision types, retaining their full projective lines.
for datum in {{"3+1+1",{0_R,0_R,0_R,u,v}}, {"2+2+1",{0_R,0_R,u,u,v}}} do (
    rs:=datum#1; av:=sum rs/5; cs:=apply(rs,z -> z-av);
    evalMap:=map(R,C,apply(toList(2..5),j -> sum(subsets(5,j),S -> product(S,i -> cs#i))));
    vals:=apply(cubeGenerators,f->evalMap f);
    << "STRATUM " << datum#0 << " identically_zero=" << apply(vals,f->f==0) << "; gcd=" << factor fold(gcd,vals) << endl << flush;
);
-- O(t) on P3 has h0=max(binomial(t+3,3),0) and Euler polynomial below.
lineH0=t -> if t<0 then 0 else binomial(t+3,3);
lineEuler=t -> (t+1)*(t+2)*(t+3)/6;
targetShifts={5,6,7,7,8}; sourceShifts={10,11,12};
sectionDimension=t -> sum(targetShifts,a->lineH0(t-a))-sum(sourceShifts,a->lineH0(t-a));
eulerDimension=t -> sum(targetShifts,a->lineEuler(t-a))-sum(sourceShifts,a->lineEuler(t-a));
assert(sectionDimension(4)==0 and sectionDimension(5)==1);
assert(sectionDimension(0)==0 and eulerDimension(0)==280);
chernOne=sum sourceShifts-sum targetShifts;
chernTwo=(sum(sourceShifts,a->a^2)-sum(targetShifts,a->a^2))/2;
chernThree=(sum(sourceShifts,a->a^3)-sum(targetShifts,a->a^3))/3;
assert(chernOne==0 and chernTwo==71 and chernThree==840);
for t from -4 to 10 do assert(eulerDimension(t)==(t+1)*(t+2)*(t+3)/3-71*(t+2)+420);
<< "CHERN c1=" << chernOne << " c2=" << chernTwo << " c3=" << chernThree << endl;
<< "NORMALIZED_SHEAF_RESOLUTION source=" << sourceShifts << " target=" << targetShifts << endl;
for t from -4 to 10 do << "SHEAF twist=" << t << " h0=" << sectionDimension t << " Euler=" << eulerDimension t << endl;
-- Finite-state reaction/transfer-matrix bridge: freezing polynomial rates
-- discards their derivative, so matrix Cayley-Hamilton need not annihilate
-- the true differential response. This is the actual n=1,d=1 cube block.
toyRate=matrix{{0_R,0_R},{0_R,u/2}};
toyVector=matrix{{1_R},{1_R}};
toyConnection=z -> matrix apply(entries z,row -> apply(row,f -> -u^2*diff(u,f)))+toyRate*z;
toyFirst=toyConnection toyVector;
toySecond=toyConnection toyFirst;
assert(toyRate^2-(u/2)*toyRate==0);
assert(toySecond-(u/2)*toyFirst==matrix{{0_R},{-u^2/2}});
assert(toySecond+(u/2)*toyFirst==0);
<< "FROZEN_CAYLEY_HAMILTON_RESIDUAL=" << toString entries(toySecond-(u/2)*toyFirst) << endl;
<< "TRUE_MONIC_CONTROL=D^2+(u/2)*D" << endl;
<< "PASS actual sheaf index does not determine existence of global sections; full collision restrictions retained" << endl;
exit 0;

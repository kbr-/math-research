-- Cheap falsifying controls for the coefficient-ring reconstruction review.
-- No dimension series: one smallest six-root deformed zero fibre (predicted
-- length70, top weight13, ambient W rank560/top18); two exact cusp lattices;
-- a nonflat conductor-square loss; Petri-invariant and SLOCC relaxations.
rvClock=cpuTime();
rvR=QQ[t,b,A,B,C,D,Degrees=>{2,1,2,3,4,2}];
rvT=rvR/ideal((ideal(A,B,C,D))^4,6*b^2+t-A-D);
rvF=rvT/ideal(t);rvBasis=basis rvF;
assert(numcols rvBasis==70);
assert((sub(b,rvF))^2!=0 and (sub(b,rvF))^7!=0 and (sub(b,rvF))^8==0);
rvWeights=flatten degrees source rvBasis;assert(max rvWeights==13);
<< "JET_ZERO_FIBRE_LENGTH=" << numcols rvBasis << " MAX_BASIS_WEIGHT=" << max rvWeights
   << " B_NILPOTENCE=8 W_RANK=" << 8*numcols rvBasis << " W_MAX_WEIGHT=" << 5+max rvWeights << endl;
<< "JET_ZERO_FIBRE_BASIS=" << toString entries rvBasis << endl;
rvA=QQ[z,Degrees=>{2}];
rvInc=matrix{{1,0},{0,z}};
rvNormAction=matrix{{0,z^2},{z,0}};
rvCuspAction=matrix{{0,z^3},{1,0}};
assert(entries(rvNormAction*rvInc)==entries(rvInc*rvCuspAction));
<< "CUSP_RAW_DEGREE=" << degree coker rvInc << " BASIS_LENGTH=" << numcols basis coker rvInc << " ANN=" << toString gens annihilator coker rvInc << endl << flush;
assert(numcols basis coker rvInc==1 and annihilator coker rvInc==ideal z);
<< "CUSP_INCLUSION=" << toString entries rvInc << " NORMAL_ACTION=" << toString entries rvNormAction
   << " CUSP_ACTION=" << toString entries rvCuspAction << " QUOTIENT_LENGTH=" << numcols basis coker rvInc << endl;
rvC=QQ[u,v,Degrees=>{2,3}]/ideal(v^2-u^3,u);
assert(numcols basis rvC==2 and v!=0 and v^2==0);
<< "NONFLAT_CONDUCTOR_ORIGINAL_LENGTH=" << numcols basis rvC << " PATCHED_LENGTH=1 KERNEL_GENERATOR=v" << endl;
rvPetri=matrix{{2_QQ},{3_QQ}};
rvReach=any(toList(0..1),i->any(toList(0..1),j->2*i+3*j==1));
assert(not rvReach and rank rvPetri==1);
<< "PETRI_INVARIANT_DIMENSION=" << 1-rank rvPetri << " ONE_REACHABLE=" << rvReach << endl;
assert(det rvInc==z and rank rvInc==2);
rvAtZero=map(QQ,rvA,{0_QQ});assert(rank(rvAtZero rvInc)==1);
<< "SLOCC_GENERIC_RANK=" << rank rvInc << " AT_ZERO_RANK=" << rank(rvAtZero rvInc)
   << " DETERMINANT=" << det rvInc << endl;
<< "PASS cpu=" << cpuTime()-rvClock << endl << flush;
exit 0;

-- Exhaustive encoding audit for the all-dimensional centered connection and
-- its marked polynomial block presentation, on the retained N5 control.
-- Stages: direct centered columns; coefficient derivation and wedge matrix;
-- all three-term identities; divided-power triangular source change;
-- constant-determinant block frame (lengths7,3); boundary relations;
-- the existing monic original order19 endpoint in the same polynomial target.
cubeDriverLines=separate("\n",get "research/tools/bmd_cube_full_cyclic_ext.m2");
cubeDriverStop=first select(toList(0..#cubeDriverLines-1),j->
    substring(0,19,cubeDriverLines#j)=="cubeResolution=res(");
value concatenate apply(take(cubeDriverLines,cubeDriverStop),l->l|"\n");
cubeN=5;cubeKappa=2*c_2/5;
cubeDeltaValues={3*c_3,4*c_4-3*cubeKappa*c_2,5*c_5-2*cubeKappa*c_3,-cubeKappa*c_4};
cubeDelta=f->sum(toList(0..3),j->cubeDeltaValues#j*diff(S_j,f));
cubeDeltaMatrix=M->matrix apply(entries M,row->apply(row,f->cubeDelta f));
cubeTranslationLowering=matrix table(5,5,(i,j)->if i==j-1 then j_S else 0_S);
cubeOneParticle=-cubeZ*diagonalMatrix apply(toList(0..4),j->(j+1/2)_S)-cubeKappa*cubeTranslationLowering;
cubeWedge=matrix table(10,10,(r,c)->(
    a:=(cubePairs#r)#0;b:=(cubePairs#r)#1;
    u:=(cubePairs#c)#0;v:=(cubePairs#c)#1;
    (if b==v then cubeOneParticle_(a,u) else 0_S)
    -(if a==v then cubeOneParticle_(b,u) else 0_S)
    +(if a==u then cubeOneParticle_(b,v) else 0_S)
    -(if b==u then cubeOneParticle_(a,v) else 0_S)
));
cubeNabla=M->cubeDeltaMatrix(M)+cubeWedge*M;
cubeCo1=append(cubeCo1,last(cubeCo1)*(-1/2-16)/17);
cubeCo3=append(cubeCo3,last(cubeCo3)*(-3/2-16)/17);
cubePowers={matrix table(5,1,(i,j)->if i==0 then 1_S else 0_S)};
for j from 1 to 18 do cubePowers=append(cubePowers,cubeZ*last cubePowers);
cubeG17=matrix table(10,1,(r,j)->(
    u:=(cubePairs#r)#0;v:=(cubePairs#r)#1;
    sum(toList(0..17),i->cubeCo1#i*cubeCo3#(17-i)*
        ((cubePowers#i)_(u,0)*(cubePowers#(18-i))_(v,0)
         -(cubePowers#i)_(v,0)*(cubePowers#(18-i))_(u,0)))
));
cubeAllG=cubeA|cubeG17;
for j from 0 to 16 do (
    rhs:=(j+1)*submatrix(cubeAllG,,{j+1});
    if j>0 then rhs=rhs+cubeKappa*(j+2)*submatrix(cubeAllG,,{j-1});
    assert(entries cubeNabla(submatrix(cubeAllG,,{j}))==entries rhs);
);
<< "PASS all170 three-term recurrence entries through pair order16" << endl << flush;
cubeIterates={submatrix(cubeAllG,,{0})};
for j from 1 to 17 do cubeIterates=append(cubeIterates,cubeNabla last cubeIterates);
cubePCols={matrix table(18,1,(i,j)->if i==0 then 1_S else 0_S)};
for j from 0 to 16 do (
    old:=cubePCols#j;
    nxt:=cubeDeltaMatrix(old)+matrix table(18,1,(i,k)->if i==0 then 0_S else old_(i-1,0));
    if j>0 then nxt=nxt-cubeKappa*(j+2)*cubePCols#(j-1);
    cubePCols=append(cubePCols,nxt/(j+1));
);
cubePowerChange=fold((A,B)->A|B,cubePCols);
cubePowerMatrix=fold((A,B)->A|B,cubeIterates);
assert(entries(cubePowerMatrix*cubePowerChange)==entries cubeAllG);
cubeDividedChange=diagonalMatrix apply(toList(0..17),j->(j!)_S)*cubePowerChange;
assert(det cubeDividedChange==1);
<< "PASS all180 source-change entries; divided-power change determinant1" << endl << flush;
cubeHead1=submatrix(cubeAllG,,{0});
cubeHead2=matrix table(10,1,(r,j)->if cubePairs#r=={0,3} then 1_S
    else if cubePairs#r=={1,2} then -(3/10)_S else 0_S);
cubeHeads={cubeHead1,cubeHead2};cubeLengths={7,3};
cubeBlocks=apply(toList(0..1),r->(
    vs:={cubeHeads#r};
    for j from 1 to cubeLengths#r-1 do vs=append(vs,cubeNabla last vs);
    vs
));
cubeFrame=fold((A,B)->A|B,flatten cubeBlocks);
cubeFrameDet=det cubeFrame;
assert(cubeFrameDet!=0 and first degree cubeFrameDet==0);
cubeFrameInverse=id_(S^10)//cubeFrame;
assert(cubeFrame*cubeFrameInverse==id_(S^10));
cubeEnds=fold((A,B)->A|B,apply(cubeBlocks,vs->cubeNabla last vs));
cubeBoundary=cubeFrameInverse*cubeEnds;
cubeZero=map(QQ,S,{0_QQ,0_QQ,0_QQ,0_QQ});
assert(cubeZero cubeBoundary==0);
<< "BLOCK_HEADS=" << toString entries(cubeHead1|cubeHead2) << endl;
<< "BLOCK_LENGTHS={7,3}; head_weights={2,4}; endpoint_weights={9,7}" << endl;
<< "BLOCK_FRAME_DETERMINANT=" << cubeFrameDet << endl;
<< "BLOCK_FRAME=" << toString entries cubeFrame << endl;
<< "BLOCK_BOUNDARY_COORDINATES=" << toString entries cubeBoundary << endl;
<< "CENTERED_WEDGE_CONNECTION=" << toString entries cubeWedge << endl;
<< "DIVIDED_POWER_SOURCE_CHANGE=" << toString entries cubeDividedChange << endl << flush;
cubePairWeights=apply(cubePairs,pr->sum(pr)+1);
cubeGradedA=map(S^(-cubePairWeights),S^(-toList(2..18)),entries cubeA);
cubeGradedG17=map(target cubeGradedA,S^{-19},entries cubeG17);
assert(isHomogeneous cubeGradedA and isHomogeneous cubeGradedG17);
cubeMonicLift=cubeGradedG17//cubeGradedA;
assert isHomogeneous cubeMonicLift;
assert(entries(cubeA*cubeMonicLift)==entries cubeG17);
<< "MONIC_PAIR_ORDER17_LOWER_COEFFICIENTS=" << toString entries(-cubeMonicLift) << endl;
<< "PASS monic original order19,total19 relation in the actual centered columns" << endl;
<< "CENTERED_CURVATURE_COMPLETED cpu=" << cpuTime()-cubeClock << endl << flush;
exit 0;

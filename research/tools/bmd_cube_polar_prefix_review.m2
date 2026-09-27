-- Review the actual two polar conditions on the retained n4,d2 object.
-- General hypothesis tested: is the polar residual partner, off collisions,
-- the rank-drop ideal of columns0..r-2, as suggested by the marked RR pairing?
-- No new parameter cases. Stages: generate prefix in the certified hull frame;
-- eliminate its identity block; compare the residual and prefix saturations.
needsPackage "Elimination";
B=QQ[e_1,e_2,e_3,e_4,Degrees=>{1,2,3,4}];
cubeRead=(path,key)->(
    sourceLines:=separate("\n",get path);
    hits:=select(sourceLines,l->substring(0,#key,l)==key);
    assert(#hits==1); value substring(#key,hits#0));
cubeMat=rows->matrix apply(rows,row->apply(row,f->sub(f,B)));
cubePlain=M->map(B^(numRows M),B^(numColumns M),M);
cubeFrameFile="research/results/cube-four-hull-frame-20260927/frame-and-derivatives.txt";
cubeC=cubePlain cubeMat cubeRead(cubeFrameFile,"HULL_CONNECTION=");
cubeS=cubeMat cubeRead(cubeFrameFile,"HILBERT_BURCH=");
cubeDvals={2*e_2-e_1^2,3*e_3-e_1*e_2,4*e_4-e_1*e_3,-e_1*e_4};
cubeDelta=f->sum(toList(0..3),j->diff(B_j,f)*cubeDvals#j);
cubeDeltaMatrix=M->cubePlain matrix apply(entries M,row->apply(row,cubeDelta));
cubeV=cubePlain matrix table(12,1,(i,j)->if i==0 then 1_B else 0_B);
cubeCols={cubeV};
for j from 1 to 10 do cubeCols=append(cubeCols,(cubeDeltaMatrix(last cubeCols)+cubeC*(last cubeCols))/j);
cubePrefix=fold((a,b)->a|b,cubeCols);
assert(cubePrefix_{0..8}==submatrix(id_(B^12),,toList(0..8)));
cubeSmall=submatrix(cubePrefix,toList(9..11),{9,10});
cubeMinus=minors(2,cubeSmall);
<< "PREFIX_BOTTOM_BLOCK=" << toString entries cubeSmall << endl;
<< "PREFIX_MINOR_GENERATORS=" << toString entries gens cubeMinus << endl;
<< "PREFIX_MINIMAL_DEGREES=" << degrees source mingens cubeMinus << endl;
cubeBZ=B[z]; cubeP=z^4-e_1*z^3+e_2*z^2-e_3*z+e_4;
cubeDisc=sub(discriminant(cubeP,z),B); cubeCollision=e_4*cubeDisc;
cubePolarFile="research/results/cube-hull-uniform-degree-review-20260927/low-polar-colon.txt";
cubePolar=ideal cubeMat cubeRead(cubePolarFile,"POLAR_EQUATIONS=");
cubeDual=ideal cubeMat cubeRead(cubePolarFile,"LINKED_GENERATORS=");
cubeT=ideal cubeMat cubeRead("research/results/cube-weighted-first-step-resolution-20260926/resolution-qq.txt","TOP_GENERATORS=");
cubeBoundary=minors(3,cubeS);
cubeCollisionResidual=cubeBoundary:cubeT;
cubeMinusSat=saturate(cubeMinus,ideal cubeCollision);
cubeDualSat=saturate(cubeDual,ideal cubeCollision);
<< "PREFIX_EQUALS_COLLISION_RESIDUAL=" << (cubeMinus==cubeCollisionResidual) << endl;
<< "PREFIX_SATURATION_UNIT=" << (cubeMinusSat==ideal 1_B) << endl;
<< "DUAL_SATURATION_UNIT=" << (cubeDualSat==ideal 1_B) << endl;
<< "SATURATED_PREFIX_EQUALS_DUAL=" << (cubeMinusSat==cubeDualSat) << endl;
<< "POLAR_SATURATION_EQUALS_FIRST_STEP=" << (saturate(cubePolar,ideal cubeCollision)==cubeT) << endl;
<< "PREFIX_SATURATION_GENERATORS=" << toString entries mingens cubeMinusSat << endl;
<< "DUAL_SATURATION_GENERATORS=" << toString entries mingens cubeDualSat << endl;
assert(cubeMinus==minors(2,submatrix(cubeS,{0,1},)));
assert(cubeMinusSat==cubeMinus);
assert((cubePolar:cubeBoundary)==cubeMinus);
assert(intersect(cubeBoundary,cubeMinus)==cubePolar);
assert(intersect(cubeMinus,cubeCollisionResidual)==cubeDual);
assert((cubeDual:cubeMinus)==cubeCollisionResidual);
assert(cubeMinus!=cubeDual and cubeMinus!=cubeT);
<< "PASS U=U:q^infinity=A:I; A=I intersect U; Tdual=U intersect J; Tdual:U=J" << endl;
cubeMinusRes=res coker gens cubeMinus;
for j from 1 to length cubeMinusRes do (
    << "PREFIX_DIFFERENTIAL_" << j << "_SOURCE_DEGREES=" << degrees source cubeMinusRes.dd_j << endl;
    << "PREFIX_DIFFERENTIAL_" << j << "=" << toString entries cubeMinusRes.dd_j << endl;
);
assert(codim cubeMinus==2 and length cubeMinusRes==2);
assert(ideal gens cubeMinus==minors(2,cubeMinusRes.dd_2));
assert(cubeMinusRes.dd_1*cubeMinusRes.dd_2==0);
<< "PASS prefix resolution maximal-minor certificate, root-space degree60" << endl;
<< "PASS exact prefix and polar-residual comparison" << endl;
exit 0;

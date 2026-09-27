-- Route review: test the intrinsic Ext-defect model, collision separation,
-- exact elimination of free channels, and marked-sector positive Hamiltonian.
-- Reuse the actual n4,d2 boundary Hilbert-Burch matrix and hull connection.
-- No new degree/dimension row: compare the marked next-column annihilator with
-- the independently retained first-step ideal, then saturation and residual.
-- The two finite graded maps (excess11,12) test the operator-insertion bridge,
-- not an alternating-index argument: keep the particular next-column class.
needsPackage "Elimination";
B=QQ[e_1,e_2,e_3,e_4,Degrees=>{1,2,3,4}];
cubeRead=(path,key)->(
    lines:=separate("\n",get path);
    hits:=select(lines,l->substring(0,#key,l)==key);
    assert(#hits==1); value substring(#key,hits#0));
cubeMat=rows->matrix apply(rows,row->apply(row,f->sub(f,B)));
cubePlain=M->map(B^(numrows M),B^(numcols M),M);
cubeFrameFile="research/results/cube-four-hull-frame-20260927/frame-and-derivatives.txt";
cubeS=cubeMat cubeRead(cubeFrameFile,"HILBERT_BURCH=");
cubeC=cubePlain cubeMat cubeRead(cubeFrameFile,"HULL_CONNECTION=");
cubeDeltaValues={2*e_2-e_1^2,3*e_3-e_1*e_2,4*e_4-e_1*e_3,-e_1*e_4};
cubeDelta=f->sum(toList(0..3),j->diff(B_j,f)*cubeDeltaValues#j);
cubeDeltaMatrix=M->cubePlain matrix apply(entries M,row->apply(row,cubeDelta));
cubeV=cubePlain matrix table(12,1,(i,j)->if i==0 then 1_B else 0_B);
cubeNext=cubeV;
for j from 1 to 13 do cubeNext=cubeDeltaMatrix(cubeNext)+cubeC*cubeNext;
cubeNext=cubeNext/(13!);
cubeA=map(B^{ -6,-5,-4 },B^{ -9,-10,-11,-12 },transpose cubeS);
assert isHomogeneous cubeA;
cubeQ=coker cubeA;
cubeW=map(cubeQ,B^{-13},submatrix(cubeNext,toList(9..11),));
assert isHomogeneous cubeW;
<< "MARKED_CLASS=" << toString entries matrix cubeW << endl << flush;
cubeMarkedAnn=ideal gens kernel cubeW;
cubeOldFile="research/results/cube-weighted-first-step-resolution-20260926/resolution-qq.txt";
cubeOldIdeal=ideal cubeMat cubeRead(cubeOldFile,"TOP_GENERATORS=");
assert(cubeMarkedAnn==cubeOldIdeal);
<< "PASS marked Ext class annihilator equals retained first-step ideal" << endl << flush;
cubeBoundary=minors(3,cubeS);
assert(annihilator cubeQ==cubeBoundary);
assert(cubeBoundary!=cubeMarkedAnn);
<< "PASS whole Ext module annihilator differs from marked class annihilator" << endl;
<< "MARKED_ANN_GENERATORS=" << toString entries mingens cubeMarkedAnn << endl << flush;
-- Identity block on the nine free channels makes the Feshbach/Schur reduction
-- polynomial. Eliminating those channels must leave the same source ideal.
cubeFullA=(id_(B^9)++cubePlain cubeA);
cubeFullQ=coker cubeFullA;
cubeFullW=map(cubeFullQ,B^1,cubeNext);
assert(ideal gens kernel cubeFullW==cubeMarkedAnn);
<< "PASS exact free-channel elimination preserves marked coefficient ideal" << endl << flush;
cubeBZ=B[z]; cubeP=z^4-e_1*z^3+e_2*z^2-e_3*z+e_4;
cubeDisc=sub(discriminant(cubeP,z),B); cubeCollision=e_4*cubeDisc;
<< "START boundary saturation by collisions" << endl << flush;
cubeSat=saturate(cubeBoundary,ideal cubeCollision);
<< "SATURATION_EQUALS_FIRST_STEP=" << (cubeSat==cubeMarkedAnn) << endl;
<< "SATURATED_GENERATOR_DEGREES=" << degrees source mingens cubeSat << endl;
<< "SATURATED_GENERATORS=" << toString entries mingens cubeSat << endl << flush;
cubeResidual=cubeBoundary:cubeMarkedAnn;
<< "RESIDUAL_GENERATOR_DEGREES=" << degrees source mingens cubeResidual << endl;
<< "RESIDUAL_GENERATORS=" << toString entries mingens cubeResidual << endl;
<< "INTERSECTION_EQUALS_BOUNDARY=" << (intersect(cubeMarkedAnn,cubeResidual)==cubeBoundary) << endl;
<< "RESIDUAL_COLLISION_SATURATION_UNIT=" << (saturate(cubeResidual,ideal cubeCollision)==ideal 1_B) << endl << flush;
cubeResidualRes=res coker gens cubeResidual;
<< "RESIDUAL_BETTI=" << betti cubeResidualRes << endl;
for j from 1 to length cubeResidualRes do (
    << "RESIDUAL_DIFFERENTIAL_" << j << "_SOURCE_DEGREES=" << degrees source cubeResidualRes.dd_j << endl;
    << "RESIDUAL_DIFFERENTIAL_" << j << "=" << toString entries cubeResidualRes.dd_j << endl;
);
cubeFpair=e_1^3-4*e_1*e_2+8*e_3;
cubeKpair=(e_1^2-4*e_2)^2-64*e_4;
cubePairOffZero=saturate(cubeResidual,ideal e_4);
assert(cubePairOffZero==ideal(cubeFpair,cubeKpair));
cubePairAtZero=saturate(cubeResidual,ideal cubeFpair);
assert(intersect(cubePairAtZero,cubePairOffZero)==cubeResidual);
<< "PAIR_ZERO_COMPONENT=" << toString entries mingens cubePairAtZero << endl;
<< "PAIR_NONZERO_COMPONENT=" << toString entries mingens cubePairOffZero << endl;
<< "PASS residual separates into the two pair-collision orbits" << endl << flush;
-- Finite graded multiplication by the particular marked class. Its exact
-- rational matrix gives a positive Hamiltonian A^t A over R with the same
-- zero states; no Euler characteristic or unmarked Ext dimension is used.
for cubeExcess in {11,12} do (
    act:=matrix apply(entries basis(cubeExcess+13,cubeW),row->apply(row,f->lift(f,QQ)));
    gram:=transpose act*act;
    assert(rank gram==rank act);
    nullity:=numcols act-rank act;
    assert(nullity==(if cubeExcess==11 then 0 else 1));
    << "MARKED_GRADED_MAP excess=" << cubeExcess << " target=" << numrows act << " source=" << numcols act << " rank=" << rank act << " nullity=" << nullity << " gram_rank=" << rank gram << endl;
    << "GRADED_MATRIX=" << toString entries act << endl << flush;
);
<< "PASS Ext-defect review tests complete" << endl;
exit 0;

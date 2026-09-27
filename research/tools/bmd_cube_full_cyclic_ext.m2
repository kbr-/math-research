-- Locate the non-CM defect using the centered filtered column presentation.
-- n4,d2 has five branch roots. Centering descends the entire column cokernel
-- to QQ[c2,c3,c4,c5], not just the top ideal. The binomial source change is
-- checked in all170 entries through exterior order16 (=original order18).
-- Unit row elimination splits seven already generated pair directions,
-- leaving the exact3x10 full-defect presentation, complete by monic order19.
-- Earlier19-row/restored-GB and uncentered3-row resolution attempts timed out.
-- Stages: centered columns, exact anchored comparison, unit elimination,
-- resolution with Hilbert-guided strategy3, dual-complex Ext support.
cubeClock=cpuTime();
S=QQ[c_2..c_5,Degrees=>{2,3,4,5}];
cubePairs=subsets(5,2);
cubeCo1={1_QQ};cubeCo3={1_QQ};
for j from 1 to 16 do (
    cubeCo1=append(cubeCo1,last(cubeCo1)*(-1/2-j+1)/j);
    cubeCo3=append(cubeCo3,last(cubeCo3)*(-3/2-j+1)/j);
);
cubeColumns=(RR,ZZ)->(
    powers:={matrix table(5,1,(i,j)->if i==0 then 1_RR else 0_RR)};
    for j from 1 to 17 do powers=append(powers,ZZ*last powers);
    matrix table(10,17,(r,j)->(
        u:=(cubePairs#r)#0;v:=(cubePairs#r)#1;
        sum(toList(0..j),q->cubeCo1#q*cubeCo3#(j-q)*
            ((powers#q)_(u,0)*(powers#(j-q+1))_(v,0)
             -(powers#q)_(v,0)*(powers#(j-q+1))_(u,0)))
    ))
);
cubeZ=matrix table(5,5,(i,j)->if j<4 then (if i==j+1 then 1_S else 0_S)
    else ({c_5,-c_4,c_3,-c_2,0_S})#i);
cubeA=cubeColumns(S,cubeZ);
B=QQ[e_1..e_4,Degrees=>{1,2,3,4}];
cubeZA=matrix table(5,5,(i,j)->if j<4 then (if i==j+1 then 1_B else 0_B)
    else ({0_B,-e_4,e_3,-e_2,e_1})#i);
cubeAnchored=cubeColumns(B,cubeZA);
cubeMean=e_1/5;cubeEs={1_B,e_1,e_2,e_3,e_4,0_B};
cubeCentered=apply(toList(2..5),j->sum(toList(0..j),i->
    (-cubeMean)^(j-i)*binomial(5-i,j-i)*cubeEs#i));
cubeMap=map(B,S,cubeCentered);
cubeTranslation=matrix table(5,5,(i,j)->if i<=j then binomial(j,i)*(-cubeMean)^(j-i) else 0_B);
cubeU=matrix table(17,17,(i,j)->if i<=j then
    (-1)^(j-i)*binomial(j+2,j-i)*cubeMean^(j-i) else 0_B);
assert(det cubeU==1);
assert(entries cubeAnchored==entries(exteriorPower(2,cubeTranslation)*(cubeMap cubeA)*cubeU));
<< "CENTERING_IDENTITIES=170; polynomial source change determinant1; cpu=" << cpuTime()-cubeClock << endl << flush;
cubePivotRows=apply(toList(1..7),s->first select(toList(0..9),i->sum(cubePairs#i)==s));
cubeOtherRows=select(toList(0..9),i->not member(i,cubePivotRows));
cubeReduced=cubeA;cubeRowChange=id_(S^10);
for j from 0 to 6 do (
    p:=cubePivotRows#j;unit:=cubeReduced_(p,j);
    assert(unit!=0 and first degree unit==0);
    rowP:=submatrix(cubeReduced,{p},)/(lift(unit,QQ));
    changeP:=submatrix(cubeRowChange,{p},)/(lift(unit,QQ));
    cubeRowChange=matrix table(10,10,(r,c)->if r==p then changeP_(0,c)
        else cubeRowChange_(r,c)-cubeReduced_(r,j)*changeP_(0,c));
    cubeReduced=matrix table(10,17,(r,c)->if r==p then rowP_(0,c)
        else cubeReduced_(r,c)-cubeReduced_(r,j)*rowP_(0,c));
);
assert(entries(cubeRowChange*cubeA)==entries cubeReduced);
assert(entries submatrix(cubeReduced,,toList(0..6))==
    entries matrix table(10,7,(i,j)->if i==cubePivotRows#j then 1_S else 0_S));
cubeWeights=apply(cubeOtherRows,i->sum(cubePairs#i)+1);
cubeRaw=submatrix(cubeReduced,cubeOtherRows,toList(7..16));
cubePhi=map(S^(-cubeWeights),S^(-toList(9..18)),entries cubeRaw);
assert(isHomogeneous cubePhi and cubeWeights=={4,5,6});
cubeC=coker cubePhi;
<< "CENTERED_DEFECT_PRESENTATION=" << toString entries cubePhi << endl << flush;
<< "TARGET_DEGREES=" << degrees target cubePhi << " SOURCE_DEGREES=" << degrees source cubePhi << endl;
<< "PRESENTATION_READY cpu=" << cpuTime()-cubeClock << endl << flush;
cubeResolution=res(cubeC,Strategy=>3);
<< "DEFECT_RESOLUTION_LENGTH=" << length cubeResolution << endl;
<< "DEFECT_BETTI=" << betti cubeResolution << endl << flush;
for j from 0 to length cubeResolution do (
    << "FREE_TERM " << j << " DEGREES=" << degrees cubeResolution_j << endl;
    if j>0 then (
        M:=cubeResolution.dd_j;
        assert isHomogeneous M;
        assert all(flatten entries M,f->f==0 or first degree f>0);
        if j>1 then assert(cubeResolution.dd_(j-1)*M==0);
        << "DEFECT_DIFFERENTIAL " << j << "=" << toString entries M << endl << flush;
    );
);
cubeDual=Hom(cubeResolution,S);
for j in {3,4} do (
    E:=prune HH^j cubeDual;
    P:=presentation E;
    << "EXT_INDEX=" << j << " DIMENSION=" << dim E << " DEGREE=" << degree E << endl;
    << "EXT_TARGET_DEGREES=" << degrees target P << endl;
    << "EXT_SOURCE_DEGREES=" << degrees source P << endl;
    << "EXT_PRESENTATION=" << toString entries P << endl;
    << "EXT_ANNIHILATOR=" << toString entries gens annihilator E << endl;
    << "EXT_HILBERT_SERIES=" << toString hilbertSeries E << endl << flush;
);
<< "FULL_CYCLIC_EXT_CONTROL_COMPLETED cpu=" << cpuTime()-cubeClock << endl << flush;
exit 0;

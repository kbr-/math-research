-- Bounded upper-quotient presentation for the actual sixfold kernel problem.
-- The proved normalization resolutions bound generators of U=ker(F->C/K2)
-- by weight18 and its relation generators by weight23 at N6.
-- Construct those full weight spaces over QQ, not a parameter specialization.
-- Stages: checked polynomial core; all residual sources in weights11..18;
-- minimal upper generators; complete relations through23; lifted connection.
-- One shared coefficient matrix per weight; rational linear algebra only.
-- No cyclic closure or complete presentation of K2/H6 is claimed at this stage.
upperClock=cpuTime();
load "research/tools/bmd_six_kernel_model_20261007.m2";
upperControl=bmdBuildKernelSource(5,17);
assert(upperControl#"weights"=={4,5,6});
<< "CONTROL N5 polynomial source and feedback checked" << endl << flush;
upperData=bmdBuildKernelSource(6,19);
upperS=upperData#"ring";upperC=upperData#"coefficients";
upperF=upperData#"module";upperProj=upperData#"projection";
upperCols=upperData#"columns";upperPairs=upperData#"pairs";
upperB=upperData#"connection";upperDelta=upperData#"delta";
upperDer=mat->matrix apply(entries mat,row->apply(row,f->upperDelta f));
upperScript=separate("\n",get "research/tools/bmd_cube_detector_image.m2");
upperEnd=first select(toList(0..#upperScript-1),i->substring(0,4,upperScript#i)=="imR=");
value concatenate apply(take(upperScript,upperEnd),l->l|"\n");
upperXY=upperS[ux,uy,Degrees=>{1,1}];upperX=upperXY_0;upperY=upperXY_1;
upperPoly=z->z^6+sum(toList(2..6),j->(-1)^j*sub(upperC#(j-2),upperXY)*z^(6-j));
upperQ=upperXY/ideal(upperPoly upperX,upperPoly upperY);
upperInto=map(upperQ,imP,apply(upperC,c->sub(c,upperQ))|
    {sub(upperX+upperY,upperQ),sub(upperX*upperY,upperQ)});
upperPair=h->(
    reduced:=lift(sub(upperY-upperX,upperQ)*upperInto h,upperXY);
    matrix table(15,1,(i,j)->sub(coefficient(
        upperX^((upperPairs#i)#0)*upperY^((upperPairs#i)#1),reduced),upperS))
);
upperH={1_imP,-(3/2)*ss};
for j from 1 to 18 do upperH=append(upperH,
    (-(j+3/2)*ss*upperH#j-(j+2)*vv*upperH#(j-1))/(j+1));
for j from 0 to 19 do (
    assert(imL(upperH#j)==0);
    assert(entries(upperPair(upperH#j))==entries((upperData#"pairColumns")#j));
);
upperJoin=(lis,n)->(if #lis==0 then map(upperS^n,upperS^0,0)
    else fold((a,b)->a|b,lis));
upperQQ=(mat,bas)->(
    if numcols mat==0 then map(QQ^(numcols bas),QQ^0,0) else (
        co:=last coefficients(mat,Monomials=>bas);
        assert(entries(bas*co)==entries mat);
        sub(co,QQ)
    )
);
upperU=map(upperF,upperS^0,0);
upperCounts={};
for d from 11 to 18 do (
    us:=flatten entries basis(d-9,imP);
    vs:=flatten entries basis(d-10,imP);
    vals:=apply(us,u->imChi u)|apply(vs,v->dr*imChi v);
    chi:=matrix table(d-8,#vals,(i,j)->lift(coefficient(tr^i*dr^(d-9-i),vals#j),QQ));
    kc:=gens ker chi;
    qs:=apply(us,u->imA5*u)|apply(vs,v->imA6*v);
    assert(#qs<=2000);
    raw:=upperJoin(apply(qs,q->(
        h:=imIntegrate q;assert(imL(h)==q);
        upperProj*upperPair h)),6);
    candidates:=map(upperF,upperS^(apply(toList(0..numcols kc),i->-d)),
        entries((raw*sub(kc,upperS))|upperCols#(d-2)));
    assert(isHomogeneous candidates);
    bas:=basis(d,upperF);
    newQQ:=upperQQ(candidates,bas);
    oldQQ:=upperQQ(upperU*basis(d,source upperU),bas);
    rem:=newQQ%gb oldQQ;
    added:=gens gb rem;
    assert(newQQ%gb(oldQQ|added)==0 and added%gb(oldQQ|newQQ)==0);
    newCols:=map(upperF,upperS^(apply(toList(1..numcols added),i->-d)),
        entries(bas*sub(added,upperS)));
    assert(isHomogeneous newCols);
    upperU=upperU|newCols;
    upperCounts=append(upperCounts,{d,numcols candidates,numcols newCols});
    << "UPPER_GENERATORS weight=" << d << " candidates=" << numcols candidates
       << " new=" << numcols newCols << " total=" << numcols upperU
       << " cpu=" << cpuTime()-upperClock << endl << flush;
);
upperP=source upperU;
upperR=map(upperP,upperS^0,0);
upperBases=new MutableHashTable;upperMatrices=new MutableHashTable;upperTargets=new MutableHashTable;
for d from 11 to 23 do (
    bas:=basis(d,upperP);tbas:=basis(d,upperF);
    aa:=upperQQ(upperU*bas,tbas);
    assert(numrows aa*numcols aa<=3000000);
    upperBases#d=bas;upperMatrices#d=aa;upperTargets#d=tbas;
    kk:=gens ker aa;
    oldQQ:=upperQQ(upperR*basis(d,source upperR),bas);
    added:=gens gb(kk%gb oldQQ);
    assert(kk%gb(oldQQ|added)==0 and added%gb(oldQQ|kk)==0);
    rel:=map(upperP,upperS^(apply(toList(1..numcols added),i->-d)),
        entries(bas*sub(added,upperS)));
    assert(upperU*rel==0 and isHomogeneous rel);
    upperR=upperR|rel;
    << "UPPER_RELATIONS weight=" << d << " rows=" << numrows aa
       << " cols=" << numcols aa << " new=" << numcols rel
       << " cpu=" << cpuTime()-upperClock << endl << flush;
);
upperWeights=flatten degrees upperP;
upperTarget=upperDer upperU+upperB*upperU;
upperLift=map(upperS^(numcols upperU),upperS^(numcols upperU),0);
for d in sort unique apply(upperWeights,w->w+1) do (
    wanted:=select(toList(0..#upperWeights-1),i->upperWeights#i+1==d);
    rhs:=upperQQ(submatrix(upperTarget,,wanted),upperTargets#d);
    sol:=rhs//(upperMatrices#d);
    assert((upperMatrices#d)*sol==rhs);
    lifted:=(upperBases#d)*sub(sol,upperS);
    upperLift=matrix table(#upperWeights,#upperWeights,(i,j)->
        if member(j,wanted) then lifted_(i,position(wanted,k->k==j)) else upperLift_(i,j));
);
assert(entries(upperU*upperLift)==entries upperTarget);
for i from 0 to #upperWeights-1 do for j from 0 to #upperWeights-1 do
    assert(upperLift_(i,j)==0 or first degree upperLift_(i,j)==upperWeights#j+1-upperWeights#i);
upperMarker=map(upperF,upperS^{-11},entries(upperCols#9));
upperMarkerQQ=upperQQ(upperMarker,upperTargets#11);
upperMarkerSol=upperMarkerQQ//(upperMatrices#11);
assert((upperMatrices#11)*upperMarkerSol==upperMarkerQQ);
upperMarkerLift=(upperBases#11)*sub(upperMarkerSol,upperS);
assert(entries(upperU*upperMarkerLift)==entries upperMarker);
<< "UPPER_GENERATOR_WEIGHTS=" << toString upperWeights << endl;
<< "UPPER_RELATION_WEIGHTS=" << toString flatten degrees source upperR << endl;
<< "UPPER_MAP=" << toString entries upperU << endl;
<< "UPPER_RELATIONS=" << toString entries upperR << endl;
<< "UPPER_CONNECTION=" << toString entries upperLift << endl;
<< "CYCLIC_MARKER=" << toString entries upperMarkerLift << endl;
<< "CORE_CONNECTION=" << toString entries upperB << endl;
<< "PAIR_PROJECTION=" << toString entries upperProj << endl;
<< "PASS bounded upper presentation and exact connection lift; cpu=" << cpuTime()-upperClock << endl << flush;
exit 0;

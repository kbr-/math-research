-- Complete six-root coefficient image over A=QQ[c2], not its normalization.
-- Tests the general coefficient-ring reduction and the sixfold boundary model.
-- Target W is free of rank560; its generic quotient rank must be78, image rank6.
-- Stages: one-variable free encoding; exact T-linear cyclic closure; all actual
-- residual source generators in weights11..18; closure under c3,c4,c5,c6;
-- b-normalization enlargement and its finite boundary quotient; graded outputs.
-- Every closure tests full module membership, not only generic rank.
-- Scalar b satisfies the monic degree24 relation p6(b)^4=0, so at most24
-- normalization steps suffice once the actual S-image is stable.
pidClock=cpuTime();
-- The first run completed and certified the target before timing out during source construction.
-- Set this boolean true to rebuild that retained prefix using the bulk encoder.
pidRebuildTarget=false;
pidRebuildImage=false; -- completed source and coefficient closure are retained separately
pidSrc=separate("\n",get "research/tools/bmd_cube_detector_image.m2");
pidEnd=first select(toList(0..#pidSrc-1),i->substring(0,4,pidSrc#i)=="imR=");
value concatenate apply(take(pidSrc,pidEnd),l->l|"\n");
pidBase=QQ[baseT,Degrees=>{2}];
pidPoly=pidBase[jetB,jetA2,jetA3,jetA4,jetD2,Degrees=>{1,2,3,4,2}];
pidPV=gens pidPoly;
pidT=pidPoly/((ideal drop(pidPV,1))^4+ideal(6*pidPV#0^2+sub(pidBase_0,pidPoly)-pidPV#1-pidPV#4));
pidTV=apply(pidPV,v->sub(v,pidT));
pidB=pidTV#0;pidA2=pidTV#1;pidA3=pidTV#2;pidA4=pidTV#3;pidD2=pidTV#4;
pidExps=select(flatten flatten flatten apply(toList(0..3),i->apply(toList(0..3),j->apply(toList(0..3),k->apply(toList(0..3),l->{i,j,k,l})))),e->sum e<4);
assert(#pidExps==35);
pidMons=flatten apply({0,1},i->apply(pidExps,e->pidPV#0^i*product(toList(0..3),j->pidPV#(j+1)^(e#j))));
pidTW=flatten apply({0,1},i->apply(pidExps,e->i+2*e#0+3*e#1+4*e#2+2*e#3));
pidTMons=apply(pidMons,m->sub(m,pidT));assert(#pidMons==70 and max pidTW==13);
pidEncT=f->sub(last coefficients(lift(f,pidPoly),Variables=>pidPV,Monomials=>pidMons),pidBase);
pidZ=pidT[pz];pidZZ=pidZ_0;
pidF=(pidZZ-pidB)^4+pidA2*(pidZZ-pidB)^2-pidA3*(pidZZ-pidB)+pidA4;
pidG=(pidZZ+2*pidB)^2+pidD2;
pidCV=apply(toList(2..6),j->sub((-1)^j*coefficient(pidZZ^(6-j),pidF*pidG),pidT));
assert(pidCV#0==sub(pidBase_0,pidT));
pidXY=pidT[px,py];pidX=pidXY_0;pidY=pidXY_1;
pidQ=pidXY/ideal((pidX-pidB)^4+pidA2*(pidX-pidB)^2-pidA3*(pidX-pidB)+pidA4,(pidY+2*pidB)^2+pidD2);
pidXq=sub(pidX,pidQ);pidYq=sub(pidY,pidQ);
pidToQ=map(pidQ,imP,apply(pidCV,f->sub(f,pidQ))|{pidXq+pidYq,pidXq*pidYq});
pidPW=flatten apply({0,1},j->apply(toList(0..3),i->i+j+1));
pidWW=flatten apply(pidTW,w->apply(pidPW,u->w+u));assert(#pidWW==560 and max pidWW==18);
pidRootMons=flatten apply({0,1},j->apply(toList(0..3),i->pidX^i*pidY^j));
pidPair=f->sub(last coefficients(lift(f,pidXY),Variables=>{pidX,pidY},Monomials=>pidRootMons),pidT);
assert(all(toList(0..7),i->entries pidPair(sub(pidRootMons#i,pidQ))==entries submatrix(id_(pidT^8),,{i})));
pidEnc=f->(
    lifts:=matrix{apply(flatten entries pidPair f,h->lift(h,pidPoly))};
    co:=sub(last coefficients(lifts,Variables=>pidPV,Monomials=>pidMons),pidBase);
    transpose matrix{flatten entries co}
);
pidJoin=lis->if #lis==0 then map(pidBase^560,pidBase^0,0) else fold((a,b)->a|b,lis);
pidMulT=f->sub(last coefficients(matrix{apply(pidTMons,m->lift(f*m,pidPoly))},Variables=>pidPV,Monomials=>pidMons),pidBase);
pidScalarOps=apply(drop(pidCV,1),f->pidMulT(f));
pidBScalar=pidMulT(pidB);
pidCops=apply(pidScalarOps,op->op**id_(pidBase^8));
pidBop=pidBScalar**id_(pidBase^8);
<< "COEFFICIENT_MAP=" << toString apply(pidCV,f->lift(f,pidPoly)) << endl;
<< "COEFFICIENT_OPERATORS_T=" << toString apply(pidScalarOps,op->entries op) << endl;
<< "NORMALIZATION_OPERATOR_T=" << toString entries pidBScalar << endl;
assert(entries pidMulT(pidCV#0)==entries(sub(pidBase_0,pidBase)*id_(pidBase^70)));
<< "ENCODING rows=560 coefficientBasis=70 genericTargetRank=78 genericImageRank=6" << endl << flush;
-- Verify the coefficient derivation preserving the fourth-power jet ideal.
pidDeltaVals={pidPV#0^2+pidPV#1/6-pidPV#4/3,3*pidPV#2-4*pidPV#0*pidPV#1,
    4*pidPV#3-6*pidPV#0*pidPV#2-pidPV#1^2,-8*pidPV#0*pidPV#3-pidPV#1*pidPV#2/2,8*pidPV#0*pidPV#4};
pidRelCheck=12*pidB*sub(pidDeltaVals#0,pidT)+3*pidCV#1-sub(pidDeltaVals#1,pidT)-sub(pidDeltaVals#4,pidT);
assert(pidRelCheck==0);
pidRel=map(pidBase^560,pidBase^0,0);pidStable=false;pidStop=-1;
if not pidRebuildTarget then (
    cacheLines:=separate("\n",get "research/results/cube-six-root-coefficient-image-20260927/target-certificate.txt");
    tag:="TARGET_STABLE_ORDER=13 TARGET_RELATIONS=";
    cacheLine:=first select(cacheLines,l->substring(0,#tag,l)==tag);
    baseT=pidBase_0;
    pidRel=matrix value substring(#tag,cacheLine);pidStable=true;pidStop=13;
    assert(ring pidRel===pidBase);
    << "TARGET_REUSED completed exact closure at order13 from retained target certificate" << endl << flush;
) else (
pidRel=map(pidBase^560,pidBase^0,0);pidStable=false;pidStop=-1;
pidXp={1_pidQ};pidYp={1_pidQ};pidBin={1_QQ};
for order from 0 to 60 do if not pidStable then (
    if order>0 then (
        pidXp=append(pidXp,last(pidXp)*pidXq);pidYp=append(pidYp,last(pidYp)*pidYq);
        pidBin=append(pidBin,last(pidBin)*(-3/2-order+1)/order);
    );
    gg:=(pidYq-pidXq)*sum(toList(0..order),i->pidBin#i*pidBin#(order-i)*pidXp#i*pidYp#(order-i));
    encg:=pidEnc gg;
    if encg%gb pidRel==0 then (pidStable=true;pidStop=order;) else (
        block:=pidJoin apply(pidTMons,m->pidEnc(sub(m,pidQ)*gg));
        pidRel=gens gb(pidRel|block);
        << "TARGET_ORDER=" << order << " GB_COLUMNS=" << numcols pidRel << " CPU=" << cpuTime()-pidClock << endl << flush;
    );
);
);
assert(pidStable and 560-rank pidRel==78);
for op in pidCops|{pidBop} do assert(op*pidRel%gb pidRel==0);
<< "TARGET_STABLE_ORDER=" << pidStop << " TARGET_RELATIONS=" << toString entries pidRel << endl << flush;
pidL=map(pidBase^560,pidBase^0,0);pidClosed=false;pidRounds=0;
if not pidRebuildImage then (
    cacheLines:=separate("\n",get "research/results/cube-six-root-coefficient-image-20260927/image-preimage-certificate.txt");
    tag:="ACTUAL_IMAGE_PREIMAGE=";
    cacheLine:=first select(cacheLines,l->substring(0,#tag,l)==tag);
    baseT=pidBase_0;pidL=matrix value substring(#tag,cacheLine);
    assert(ring pidL===pidBase);
    pidClosed=all(pidCops,op->op*pidL%gb pidL==0);pidRounds=1;
    << "IMAGE_REUSED completed source weights11..18 and full coefficient closure" << endl << flush;
) else (
pidSource=map(pidBase^560,pidBase^0,0);
for d from 11 to 18 do (
    us:=flatten entries basis(d-9,imP);vs:=flatten entries basis(d-10,imP);
    vals:=apply(us,u->imChi u)|apply(vs,v->dr*imChi v);
    chi:=matrix table(d-8,#vals,(i,j)->lift(coefficient(tr^i*dr^(d-9-i),vals#j),QQ));
    kc:=gens ker chi;
    qs:=apply(us,u->imA5*u)|apply(vs,v->imA6*v);
    assert(#qs<=2000);
    raw:=pidJoin apply(qs,q->(
        h:=imIntegrate q;assert(imL(h)==q);
        pidEnc((pidYq-pidXq)*pidToQ h)
    ));
    pidSource=gens gb(pidSource|raw*sub(kc,pidBase));
    << "SOURCE_WEIGHT=" << d << " INPUT_COLUMNS=" << #qs << " GB_COLUMNS=" << numcols pidSource
       << " CPU=" << cpuTime()-pidClock << endl << flush;
);
pidL=gens gb(pidRel|pidSource);pidClosed=false;pidRounds=0;
while not pidClosed and pidRounds<40 do (
    adds:=pidJoin apply(pidCops,op->op*pidL%gb pidL);
    if adds==0 then pidClosed=true else pidL=gens gb(pidL|adds);
    pidRounds=pidRounds+1;
    << "COEFFICIENT_ROUND=" << pidRounds << " GB_COLUMNS=" << numcols pidL << " CPU=" << cpuTime()-pidClock << endl << flush;
);
);
assert(pidClosed and rank pidL-rank pidRel==6);
pidWitnessQ=imA5*(c_3/6-c_2*ss/3-2*ss^3/3+ss*vv);
pidWitness=pidEnc((pidYq-pidXq)*pidToQ(imIntegrate pidWitnessQ));
assert(pidWitness%gb pidL==0 and pidBop*pidWitness%gb pidL!=0);
<< "ACTUAL_IMAGE_PREIMAGE=" << toString entries pidL << endl << flush;
pidNorm=pidL;pidNormClosed=false;pidNormRounds=0;
while not pidNormClosed and pidNormRounds<24 do (
    add:=pidBop*pidNorm%gb pidNorm;
    if add==0 then pidNormClosed=true else pidNorm=gens gb(pidNorm|add);
    pidNormRounds=pidNormRounds+1;
    << "NORMALIZATION_ROUND=" << pidNormRounds << " GB_COLUMNS=" << numcols pidNorm << " CPU=" << cpuTime()-pidClock << endl << flush;
);
assert(pidNormClosed and rank pidNorm==rank pidL);
-- Recover actual homogeneous column weights before graded quotient operations.
pidColWeight=mat->apply(toList(0..numcols mat-1),j->(
    ws:=select(apply(toList(0..559),i->if mat_(i,j)==0 then null else (
        assert(#terms(mat_(i,j))==1);pidWW#i+first degree(mat_(i,j))
    )),w->w=!=null);
    assert(#ws>0 and min ws==max ws);first ws
));
pidW=pidBase^(apply(pidWW,w->-w));
pidGr=mat->map(pidW,pidBase^(apply(pidColWeight mat,w->-w)),entries mat);
pidM=coker pidGr pidRel;
pidIM=prune image map(pidM,pidBase^(apply(pidColWeight pidL,w->-w)),entries pidL);
pidDM=coker pidGr pidL;
pidBoundary=prune image map(pidDM,pidBase^(apply(pidColWeight pidNorm,w->-w)),entries pidNorm);
assert(dim pidBoundary==0);
pidSatRel=saturate(image pidRel,ideal(pidBase_0));
pidInt=gens intersect(image pidL,pidSatRel);
pidTor=prune image map(pidM,pidBase^(apply(pidColWeight pidInt,w->-w)),entries pidInt);
assert(dim pidTor<=0);
pidFreeM=coker pidGr gens pidSatRel;
pidFree=prune image map(pidFreeM,pidBase^(apply(pidColWeight pidL,w->-w)),entries pidL);
assert(rank pidFree==6 and numcols presentation pidFree==0);
<< "NORMALIZATION_PREIMAGE=" << toString entries pidNorm << endl;
<< "IMAGE_PRESENTATION=" << toString entries presentation pidIM << " IMAGE_GENERATOR_WEIGHTS=" << toString degrees pidIM << endl;
<< "FREE_WEIGHTS=" << toString degrees pidFree << endl;
<< "TORSION_LENGTH=" << numcols basis pidTor << " TORSION_WEIGHTS=" << toString degrees source basis pidTor << endl;
<< "TORSION_PRESENTATION=" << toString entries presentation pidTor << endl;
<< "BOUNDARY_LENGTH=" << numcols basis pidBoundary << " BOUNDARY_WEIGHTS=" << toString degrees source basis pidBoundary << endl;
<< "BOUNDARY_PRESENTATION=" << toString entries presentation pidBoundary << endl;
<< "COMPLETE targetRank=" << rank pidM << " imageRank=" << rank pidIM << " coefficientRounds=" << pidRounds
   << " normalizationRounds=" << pidNormRounds << " cpu=" << cpuTime()-pidClock << endl << flush;
exit 0;

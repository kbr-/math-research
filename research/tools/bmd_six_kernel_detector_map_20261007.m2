-- Actual six-root detector map on the certified nineteen-generator upper cover.
-- General reconstruction test: preserve all coefficient actions and the image
-- torsion while preparing the full sixfold kernel, not only generic ranks.
-- Stages: import certified data; polynomial exterior projection; image lift;
-- complete preimage generators through20 and relations through25, justified
-- by the upper extension and the retained image Betti polynomial; connection;
-- the parameter fibre's forced hidden weight16 class.
-- The final cyclic quotient and full k[c2] kernel remain separate.
dkrClock=cpuTime();
dkrRead=(lines,tag)->(
    hits:=select(lines,l->substring(0,#tag,l)==tag);assert(#hits==1);
    substring(#tag,first hits)
);
dkrS=QQ[c_2..c_6,Degrees=>{2,3,4,5,6}];dkrC=gens dkrS;
dkrUpperLines=separate("\n",get "research/results/bmd-six-kernel-presentation-20261007/upper-certificate.txt");
dkrGW=value dkrRead(dkrUpperLines,"UPPER_GENERATOR_WEIGHTS=");
dkrRW=value dkrRead(dkrUpperLines,"UPPER_RELATION_WEIGHTS=");
dkrFW={4,5,6,6,7,8};
dkrF=dkrS^(-dkrFW);dkrP=dkrS^(-dkrGW);
dkrG=map(dkrF,dkrP,entries matrix value dkrRead(dkrUpperLines,"UPPER_MAP="));
dkrR=map(dkrP,dkrS^(-dkrRW),entries matrix value dkrRead(dkrUpperLines,"UPPER_RELATIONS="));
dkrB=matrix value dkrRead(dkrUpperLines,"CORE_CONNECTION=");
dkrProjection=matrix value dkrRead(dkrUpperLines,"PAIR_PROJECTION=");
dkrTheta=matrix value dkrRead(dkrUpperLines,"CYCLIC_MARKER=");
dkrMarker=dkrG*dkrTheta;
assert(numcols dkrG==19 and numcols dkrR==19 and dkrG*dkrR==0);
assert(isHomogeneous dkrG and isHomogeneous dkrR);
dkrKappa=dkrC#0/3;
dkrDrift=apply(toList(2..6),j->
    (if j<6 then (j+1)*dkrC#(j-1) else 0_dkrS)
    -dkrKappa*(7-j)*(if j>2 then dkrC#(j-3) else 0_dkrS));
dkrDelta=f->sum(toList(0..4),j->dkrDrift#j*diff(dkrC#j,f));
dkrDer=mat->matrix apply(entries mat,row->apply(row,f->dkrDelta f));
-- Reuse the exact deformed coefficient encoding, without rebuilding closures.
dkrPidSource=separate("\n",get "research/tools/bmd_cube_coefficient_image_pid.m2");
dkrPidLabel="pidScalarOps=";
dkrPidStop=first select(toList(0..#dkrPidSource-1),i->substring(0,#dkrPidLabel,dkrPidSource#i)==dkrPidLabel);
-- Prefix lookup uses the literal full label, allowing future comment changes.
value concatenate apply(take(dkrPidSource,dkrPidStop),l->l|"\n");
baseT=pidBase_0;
dkrTargetLines=separate("\n",get "research/results/cube-six-root-coefficient-image-20260927/target-certificate.txt");
dkrTargetRel=matrix value dkrRead(dkrTargetLines,"TARGET_STABLE_ORDER=13 TARGET_RELATIONS=");
dkrActionLines=separate("\n",get "research/results/cube-six-root-coefficient-image-20260927/actions-certificate.txt");
dkrImageLine=dkrRead(dkrActionLines,"IMAGE_GENERATOR_WEIGHTS=");
dkrIW=value first separate(" TORSION_INDEX=",dkrImageLine);
dkrTor=value last separate(" TORSION_INDEX=",dkrImageLine);
dkrEmbedding=matrix value dkrRead(dkrActionLines,"IMAGE_EMBEDDING=");
dkrOps=apply(toList(3..6),j->matrix value dkrRead(dkrActionLines,
    "COEFFICIENT_ACTION="|toString j|" MATRIX="));
assert(#dkrIW==7 and dkrIW#dkrTor==14 and numrows dkrEmbedding==560);
dkrColWeights=mat->apply(toList(0..numcols mat-1),j->(
    ws:=select(apply(toList(0..numrows mat-1),i->if mat_(i,j)==0 then null else (
        assert(#terms(mat_(i,j))==1);pidWW#i+first degree mat_(i,j)
    )),w->w=!=null);
    assert(#ws>0 and min ws==max ws);first ws
));
dkrTargetWeights=dkrColWeights dkrTargetRel;
dkrTarget=coker map(pidBase^(-pidWW),pidBase^(-dkrTargetWeights),entries dkrTargetRel);
dkrIPres=matrix table(7,1,(i,j)->if i==dkrTor then baseT else 0_pidBase);
dkrImage=coker map(pidBase^(-dkrIW),pidBase^{-16},entries dkrIPres);
dkrInc=map(dkrTarget,dkrImage,entries dkrEmbedding);
assert(isHomogeneous dkrInc);
assert((dkrEmbedding*dkrIPres)%gb dkrTargetRel==0);
dkrPairs=subsets(toList(0..5),2);
dkrPivotPairs=apply(toList(1..5),j->{0,j})|apply(toList(1..4),j->{j,5});
dkrRest=select(toList(0..14),i->not member(dkrPairs#i,dkrPivotPairs));
dkrSection=submatrix(id_(dkrS^15),,dkrRest);
assert(entries(dkrProjection*dkrSection)==entries id_(dkrS^6));
assert(apply(dkrRest,i->sum(dkrPairs#i)+1)==dkrFW);
dkrToQ=map(pidQ,dkrS,apply(pidCV,c->sub(c,pidQ)));
dkrPairValues=apply(dkrRest,i->(
    p:=dkrPairs#i;pidXq^(p#0)*pidYq^(p#1)-pidXq^(p#1)*pidYq^(p#0)
));
dkrRaw=fold((a,b)->a|b,apply(toList(0..18),j->
    pidEnc sum(toList(0..5),i->dkrToQ(dkrG_(i,j))*dkrPairValues#i)));
dkrRawMap=map(dkrTarget,pidBase^(-dkrGW),entries dkrRaw);
assert(isHomogeneous dkrRawMap);
<< "DETECTOR_BEGIN targetRows=560 sourceColumns=19 cpu=" << cpuTime()-dkrClock << endl << flush;
dkrLift=dkrRawMap//dkrInc;
dkrPhi=(matrix entries dkrLift)%gb dkrIPres;
assert((dkrEmbedding*dkrPhi-dkrRaw)%gb dkrTargetRel==0);
for i from 0 to 6 do for j from 0 to 18 do
    assert(dkrPhi_(i,j)==0 or first degree dkrPhi_(i,j)+dkrIW#i==dkrGW#j);
dkrPowers=apply(dkrOps,op->(
    lis:={id_(pidBase^7)};for i from 1 to 8 do lis=append(lis,last(lis)*op);lis
));
dkrAct=(f,col)->(
    if f==0 then map(pidBase^7,source col,0) else sum(listForm sub(f,dkrS),term->(
        ex:=term#0;assert(all(drop(ex,1),e->e<=8));
        op:=fold((a,b)->a*b,prepend(id_(pidBase^7),
            apply(toList(0..3),j->(dkrPowers#j)#(ex#(j+1)))));
        sub(term#1,pidBase)*baseT^(ex#0)*op*col
    ))
);
dkrImageBasis=d->(
    rows:=select(toList(0..6),i->
        d>=dkrIW#i and (d-dkrIW#i)%2==0 and (i!=dkrTor or d==14));
    if #rows==0 then map(pidBase^7,pidBase^0,0) else
        matrix table(7,#rows,(i,j)->if i==rows#j then
            baseT^((d-dkrIW#i)//2) else 0_pidBase)
);
dkrImageQQ=(mat,d)->(
    reduced:=mat%gb dkrIPres;bas:=dkrImageBasis d;
    rows:=select(toList(0..6),i->
        d>=dkrIW#i and (d-dkrIW#i)%2==0 and (i!=dkrTor or d==14));
    co:=if #rows==0 then map(QQ^0,QQ^(numcols mat),0) else
        matrix table(#rows,numcols mat,(i,j)->
            lift(coefficient(baseT^((d-dkrIW#(rows#i))//2),reduced_(rows#i,j)),QQ));
    assert(entries(bas*sub(co,pidBase))==entries reduced);
    co
);
dkrApplyColumn=col->sum(select(toList(0..18),i->col_(i,0)!=0),
    i->dkrAct(col_(i,0),submatrix(dkrPhi,,{i})));
assert(dkrApplyColumn(dkrTheta)%gb dkrIPres==0);
for j from 0 to numcols dkrR-1 do
    assert(dkrApplyColumn(submatrix(dkrR,,{j}))%gb dkrIPres==0);
<< "DETECTOR_MAP=" << toString entries dkrPhi << endl;
<< "IMAGE_WEIGHTS=" << toString dkrIW << " TORSION_INDEX=" << dkrTor << endl;
<< "PASS detector lifts, upper relations and marker checked" << endl << flush;
dkrQQ=(mat,bas)->(
    if numcols mat==0 then map(QQ^(numcols bas),QQ^0,0) else (
        co:=last coefficients(mat,Monomials=>bas);
        assert(entries(bas*co)==entries mat);sub(co,QQ)
    )
);
dkrV=map(dkrF,dkrS^0,0);
for d from 11 to 20 do (
    sb:=basis(d,dkrP);tb:=basis(d,dkrF);
    images:=if numcols sb==0 then map(pidBase^7,pidBase^0,0)
        else fold((a,b)->a|b,apply(toList(0..numcols sb-1),j->
            dkrApplyColumn(submatrix(sb,,{j}))));
    iq:=dkrImageQQ(images,d);
    if member(d,{12,13,14,15}) then assert(rank iq==numcols(dkrImageBasis d));
    kk:=gens ker iq;
    raw:=dkrG*sb*sub(kk,dkrS);
    newQQ:=dkrQQ(raw,tb);
    oldQQ:=dkrQQ(dkrV*basis(d,source dkrV),tb);
    added:=gens gb(newQQ%gb oldQQ);
    assert(newQQ%gb(oldQQ|added)==0 and added%gb(oldQQ|newQQ)==0);
    cols:=map(dkrF,dkrS^(apply(toList(1..numcols added),i->-d)),
        entries(tb*sub(added,dkrS)));
    assert(isHomogeneous cols);dkrV=dkrV|cols;
    << "KERNEL_PREIMAGE weight=" << d << " candidateSpace=" << numcols sb
       << " imageRank=" << rank iq << " new=" << numcols cols
       << " total=" << numcols dkrV << " cpu=" << cpuTime()-dkrClock << endl << flush;
);
dkrVP=source dkrV;
dkrVR=map(dkrVP,dkrS^0,0);
dkrBases=new MutableHashTable;dkrMatrices=new MutableHashTable;dkrTargets=new MutableHashTable;
for d from 11 to 25 do (
    bas:=basis(d,dkrVP);tb:=basis(d,dkrF);
    aa:=dkrQQ(dkrV*bas,tb);
    assert(numrows aa*numcols aa<=3000000);
    dkrBases#d=bas;dkrMatrices#d=aa;dkrTargets#d=tb;
    kk:=gens ker aa;
    oldQQ:=dkrQQ(dkrVR*basis(d,source dkrVR),bas);
    added:=gens gb(kk%gb oldQQ);
    assert(kk%gb(oldQQ|added)==0 and added%gb(oldQQ|kk)==0);
    rel:=map(dkrVP,dkrS^(apply(toList(1..numcols added),i->-d)),
        entries(bas*sub(added,dkrS)));
    assert(dkrV*rel==0 and isHomogeneous rel);dkrVR=dkrVR|rel;
    << "PREIMAGE_RELATIONS weight=" << d << " rows=" << numrows aa
       << " cols=" << numcols aa << " new=" << numcols rel
       << " cpu=" << cpuTime()-dkrClock << endl << flush;
);
dkrVW=flatten degrees dkrVP;
dkrConnTarget=dkrDer dkrV+dkrB*dkrV;
dkrVH=map(dkrS^(#dkrVW),dkrS^(#dkrVW),0);
for d in sort unique apply(dkrVW,w->w+1) do (
    wanted:=select(toList(0..#dkrVW-1),i->dkrVW#i+1==d);
    rhs:=dkrQQ(submatrix(dkrConnTarget,,wanted),dkrTargets#d);
    sol:=rhs//(dkrMatrices#d);assert((dkrMatrices#d)*sol==rhs);
    lifted:=(dkrBases#d)*sub(sol,dkrS);
    dkrVH=matrix table(#dkrVW,#dkrVW,(i,j)->
        if member(j,wanted) then lifted_(i,position(wanted,k->k==j)) else dkrVH_(i,j));
);
assert(entries(dkrV*dkrVH)==entries dkrConnTarget);
for i from 0 to #dkrVW-1 do for j from 0 to #dkrVW-1 do
    assert(dkrVH_(i,j)==0 or first degree dkrVH_(i,j)==dkrVW#j+1-dkrVW#i);
dkrMarkerQQ=dkrQQ(dkrMarker,dkrTargets#11);
dkrMS=dkrMarkerQQ//(dkrMatrices#11);assert((dkrMatrices#11)*dkrMS==dkrMarkerQQ);
dkrVT=(dkrBases#11)*sub(dkrMS,dkrS);
assert(entries(dkrV*dkrVT)==entries dkrMarker);
<< "PREIMAGE_GENERATOR_WEIGHTS=" << toString dkrVW << endl;
<< "PREIMAGE_RELATION_WEIGHTS=" << toString flatten degrees source dkrVR << endl;
<< "PREIMAGE_MAP=" << toString entries dkrV << endl;
<< "PREIMAGE_RELATIONS=" << toString entries dkrVR << endl;
<< "PREIMAGE_CONNECTION=" << toString entries dkrVH << endl;
<< "PREIMAGE_MARKER=" << toString entries dkrVT << endl << flush;
-- Retain the Tor class: this is base change of the full presentation, not
-- identification with its image in the specialized ambient free module.
dkrA0=QQ[z_3..z_6,Degrees=>{3,4,5,6}];
dkrSpec=map(dkrA0,dkrS,prepend(0_dkrA0,gens dkrA0));
dkrVF0=dkrA0^(-dkrFW);dkrVP0=dkrA0^(-dkrVW);
dkrV0=map(dkrVF0,dkrVP0,entries(dkrSpec dkrV));
dkrVRW=flatten degrees source dkrVR;
dkrVR0=map(dkrVP0,dkrA0^(-dkrVRW),entries(dkrSpec dkrVR));
for d in {15,16,17} do (
    bas:=basis(d,dkrVP0);tb:=basis(d,dkrVF0);
    aa:=dkrQQ(dkrV0*bas,tb);kk:=gens ker aa;
    rel:=dkrQQ(dkrVR0*basis(d,source dkrVR0),bas);
    hidden:=numcols kk-rank rel;
    assert(rel%gb kk==0);
    assert(hidden==(if d==16 then 1 else 0));
    << "PARAMETER_FIBRE weight=" << d << " hidden=" << hidden << endl << flush;
);
<< "PASS actual detector preimage, complete bounded relations, connection and hidden Tor control; cpu="
   << cpuTime()-dkrClock << endl << flush;
exit 0;

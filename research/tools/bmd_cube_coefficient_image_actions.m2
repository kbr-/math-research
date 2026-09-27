-- Extract the original coefficient actions on the minimal A=QQ[c2] image
-- presentation, retaining its embedding. Reuse all completed closures.
actClock=cpuTime();
actSource=separate("\n",get "research/tools/bmd_cube_coefficient_image_pid.m2");
actEnd=first select(toList(0..#actSource-1),i->substring(0,12,actSource#i)=="<< \"ENCODING");
value concatenate apply(take(actSource,actEnd),l->l|"\n");
actLines=separate("\n",get "research/results/cube-six-root-coefficient-image-20260927/pid-certificate.txt");
actGet=tag->matrix value substring(#tag,first select(actLines,l->substring(0,#tag,l)==tag));
baseT=pidBase_0;
pidRel=actGet "TARGET_STABLE_ORDER=13 TARGET_RELATIONS=";
pidL=actGet "ACTUAL_IMAGE_PREIMAGE=";
actStart=first select(toList(0..#actSource-1),i->substring(0,13,actSource#i)=="pidColWeight=");
actStop=first select(toList(0..#actSource-1),i->substring(0,6,actSource#i)=="pidIM=");
value concatenate apply(take(drop(actSource,actStart),actStop-actStart),l->l|"\n");
actRaw=image map(pidM,pidBase^(apply(pidColWeight pidL,w->-w)),entries pidL);
actSmall=prune actRaw;
actInc=map(pidM,actRaw,gens actRaw)*actSmall.cache.pruningMap;
actPres=matrix entries presentation actSmall;
actWeights=flatten degrees actSmall;
assert(#actWeights==7 and numcols actPres==1);
actTorRows=select(toList(0..6),i->actPres_(i,0)!=0);
assert(#actTorRows==1);actTor=first actTorRows;
assert(actWeights#actTor==14 and actPres_(actTor,0)==baseT);
actFree=select(toList(0..6),i->i!=actTor);
actOps={};
for k from 0 to 3 do (
    ambientOp:=map(pidM,pidM,entries(pidCops#k));
    smallOp:=(ambientOp*actInc)//actInc;
    assert((matrix entries(actInc*smallOp-ambientOp*actInc))%gb(matrix entries presentation pidM)==0);
    norm:=(matrix entries smallOp)%gb actPres;
    assert(norm*actPres%gb actPres==0);
    assert(submatrix(norm,{actTor},)==0 and submatrix(norm,,{actTor})==0);
    for i from 0 to 6 do for j from 0 to 6 do if norm_(i,j)!=0 then
        assert(first degree(norm_(i,j))+actWeights#i==actWeights#j+k+3);
    actOps=append(actOps,norm);
    << "COEFFICIENT_ACTION=" << k+3 << " MATRIX=" << toString entries norm << endl << flush;
);
for i from 0 to 3 do for j from i+1 to 3 do assert((actOps#i*actOps#j-actOps#j*actOps#i)%gb actPres==0);
actZero=map(QQ,pidBase,{0_QQ});actConstants=fold((a,b)->a|b,apply(actOps,op->actZero op));
actMinimal=apply(sort unique actWeights,w->{w,#select(actWeights,v->v==w)-rank(submatrix(actConstants,select(toList(0..6),i->actWeights#i==w),))});
<< "IMAGE_GENERATOR_WEIGHTS=" << toString actWeights << " TORSION_INDEX=" << actTor << endl;
<< "FREE_GENERATOR_WEIGHTS=" << toString apply(actFree,i->actWeights#i) << endl;
<< "FREE_COEFFICIENT_ACTIONS=" << toString apply(actOps,op->entries submatrix(op,actFree,actFree)) << endl;
<< "S_MINIMAL_GENERATORS_WEIGHT_MULTIPLICITY=" << toString actMinimal << endl;
<< "IMAGE_EMBEDDING=" << toString entries actInc << endl;
<< "S_SPLITTING=free_A_part_plus_residue_field_weight14 ALL_ACTIONS_COMMUTE=true" << endl;
<< "PASS cpu=" << cpuTime()-actClock << endl << flush;
exit 0;

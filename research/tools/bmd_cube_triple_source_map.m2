-- Map the entire proved six-root residual source (weights11..18) into the
-- saved four-row triple-triple polynomial core. No whole-module Groebner basis.
-- The existing quadratic image has dimension4. Use it to select four actual
-- polynomial source classes, without inferring completeness of their lifts.
-- Stages: exact source kernels/EPD primitives; polynomial projection; complete
-- closure check in the same quadratic Artin algebra; retain actual lifts.
sourceClock=cpuTime();
src=separate("\n",get "research/tools/bmd_cube_detector_image.m2");
cut=first select(toList(0..#src-1),i->substring(0,4,src#i)=="imR=");
value concatenate apply(take(src,cut),line->line|"\n");
R=QQ[A,B,C,D];P=R[t,u];Q=P/ideal(t^3+A*t-B,u^3+C*u-D);
prior=separate("\n",get "research/results/cube-triple-triple-transverse-residual-20260927/deflation-certificate.txt");
readTag=tag->matrix value substring(#tag,first select(prior,line->substring(0,#tag,line)==tag));
project=readTag "PROJECT=";
coreRaw=readTag "CORE_RAW=";
assert(numrows project==4 and numcols project==9);
encode=f->matrix table(9,1,(i,j)->sub(coefficient(t^(i%3)*u^(i//3),lift(f,P)),R));
Z=R[z];poly6=((z+1)^3+A*(z+1)-B)*((z-1)^3+C*(z-1)-D);
cv=apply(toList(2..6),j->sub((-1)^j*coefficient(z^(6-j),poly6),R));
toQ=map(Q,imP,apply(cv,c->sub(c,Q))|{sub(t+u,Q),sub((t-1)*(u+1),Q)});
allSource=map(R^4,R^0,0);sourceWeights={};sourceLabels={};
for d from 11 to 18 do (
    us:=flatten entries basis(d-9,imP);vs:=flatten entries basis(d-10,imP);
    vals:=apply(us,u->imChi u)|apply(vs,v->dr*imChi v);
    chi:=matrix table(d-8,#vals,(i,j)->lift(coefficient(tr^i*dr^(d-9-i),vals#j),QQ));
    kc:=gens ker chi;
    qs:=matrix{apply(us,u->imA5*u)|apply(vs,v->imA6*v)};
    actualQs:=qs*sub(kc,imP);
    assert(numcols actualQs<=2000);
    mapped:=apply(flatten entries actualQs,q->(
        h:=imIntegrate q;assert(imL(h)==q);project*encode(toQ h)
    ));
    if #mapped>0 then allSource=allSource|fold((a,b)->a|b,mapped);
    sourceWeights=sourceWeights|toList(#mapped:d);
    sourceLabels=sourceLabels|apply(toList(0..#mapped-1),j->{d,j});
    << "SOURCE_WEIGHT=" << d << " KERNEL_COLUMNS=" << #mapped
       << " TOTAL_COLUMNS=" << numcols allSource << " CPU=" << cpuTime()-sourceClock << endl << flush;
);
<< "SOURCE_WEIGHTS=" << toString sourceWeights << endl;
<< "SOURCE_LABELS=" << toString sourceLabels << endl;
<< "SOURCE_MATRIX=" << toString entries allSource << endl << flush;
-- Reconstruct only the small core connection; use the retained projection.
alpha=(A-C)/3;leftSlope=alpha+2;rightSlope=alpha-2;
drift={3*B+2*leftSlope*A,3*leftSlope*B-2*A^2/3,
       3*D+2*rightSlope*C,3*rightSlope*D-2*C^2/3};
delta=f->sum(toList(0..3),i->drift#i*diff(R_i,f));
daP=f->sum(toList(0..3),i->sub(drift#i,P)*diff(sub(R_i,P),f));
vT=-t^2+sub(leftSlope,P)*t-2*A/3;
vU=-u^2+sub(rightSlope,P)*u-2*C/3;
connP=f->daP f+vT*diff(t,f)+vU*diff(u,f)+(2*sub(alpha,P)-3*(t+u)/2)*f;
basisQ=flatten apply(toList(0..2),j->apply(toList(0..2),i->sub(t^i*u^j,Q)));
mat=fold((a,b)->a|b,apply(basisQ,f->encode sub(connP lift(f,P),Q)));
coreMat=project*mat*submatrix(id_(R^9),,{3,4,6,7});
art=R/((ideal gens R)^3);
ar=sub(coreRaw,art);asource=sub(allSource,art);
artCon=vv->matrix apply(entries vv,row->apply(row,f->sub(delta lift(f,R),art)))+sub(coreMat,art)*vv;
assert(artCon(ar)%gb ar==0);
assert(numcols basis coker ar==36);
chosen={};current=gens gb ar;
for j from 0 to numcols asource-1 do (
    rem:=submatrix(asource,,{j})%gb current;
    if rem!=0 then (
        chosen=append(chosen,j);current=gens gb(current|rem);
    );
);
assert(#chosen==4);
assert(asource%gb current==0);
assert(numcols basis coker current==32);
selected=submatrix(allSource,,chosen);
assert(all(gens art,a->a*sub(selected,art)%gb ar==0));
<< "QUADRATIC_FULL_LENGTH=36 QUADRATIC_UPPER_LENGTH=32 SOURCE_IMAGE=4" << endl;
<< "SELECTED_COLUMNS=" << chosen << " SELECTED_LABELS=" << apply(chosen,j->sourceLabels#j) << endl;
<< "SELECTED_LIFTS=" << toString entries selected << endl;
<< "CORE_CONNECTION=" << toString entries coreMat << endl;
<< "COMPLETE cpu=" << cpuTime()-sourceClock << endl << flush;
exit 0;

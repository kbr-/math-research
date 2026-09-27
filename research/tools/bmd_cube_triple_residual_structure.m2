-- Extract the full sixteen-dimensional origin module without recomputing
-- cyclic closure. Its certified monomial annihilator reduces the coefficient
-- algebra to16 dimensions, so all subsequent checks are finite exact QQ algebra.
-- Test the specific canonical-module hypothesis by minimal-generator and
-- tsSocle dimensions; do not infer a module isomorphism from length alone.
structureClock=cpuTime();
R=QQ[A,B,C,D];
tsLines=separate("\n",get "research/results/cube-triple-triple-source-relations-20260927/residual-certificate.txt");
tsTag="ORIGIN_PRESENTATION=";
tsPres=matrix value substring(#tsTag,first select(tsLines,l->substring(0,#tsTag,l)==tsTag));
tsAnn=ideal(A^3,A*B,B^2,C^3,C*D,D^2);
T=R/tsAnn;
tsTm=flatten entries basis T;tsLiftMons=apply(tsTm,m->lift(m,R));
assert(#tsTm==16);
tsNt=numrows tsPres;
tsEnc=mm->matrix table(tsNt*16,numcols mm,(i,j)->
    lift(coefficient(tsLiftMons#(i//tsNt),lift(mm_(i%tsNt,j),R)),QQ));
tsPp=sub(tsPres,T);
tsQqrels=fold((a,b)->a|b,apply(tsTm,m->tsEnc(m*tsPp)));
tsQqgb=gens gb tsQqrels;
assert(tsNt*16-rank tsQqgb==16);
-- Choose a constant vector-space complement, retaining original coordinates.
tsChosen={};tsSpan=tsQqgb;
for j from 0 to tsNt*16-1 do if #tsChosen<16 then (
    e:=submatrix(id_(QQ^(tsNt*16)),,{j});
    if rank(tsSpan|e)>numcols tsSpan then (
        tsChosen=append(tsChosen,j);tsSpan=gens gb(tsSpan|e);
    );
);
assert(#tsChosen==16);
tsLiftQQ=submatrix(id_(QQ^(tsNt*16)),,tsChosen);
tsJoint=tsQqgb|tsLiftQQ;
assert(numrows tsJoint==numcols tsJoint and rank tsJoint==numrows tsJoint);
tsJointInv=id_(QQ^(tsNt*16))//tsJoint;
tsProjectQQ=submatrix(tsJointInv,toList(numcols tsQqgb..tsNt*16-1),);
assert(tsProjectQQ*tsQqgb==0 and tsProjectQQ*tsLiftQQ==id_(QQ^16));
tsToT=col->matrix table(tsNt,1,(i,j)->
    sum(toList(0..15),a->sub(col_(a*tsNt+i,0),T)*tsTm#a));
tsLiftT=fold((a,b)->a|b,apply(toList(0..15),j->tsToT submatrix(tsLiftQQ,,{j})));
tsOps=apply(gens T,a->tsProjectQQ*tsEnc(a*tsLiftT));
for i from 0 to 3 do for j from i+1 to 3 do assert(tsOps#i*tsOps#j==tsOps#j*tsOps#i);
assert((tsOps#0)^3==0 and tsOps#0*tsOps#1==0 and (tsOps#1)^2==0);
assert((tsOps#2)^3==0 and tsOps#2*tsOps#3==0 and (tsOps#3)^2==0);
tsTop=16-rank fold((a,b)->a|b,tsOps);
tsSocle=16-rank fold((a,b)->a||b,tsOps);
<< "LENGTH=16 TOP=" << tsTop << " SOCLE=" << tsSocle << endl;
for i from 0 to 3 do << "ACTION=" << R_i << " MATRIX=" << toString entries tsOps#i << endl;
tsPower= id_(QQ^16);tsHilbert={};tsOldDim=16;
for j from 1 to 6 do (
    tsNewer=gens gb fold((a,b)->a|b,apply(tsOps,op->op*tsPower));
    tsNewDim=rank tsNewer;tsHilbert=append(tsHilbert,tsOldDim-tsNewDim);
    tsPower=tsNewer;tsOldDim=tsNewDim;
);
assert(tsOldDim==0);
<< "MAXIMAL_IDEAL_HILBERT=" << tsHilbert << endl;
<< "COMPLETE cpu=" << cpuTime()-structureClock << endl << flush;
exit 0;

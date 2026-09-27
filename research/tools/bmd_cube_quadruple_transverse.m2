-- Complete transverse (4,2) cross-pair module, over QQ[A,B,C,D].
-- The quartic is (X+1)^4+A(X+1)^2-B(X+1)+C; the quadratic
-- is (X-2)^2+D. The cluster centres are fixed, their gap is3.
-- A root drift -X^2+alpha*X+beta preserves both cluster means.
-- On universal alternating columns g_j its connection is triangular:
-- nabla g_j=(j+1)g_(j+1)+alpha(j+2)g_j-beta(j+2)g_(j-1).
-- Thus exact stable cyclic closure computes the original cross-pair defect
-- on this transverse slice. First separate clusters formally; no global
-- grading or connection transfer to other root counts is asserted.
-- Stages: verify tangent drift and quotient matrices; cyclic Groebner closure
-- (eight rows, four parameters, at most thirty iterates); extract H^0_m by
-- module saturation; retain complete presentation and annihilator.
-- Closed fibre must have dimension3. The internal quartic summand has only
-- the top normalization layer, so any finite-length cross residual is K2.
transClock=cpuTime();
R=QQ[A,B,C,D,MonomialOrder=>GRevLex];
alpha=1+A/6-D/3;beta=2-A/3-D/3;
h=alpha+2;transQuadraticSlope=alpha-4;
dr={3*B+2*h*A,4*C+3*h*B-A^2,4*h*C-A*B/2,2*transQuadraticSlope*D};
delta=f->sum(toList(0..3),i->dr#i*diff(R_i,f));
P=R[t,u];ff=t^4+A*t^2-B*t+C;gg=u^2+D;
daP=f->sum(toList(0..3),i->sub(dr#i,P)*diff(sub(R_i,P),f));
vT=-t^2+sub(h,P)*t-A/2;vU=-u^2+sub(transQuadraticSlope,P)*u-D;
assert((daP(ff)+vT*diff(t,ff))%ideal(ff)==0);
assert((daP(gg)+vU*diff(u,gg))%ideal(gg)==0);
Q=P/ideal(ff,gg);basisQ=flatten apply(toList(0..1),j->apply(toList(0..3),i->sub(t^i*u^j,Q)));
encode=f->matrix table(8,1,(i,j)->sub(coefficient(t^(i%4)*u^(i//4),lift(f,P)),R));
connP=f->daP f+vT*diff(t,f)+vU*diff(u,f)+(sub(alpha,P)-(t+u+1)/2)*f;
mat=fold((x,y)->x|y,apply(basisQ,f->encode sub(connP lift(f,P),Q)));
con=vv->matrix apply(entries vv,row->apply(row,f->delta f))+mat*vv;
v=encode sub(3+u-t,Q);
rels=map(R^8,R^0,0);stable=false;stopAt=-1;
for order from 0 to 30 do if not stable then (
    rem:=v%gb rels;
    if rem==0 then (stable=true;stopAt=order;) else (
        rels=gens gb(rels|rem);
        << "ORDER=" << order << " GB_COLUMNS=" << numcols rels << " CPU=" << cpuTime()-transClock << endl << flush;
        v=con v;
    );
);
assert(stable);
assert(con(rels)%gb rels==0);
transAug=map(QQ,R,toList(4:0_QQ));assert(rank(transAug rels)==5);
M=coker rels;
<< "ALPHA=" << alpha << " BETA=" << beta << " DRIFT=" << dr << endl;
<< "CONNECTION=" << toString entries mat << endl;
<< "PRESENTATION=" << toString entries rels << endl;
<< "STABLE_ORDER=" << stopAt << " CLOSED_DEFECT=" << 8-rank(transAug rels) << endl << flush;
sat=saturate(image rels,ideal gens R);
K=prune(sat/image rels);
<< "RESIDUAL_DIM=" << dim K << " RESIDUAL_DEGREE=" << degree K << endl << flush;
<< "SATURATION_GENERATORS=" << toString entries gens sat << endl;
<< "RESIDUAL_PRESENTATION=" << toString entries presentation K << endl;
<< "RESIDUAL_ANNIHILATOR=" << toString gens annihilator K << endl;
if dim K==0 then (
    << "RESIDUAL_BASIS=" << toString entries basis K << endl;
    << "RESIDUAL_LENGTH=" << numcols basis K << endl;
);
<< "COMPLETE cpu=" << cpuTime()-transClock << endl << flush;
exit 0;

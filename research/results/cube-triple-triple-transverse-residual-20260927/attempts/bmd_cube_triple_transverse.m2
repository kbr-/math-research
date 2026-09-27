-- Decide the universal triple-triple residual contribution in characteristic
-- zero. This computes a complete module over QQ[A,B,C,D], not an Artin window.
-- The smallest active core has six roots: cubics at -1 and 1, four transverse
-- coefficients, nine tensor rows. Their internal pair defects vanish.
-- Stages: verify tangent derivation; exact invariant cyclic closure; extract
-- maximal-ideal torsion by saturation and retain its full presentation.
-- The closed fibre must have dimension4. Either zero or nonzero saturation
-- decides the missing support component; no larger root count is requested.
tripleClock=cpuTime();
R=QQ[A,B,C,D,MonomialOrder=>GRevLex];
alpha=(A-C)/3;beta=1-(A+C)/3;
leftSlope=alpha+2;rightSlope=alpha-2;
dr={3*B+2*leftSlope*A,3*leftSlope*B-2*A^2/3,
    3*D+2*rightSlope*C,3*rightSlope*D-2*C^2/3};
delta=f->sum(toList(0..3),i->dr#i*diff(R_i,f));
P=R[t,u];ff=t^3+A*t-B;gg=u^3+C*u-D;
daP=f->sum(toList(0..3),i->sub(dr#i,P)*diff(sub(R_i,P),f));
vT=-t^2+sub(leftSlope,P)*t-2*A/3;
vU=-u^2+sub(rightSlope,P)*u-2*C/3;
assert((daP(ff)+vT*diff(t,ff))%ideal(ff)==0);
assert((daP(gg)+vU*diff(u,gg))%ideal(gg)==0);
Q=P/ideal(ff,gg);
basisQ=flatten apply(toList(0..2),j->apply(toList(0..2),i->sub(t^i*u^j,Q)));
encode=f->matrix table(9,1,(i,j)->sub(coefficient(t^(i%3)*u^(i//3),lift(f,P)),R));
connP=f->daP f+vT*diff(t,f)+vU*diff(u,f)+(sub(alpha,P)-(t+u)/2)*f;
mat=fold((x,y)->x|y,apply(basisQ,f->encode sub(connP lift(f,P),Q)));
con=vv->matrix apply(entries vv,row->apply(row,f->delta f))+mat*vv;
v=encode sub(2+u-t,Q);
rels=map(R^9,R^0,0);stable=false;stopAt=-1;
for order from 0 to 30 do if not stable then (
    rem:=v%gb rels;
    if rem==0 then (stable=true;stopAt=order;) else (
        rels=gens gb(rels|rem);
        << "ORDER=" << order << " GB_COLUMNS=" << numcols rels
           << " CPU=" << cpuTime()-tripleClock << endl << flush;
        v=con v;
    );
);
assert(stable);
assert(con(rels)%gb rels==0);
tripleAug=map(QQ,R,toList(4:0_QQ));
assert(rank(tripleAug rels)==5);
M=coker rels;
<< "ALPHA=" << alpha << " BETA=" << beta << " DRIFT=" << dr << endl;
<< "CONNECTION=" << toString entries mat << endl;
<< "PRESENTATION=" << toString entries rels << endl;
<< "STABLE_ORDER=" << stopAt << " CLOSED_DEFECT=" << 9-rank(tripleAug rels)
   << " CPU=" << cpuTime()-tripleClock << endl << flush;
sat=saturate(image rels,ideal gens R);
K=prune(sat/image rels);
<< "SATURATION_GENERATORS=" << toString entries gens sat << endl;
<< "RESIDUAL_PRESENTATION=" << toString entries presentation K << endl;
<< "RESIDUAL_ANNIHILATOR=" << toString gens annihilator K << endl;
if K==0 then (
    << "RESIDUAL_ZERO=true RESIDUAL_LENGTH=0" << endl;
) else (
    assert(dim K==0);
    << "RESIDUAL_ZERO=false RESIDUAL_DIM=" << dim K
       << " RESIDUAL_LENGTH=" << numcols basis K << endl;
    << "RESIDUAL_BASIS=" << toString entries basis K << endl;
);
<< "COMPLETE cpu=" << cpuTime()-tripleClock << endl << flush;
exit 0;

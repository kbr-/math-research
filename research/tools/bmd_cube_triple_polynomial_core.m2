-- Exact polynomial deflation of the transverse triple-triple cross module.
-- Four parameters, nine tensor rows; the first five universal columns have a
-- constant triangular pivot determinant, leaving a four-row polynomial core.
-- This certifies only the encoding/projection, NOT completeness of columns0..16.
-- The formal root-difference gauge, factor drifts and projection identities are
-- all verified exactly. Full source, connection and eliminated derivatives are
-- retained for subsequent targeted residual computations.
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
-- Multiplication by (Y-X)=2+u-t is a unit at the formal origin.
-- Conjugation changes density to 2*alpha-3*(X+Y)/2 and marker to1.
oldCon=con;
gaugeConnP=f->daP f+vT*diff(t,f)+vU*diff(u,f)+(2*sub(alpha,P)-3*(t+u)/2)*f;
gaugeMat=fold((x,y)->x|y,apply(basisQ,f->encode sub(gaugeConnP lift(f,P),Q)));
gauge=fold((x,y)->x|y,apply(basisQ,f->encode((sub(2+u-t,Q))*f)));
gaugeAug=map(QQ,R,toList(4:0_QQ));assert(det(gaugeAug gauge)!=0);
assert(entries oldCon(gauge)==entries(gauge*gaugeMat));
mat=gaugeMat;v=encode(1_Q);

tripleDirectClock=cpuTime();
coeffs={1_QQ};
for j from 1 to 16 do coeffs=append(coeffs,last(coeffs)*(-3/2-j+1)/j);
columns=apply(toList(0..16),j->encode(sum(toList(0..j),i->coeffs#i*coeffs#(j-i)*sub((t-1)^i*(u+1)^(j-i),Q))));
raw=fold((x,y)->x|y,columns);
<< "DIRECT_COLUMNS=" << numcols raw << " CPU=" << cpuTime()-tripleDirectClock << endl << flush;

pivotRows={0,1,2,5,8};keepRows={3,4,6,7};
head=submatrix(raw,,toList(0..4));
unit=submatrix(head,pivotRows,);low=submatrix(head,keepRows,);
assert(det unit!=0 and all(toList(0..3),i->diff(R_i,det unit)==0));
unitInv=id_(R^5)//unit;
assert(entries(unit*unitInv)==entries id_(R^5));
perm=submatrix(id_(R^9),join(pivotRows,keepRows),);
project=(-low*unitInv|id_(R^4))*perm;
liftCore=submatrix(id_(R^9),,keepRows);
assert(project*head==0);
assert(entries(project*liftCore)==entries id_(R^4));
coreRaw=submatrix(project*raw,,toList(5..16));
coreMat=project*con(liftCore);
coreCon=vv->matrix apply(entries vv,row->apply(row,f->delta f))+coreMat*vv;
<< "POLYNOMIAL_CORE_ROWS=4 UNIT_DETERMINANT=" << det unit
   << " CPU=" << cpuTime()-tripleDirectClock << endl << flush;
<< "CORE_RAW=" << toString entries coreRaw << endl << flush;

out=openOut "research/results/cube-triple-triple-transverse-residual-20260927/core-data.sing";
out << "ring R=0,(A,B,C,D),(ds,C);\n";
out << "matrix conn[4][4]=" << demark(",",apply(flatten entries coreMat,toString)) << ";\n";
out << "ideal drift=" << demark(",",apply(dr,toString)) << ";\n";
out << "matrix rawColumns[4][12]=" << demark(",",apply(flatten entries coreRaw,toString)) << ";\n";
out << "matrix headDerivatives[4][5]=" << demark(",",apply(flatten entries(project*con(head)),toString)) << ";\n";
close out;
<< "PROJECT=" << toString entries project << endl;
<< "HEAD_DERIVATIVES=" << toString entries(project*con(head)) << endl;
<< "CORE_EXPORT_COMPLETE" << endl;
exit 0;

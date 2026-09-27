-- Export the verified nine-row connection to Singular for exact local algebra.
-- Reuse only the tangent/encoding construction, not the slow global closure.
src=separate("\n",get "research/tools/bmd_cube_triple_transverse.m2");
cut=first select(toList(0..#src-1),i->substring(0,5,src#i)=="rels=");
value concatenate apply(take(src,cut),line->line|"\n");
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
rels=gens gb coreRaw;
<< "BATCH_GB_COLUMNS=" << numcols rels << " CPU=" << cpuTime()-tripleDirectClock << endl << flush;
assert(coreCon(rels)%gb rels==0);
assert((project*con(head))%gb rels==0);
<< "INVARIANT=true" << endl << flush;
aug=map(QQ,R,toList(4:0_QQ));assert(rank(aug rels)==0);
<< "PROJECT=" << toString entries project << endl;
<< "CORE_CONNECTION=" << toString entries coreMat << endl;
<< "PRESENTATION=" << toString entries rels << endl << flush;
sat=saturate(image rels,ideal gens R);
K=prune(sat/image rels);
<< "SATURATION_GENERATORS=" << toString entries gens sat << endl;
<< "RESIDUAL_PRESENTATION=" << toString entries presentation K << endl;
<< "RESIDUAL_ANNIHILATOR=" << toString gens annihilator K << endl;
if K==0 then (<< "RESIDUAL_LENGTH=0" << endl;) else (
 assert(dim K==0); << "RESIDUAL_LENGTH=" << numcols basis K << endl;
 << "RESIDUAL_BASIS=" << toString entries basis K << endl;
);
<< "COMPLETE cpu=" << cpuTime()-tripleDirectClock << endl << flush;
exit 0;

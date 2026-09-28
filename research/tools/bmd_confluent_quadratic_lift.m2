-- One exact control of the proposed all-M quadratic lifting mechanism.
-- M=3 is the smallest M in the proved monic-limit/first-jet statements.
-- Centered internal roots {-3,1,2}; no threshold row or dimension sweep.
-- Stages: build actual pair columns once; exact internal elimination;
-- cross Vandermonde normalization; retain epsilon^0..2 in original weight;
-- one rational kernel of the 213-by-109 coefficient map; reconstruct it.
-- Outcomes decide whether the next uniform proof should target a quadratic
-- obstruction or a further lifting identity. No finite result is extrapolated.
kk=QQ;
S=kk[ep,ss,tt];
bmdB={-3_kk,1_kk,2_kk};
bmdM=3;bmdR=3;bmdD=11;
assert(sum bmdB==0 and #unique bmdB==3);
bmdGamma={1_kk};
for j from 0 to bmdD-1 do bmdGamma=append(bmdGamma,-(2*j+3)/(2*j+2)*last bmdGamma);
bmdH=(j,x,y)->sum(toList(0..j),a->bmdGamma#a*bmdGamma#(j-a)*x^a*y^(j-a));
bmdPairs=subsets(toList(0..bmdM-1),2);
bmdInternal=matrix apply(bmdPairs,p->apply(toList(0..bmdD),j->bmdH(j,bmdB#(p#0),bmdB#(p#1))));
bmdU=submatrix(bmdInternal,toList(0..2),toList(0..2));
assert(det bmdU!=0);
bmdC=(inverse bmdU)*bmdInternal;
assert(bmdU*bmdC==bmdInternal);
bmdV=matrix apply(bmdB,b->apply(toList(0..2),a->b^a));
bmdVI=inverse bmdV;
assert(bmdV*bmdVI==id_(target bmdV));
bmdCross=(x)->(
 raw:=matrix apply(bmdB,b->apply(toList(0..bmdD),j->bmdH(j,ep*b,x)));
 mixed:=sub(bmdVI,S)*raw;
 norm:=matrix apply(toList(0..2),a->apply(toList(0..bmdD),j->(
   q:=mixed_(a,j)//ep^a;assert(ep^a*q==mixed_(a,j));q)));
 assert(sub(norm,{ep=>0_S})==matrix apply(toList(0..2),a->apply(toList(0..bmdD),j->if j<a then 0_S else bmdGamma#a*bmdGamma#(j-a)*x^(j-a))));
 norm);
bmdUpper=bmdCross(ss)||bmdCross(tt)||matrix{apply(toList(0..bmdD),j->bmdH(j,ss,tt))};
bmdBmat=matrix apply(toList(0..6),a->apply(toList(bmdR..bmdD),j->
 bmdUpper_(a,j)-sum(toList(0..bmdR-1),i->sub(bmdC_(i,j),S)*ep^(j-i)*bmdUpper_(a,i))));
bmdTargetWeights={0,1,2,0,1,2,0};
bmdSourceWeights=toList(3..11);
bmdMap=map(S^(-bmdTargetWeights),S^(-bmdSourceWeights),bmdBmat);
assert(isHomogeneous bmdMap);
-- At this centered three-root control, both possible linear contributions vanish.
assert(bmdC_(2,3)==0);
assert(diff(ep,bmdBmat)%ideal(ep)==0);
Q=S/ideal(ep^3);
bmdQmap=map(Q^(-bmdTargetWeights),Q^(-bmdSourceWeights),sub(bmdBmat,Q));
bmdSrc=basis(bmdD,source bmdQmap);
bmdTgt=basis(bmdD,target bmdQmap);
assert({numcols bmdTgt,numcols bmdSrc}=={213,109});
bmdProducts=bmdQmap*bmdSrc;
bmdCoeff=last coefficients(bmdProducts,Monomials=>bmdTgt);
assert(bmdTgt*bmdCoeff==bmdProducts);
bmdCoeff=sub(bmdCoeff,kk);
bmdKernel=gens ker bmdCoeff;
assert(bmdCoeff*bmdKernel==0);
bmdLift=bmdSrc*sub(bmdKernel,Q);
assert(bmdQmap*bmdLift==0);
bmdTop=submatrix(bmdLift,{8},toList(0..numcols bmdLift-1));
<< "M=3 CENTERED_INTERNAL_ROOTS=" << toString bmdB << endl;
<< "INTERNAL_DETERMINANT=" << det bmdU << endl;
<< "NORMALIZED_MATRIX=" << toString entries bmdBmat << endl;
<< "COEFFICIENT_ROWS=213 COEFFICIENT_COLUMNS=109" << endl;
<< "KERNEL_DIMENSION=" << numcols bmdKernel << endl;
<< "TOP_COORDINATES=" << toString entries bmdTop << endl;
<< "LIFT_VECTORS=" << toString entries bmdLift << endl;
<< "MONIC_QUADRATIC_LIFT=" << (bmdTop!=0) << endl;
<< "COMPLETED_EXACT_QUADRATIC_CONTROL" << endl;
exit 0;

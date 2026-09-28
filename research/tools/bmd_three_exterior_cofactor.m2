-- One falsifying control for a uniform hypothesis: does the explicit
-- zero-first-coordinate cofactor relation automatically satisfy the existing
-- quadratic cross conditions? Reuse the saved M=3 matrix and marked column.
-- No new dimension, deformation order, kernel, or saturation is computed.
-- Stages: form the four signed 3x3 cofactors, divide the proven alternating
-- factor, reconstruct the exact relation, then evaluate its inverse-Euler
-- moment at s=1 and measure only the required (t-1)^4 divisibility.
-- Failure refutes automatic quadratic compatibility; success would not
-- establish the other pair tests, exterior-row repair, or original descent.
kk=QQ;R=kk[tt,zz];
bmdRead=(file,prefix)->(
 found:=select(lines get file,l->substring(0,#prefix,l)==prefix);
 assert(#found==1);value substring(#prefix,first found));
bmdBase=matrix bmdRead("research/results/cube-exterior-pair-image-20260928/exterior-image.txt","EXTERIOR_MAP=");
bmdLast=matrix bmdRead("research/results/cube-exterior-pair-image-20260928/marked-column.txt","MARKED_COLUMN=");
bmdFull=bmdBase|bmdLast;
bmdTail=submatrix(bmdFull,toList(0..2),toList(1..4));
bmdV=(tt-1)*(zz-1)*(tt-zz);
bmdVector=matrix apply(toList(0..3),j->{
 f:=(-1)^j*det submatrix(bmdTail,toList(0..2),select(toList(0..3),k->k!=j));
 q:=f//bmdV;assert(q*bmdV==f);q});
assert(bmdVector!=0 and bmdTail*bmdVector==0);
T=R[uu];
bmdP=sum(toList(0..3),j->sub(bmdVector_(j,0),T)*uu^(j+1));
bmdF=uu^3*(uu-1)^3*(uu-sub(tt,T))^3*(uu-sub(zz,T))^3*bmdP;
assert(sub(coefficient(uu^0,bmdP),R)==0);
bmdMoment=sum(toList(0..16),j->sub(coefficient(uu^j,bmdF),R)/(j-3/2));
-- beta=-1/2, hence E+beta-1=E-3/2.
bmdVal=0;bmdRem=bmdMoment;
while bmdRem!=0 and sub(bmdRem,{tt=>1_R})==0 do (
 q:=bmdRem//(tt-1);assert(q*(tt-1)==bmdRem);
 bmdRem=q;bmdVal=bmdVal+1);
<< "M=3 REUSED_ZERO_FIRST_COORDINATE_COFACTOR" << endl;
<< "COFACTOR_VECTOR=" << toString entries bmdVector << endl;
<< "EXACT_KERNEL_RECONSTRUCTION=PASS" << endl;
<< "MOMENT_AT_s=1=" << toString bmdMoment << endl;
<< "MOMENT_ZERO=" << (bmdMoment==0) << endl;
<< "COLLISION_VALUATION=" << bmdVal << endl;
<< "REQUIRED_COLLISION_POWER=4" << endl;
<< "FIRST_PAIR_QUADRATIC_COMPATIBLE=" << (bmdMoment==0 or bmdVal>=4) << endl;
<< "FIRST_NONZERO_COLLISION_COEFFICIENT=" << toString sub(bmdRem,{tt=>1_R}) << endl;
<< "COMPLETED_EXACT_COFACTOR_TEST" << endl;
exit 0;

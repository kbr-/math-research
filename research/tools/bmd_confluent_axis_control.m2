-- Falsifying control for the proposed uniform axis constraint st | A.
-- Reuse the complete exact normalized M=3 matrix from the earlier run.
-- Binary excess two is the first degree admitting the second generator J;
-- the earlier excess-zero test cannot test its diagonal cancellation.
-- One 255-by-162 rational kernel modulo epsilon^3 is computed. A nonzero
-- epsilon-zero projection would refute the proposed no-limit bound below4.
-- Higher-epsilon relations remain as a nonvacuous positive kernel control.
kk=QQ;
S=kk[ep,ss,tt];
bmdText=get "research/results/cube-two-root-quadratic-20260928/quadratic-control.txt";
bmdPrefix="NORMALIZED_MATRIX=";
bmdLines=select(lines bmdText,l->substring(0,#bmdPrefix,l)==bmdPrefix);
assert(#bmdLines==1);
bmdBmat=matrix value substring(#bmdPrefix,first bmdLines);
assert({numrows bmdBmat,numcols bmdBmat}=={7,9});
bmdTargetWeights={0,1,2,0,1,2,0};
bmdSourceWeights=toList(3..11);
Q=S/ideal(ep^3);
bmdMap=map(Q^(-bmdTargetWeights),Q^(-bmdSourceWeights),sub(bmdBmat,Q));
assert(isHomogeneous bmdMap);
bmdSrc=basis(13,source bmdMap);
bmdTgt=basis(13,target bmdMap);
assert({numcols bmdTgt,numcols bmdSrc}=={255,162});
bmdProducts=bmdMap*bmdSrc;
bmdCoeff=last coefficients(bmdProducts,Monomials=>bmdTgt);
assert(bmdTgt*bmdCoeff==bmdProducts);
bmdCoeff=sub(bmdCoeff,kk);
bmdK=gens ker bmdCoeff;
assert(bmdCoeff*bmdK==0);
bmdLift=bmdSrc*sub(bmdK,Q);
assert(bmdMap*bmdLift==0);
bmdInitial=sub(bmdLift,{ep=>0_Q});
<< "M=3 REUSED_MATRIX=quadratic-control.txt BINARY_EXCESS=2" << endl;
<< "ROWS=255 COLUMNS=162 KERNEL_DIMENSION=" << numcols bmdK << endl;
<< "ALL_INITIAL_LIMITS_ZERO=" << (bmdInitial==0) << endl;
<< "LIFT_VECTORS=" << toString entries bmdLift << endl;
<< "INITIAL_VECTORS=" << toString entries bmdInitial << endl;
assert(numcols bmdK>0);
<< "COMPLETED_EXACT_AXIS_CONTROL" << endl;
exit 0;

-- Complete cyclic-source prerequisite for the six-root detector kernel.
-- General hypothesis tested: the retained polynomial source can supply a
-- complete formal sixfold kernel model with simple spectators, not just ranks.
-- N5 is the exact encoding control (first monic pair order17); N6 is the
-- smallest source with the new detector-kernel torsion. No dimension sweep.
-- Stages: shared universal columns; verify every connection recurrence;
-- split constant polynomial pivots; one homogeneous coefficient matrix;
-- FLINT exact rectangular solve; independent polynomial reconstruction.
-- No unrestricted Groebner basis and no claim of a minimal N6 endpoint.
-- Sizes: N5 pair10/pivots7/core3; N6 pair15/pivots9/core6.
-- N6 tests pair order36; modular inconsistency is not rational nonmembership.
-- Complete stdout is the certificate; retain with save-run-output.py.
load "research/tools/bmd_six_kernel_model_20261007.m2";
srcClock=cpuTime();
srcOut=getenv "BMD_SIX_KERNEL_SCRATCH";
assert(#srcOut>0);
for srcN in {5,6} do (
    srcCap:=if srcN==5 then 17 else 36;
    srcData:=bmdBuildKernelSource(srcN,srcCap);
    srcS:=srcData#"ring";srcCols:=srcData#"pairColumns";
    srcR:=#(srcData#"pairs");srcSplit:=srcData#"split";
    srcProj:=srcData#"projection";srcCW:=srcData#"weights";srcF:=srcData#"module";
    srcQ:=#srcCW;srcAll:=fold((a,b)->a|b,srcCols);
    srcPrefix:=map(srcF,srcS^(-toList(srcSplit+2..srcCap+1)),
        entries(srcProj*submatrix(srcAll,,toList(srcSplit..srcCap-1))));
    col:=map(srcF,srcS^{-srcCap-2},entries(srcProj*srcCols#srcCap));
    assert(isHomogeneous srcPrefix and isHomogeneous col);
    << "BEGIN N=" << srcN << " pairRows=" << srcR << " pivotRows=" << srcSplit
       << " coreRows=" << srcQ << " prefixColumns=" << numcols srcPrefix
       << " cap=" << srcCap << " recurrenceChecks=" << srcCap
       << " cpu=" << cpuTime()-srcClock << endl << flush;
    srcBasis:=basis(srcCap+2,source srcPrefix);
    srcTargetBasis:=basis(srcCap+2,srcF);
    srcProducts:=srcPrefix*srcBasis;
    srcCoeffs:=last coefficients(srcProducts,Monomials=>srcTargetBasis);
    srcRhs:=last coefficients(col,Monomials=>srcTargetBasis);
    assert(entries(srcTargetBasis*srcCoeffs)==entries srcProducts);
    assert(entries(srcTargetBasis*srcRhs)==entries col);
    srcAA:=sub(srcCoeffs,QQ);srcBB:=sub(srcRhs,QQ);
    assert(numrows srcAA==numcols srcTargetBasis and numcols srcAA==numcols srcBasis);
    assert(numrows srcBB==numrows srcAA and numcols srcBB==1);
    assert(numrows srcAA*numcols srcAA<=5000000);
    << "LINEAR_SIZE N=" << srcN << " rows=" << numrows srcAA
       << " cols=" << numcols srcAA << " cpu=" << cpuTime()-srcClock << endl << flush;
    srcInput:=srcOut|"/source-"|toString srcN|".input";
    srcOutput:=srcOut|"/source-"|toString srcN|".solution";
    srcFile:=openOut srcInput;
    srcFile << numrows srcAA << " " << numcols srcAA << " 1" << endl
        << toString entries srcAA << endl << toString entries srcBB << endl;
    close srcFile;
    srcCommand:="\""|srcOut|"/six-kernel-rational-solve\" \""|srcInput|"\" \""|srcOutput|"\"";
    srcStatus:=run srcCommand;
    assert(srcStatus==0);
    srcSolution:=matrix value get srcOutput;
    assert(numrows srcSolution==numcols srcAA and numcols srcSolution==1);
    assert(entries(srcAA*srcSolution)==entries srcBB);
    cert:=map(source srcPrefix,source col,entries(srcBasis*sub(srcSolution,srcS)));
    assert(entries(srcPrefix*cert)==entries col and isHomogeneous cert);
    srcStop:=srcCap;
    << "CLOSED N=" << srcN << " pairOrder=" << srcCap << " originalOrderBound=" << srcCap+2
       << " coreColumns=" << numcols srcPrefix << " cpu=" << cpuTime()-srcClock << endl;
    << "CORE_SOURCE_WEIGHTS=" << toString degrees source srcPrefix << endl;
    << "CORE_TARGET_WEIGHTS=" << toString degrees target srcPrefix << endl;
    << "PAIR_PROJECTION=" << toString entries srcProj << endl;
    << "CORE_PRESENTATION=" << toString entries srcPrefix << endl;
    << "NEXT_COLUMN=" << toString entries col << endl;
    << "DEPENDENCE_COEFFICIENTS=" << toString entries cert << endl << flush;
    if srcN==5 then assert(srcStop==17);
    -- Generic rank/support are proved dependencies, not closure tests.
    -- Avoid an unrelated kernel/resolution computation after certification.
    << "PASS N=" << srcN << " full cyclic source certified" << endl << flush;
);
<< "COMPLETED cpu=" << cpuTime()-srcClock << endl << flush;
exit 0;

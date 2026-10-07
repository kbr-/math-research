-- Full standard basis of the proved finite cyclic source, via Singular modStd.
-- This is not a search for cyclic closure. The source is already proved complete.
-- The installed modular algorithm runs in exactness1 mode with twelve workers.
-- Check the complete source round-trip, homogeneous output, and the entire
-- leading-module Hilbert numerator against the independent Smith/upper theorem.
amClock=cpuTime();
amOut=getenv "BMD_SIX_ACTION_SCRATCH";assert(#amOut>0);
load "research/tools/bmd_six_full_action_source_20261007.m2";
amScript=amOut|"/modular-source.sing";amOutput=amOut|"/modular-basis.m2";
amFile=openOut amScript;
(amFile << "LIB \"modstd.lib\";\nsetcores(12);\nshort=0;\nprintlevel=1;\n"
 << "ring R=0,(c_2,c_3,c_4,c_5,c_6),(wp(2,3,4,5,6),C);\n"
 << "matrix src[6][30]=" << concatenate between(",",apply(flatten entries abGamma,f->toString f)) << ";\n"
 << "module M=src;\nprint(\"MODULAR_BASIS_BEGIN\");\nmodule G=modStd(M,1);\n"
 << "if(size(reduce(M,G))!=0){ERROR(\"source remainder nonzero\");}\n"
 << "print(\"MODULAR_BASIS_END columns=\"+string(ncols(G)));\n"
 << "proc m2matrix(matrix A){string s=\"{\";int i,j;for(i=1;i<=nrows(A);i++){if(i>1){s=s+\",\";}s=s+\"{\";for(j=1;j<=ncols(A);j++){if(j>1){s=s+\",\";}s=s+string(A[i,j]);}s=s+\"}\";}return(s+\"}\");}\n"
 << "link out=\"ASCII:w " << amOutput << "\";\nopen(out);\n"
 << "write(out,\"amReturnedSource=\"+m2matrix(src)+\";\");\n"
 << "write(out,\"amReturnedBasis=\"+m2matrix(matrix(G))+\";\");\n"
 << "write(out,\"amReturnedLead=\"+m2matrix(matrix(lead(G)))+\";\");\n"
 << "close(out);\nprint(\"PASS Singular exact modular standard basis\");\nquit;\n");
close amFile;
<< "MODULAR_DRIVER_BEGIN cpu=" << cpuTime()-amClock << endl << flush;
amStatus=run("Singular -q \""|amScript|"\"");assert(amStatus==0);
value get amOutput;
assert(amReturnedSource==entries abGamma);
amRaw=matrix amReturnedBasis;amLeadRaw=matrix amReturnedLead;
assert(numrows amRaw==6 and numrows amLeadRaw==6 and numcols amRaw==numcols amLeadRaw);
amWeights=apply(toList(0..numcols amRaw-1),j->(
    ws:=select(apply(toList(0..5),i->if amRaw_(i,j)==0 then null
        else (abData#"weights")#i+first degree amRaw_(i,j)),w->w=!=null);
    assert(#ws>0 and min ws==max ws);first ws
));
amG=map(abF,abS^(-amWeights),entries amRaw);
amLead=map(abF,abS^(-amWeights),entries amLeadRaw);
assert(isHomogeneous amG and isHomogeneous amLead);
assert(poincare(coker amLead)==abHint);
<< "MODULAR_GENERATOR_WEIGHTS=" << toString amWeights << endl;
<< "MODULAR_BASIS=" << toString entries amG << endl;
<< "MODULAR_LEAD=" << toString entries amLead << endl;
<< "CYCLIC_COLUMNS=" << toString entries abGamma << endl;
<< "PASS exact source round-trip, homogeneous modular basis and complete Hilbert numerator; cpu="
   << cpuTime()-amClock << endl << flush;
exit 0;

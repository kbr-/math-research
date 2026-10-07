-- Unsuccessful bounded polynomial-basis alternative; not used by the accepted frame method.
-- BMD_GB_LINEAR=1 reproduces the unsupported QQ experimental-kernel attempt.
load "research/tools/bmd_six_full_action_source_20261007.m2";
<< "BOUNDED_GB_BEGIN rows=6 columns=30 degree=40 cpu=" << cpuTime()-abClock << endl << flush;
gbTrace=1;
abGB=gb(abGamma,DegreeLimit=>{40},Hilbert=>abHint,ChangeMatrix=>true,Algorithm=>(if getenv "BMD_GB_LINEAR"=="1" then LinearAlgebra else Homogeneous));
gbTrace=0;
<< "BOUNDED_GB_END status=" << status abGB << " cpu=" << cpuTime()-abClock << endl << flush;
abG=gens abGB;abChange=getChangeMatrix abGB;
assert(entries(abGamma*abChange)==entries abG);
assert(abGamma%abGB==0 and isHomogeneous abG);
abLead=leadTerm abG;
abCM=coker abLead;
abUpper=d->(
    if d<0 then 0 else (
        m:=(d-4)//2;max(d-8,0)+(if d>=4 then (m+1)*(m+2)//2 else 0)
    )
);
abImage=d->(#select({12,13,13,14,14,15},w->d>=w and (d-w)%2==0)
    +(if d==14 then 1 else 0));
abKernel=d->(
    sum(abFree,b->if d>=b#0 and (d-b#0)%2==0 then b#1 else 0)+
    sum(abTor,row->sum(row#1,b->if d>=b#0 and (d-b#0)%2==0 and d-b#0<2*row#0 then b#1 else 0))
);
for d from 0 to 40 do (
    got:=numcols basis(d,abCM);expected:=abUpper(d)+abImage(d)+abKernel(d);
    assert(got==expected);
    << "LEADING_HILBERT degree=" << d << " dimension=" << got << endl;
);
<< "REDUCTION_GENERATOR_WEIGHTS=" << toString flatten degrees source abG << endl;
<< "REDUCTION_BASIS=" << toString entries abG << endl;
<< "REDUCTION_CHANGE=" << toString entries abChange << endl;
<< "CYCLIC_COLUMNS=" << toString entries abGamma << endl;
<< "PASS degree40 exact polynomial reductions, source change and all Hilbert dimensions; cpu="
   << cpuTime()-abClock << endl << flush;
exit 0;

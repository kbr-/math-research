-- Shared exact source and proved Hilbert numerator for the full-action construction.
-- Universal columns, centered recurrence and pivot feedback are checked by the model.
abClock=cpuTime();
load "research/tools/bmd_six_kernel_model_20261007.m2";
abData=bmdBuildKernelSource(6,38);abS=abData#"ring";abF=abData#"module";
abColumns=fold((a,b)->a|b,drop(abData#"columns",9));
abGamma=map(abF,abS^(-toList(11..40)),entries abColumns);
assert(isHomogeneous abGamma);
abD=degreesRing abS;abZ=abD_0;
abFree={{15,3},{16,7},{17,6},{18,8},{19,9},{20,10},{21,4},{22,1}};
abTor={{1,{{32,1},{33,1}}},{2,{{31,8},{32,4}}},{3,{{30,9}}},
 {4,{{29,11},{30,2}}},{5,{{27,10},{28,14}}},{6,{{26,13},{27,3}}},
 {7,{{25,14},{26,1}}},{8,{{23,12},{24,14}}},{9,{{21,7},{22,12}}}};
abANum=sum(abFree,b->b#1*abZ^(b#0))+
    sum(abTor,row->sum(row#1,b->b#1*(abZ^(b#0)-abZ^(b#0+2*row#0))));
abINum=abZ^12+2*abZ^13+2*abZ^14+abZ^15+abZ^14*(1-abZ^2);
abRest=product(toList(3..6),j->1-abZ^j);
abENum=(abZ^9*(1+abZ)*(1+abZ+abZ^2)*product(toList(4..6),j->1-abZ^j)
    +abZ^4*(1+abZ^2)*(1+abZ+abZ^2)*(1-abZ^5)*(1-abZ^6));
abHint=abRest*(abANum+abINum)+abENum;
assert(canUseHilbertHint abGamma);

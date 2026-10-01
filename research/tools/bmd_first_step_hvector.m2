-- Hilbert series numerators of B/T_2 and B/T_2' (T_2' the link by A = (F, deltaF)) for the d = 2 dimension-four first-step
-- ideal (5 October 2026; cycle bmd-20261005-w).  Numerical self-linkage means equal Hilbert series; the canonical module of
-- B/T_2 is T_2'/A up to shift, so this compares B/T_2 with the dual numerics of its canonical module.
B=QQ[e_1,e_2,e_3,e_4,Degrees=>{1,2,3,4}];
readKey=(file,key)->(L:=separate("\n",get file); H:=select(L,l->substring(0,#key,l)==key); value substring(#key,last H));
Tgens=apply(flatten readKey("research/results/cube-weighted-first-step-resolution-20260926/resolution-qq.txt","TOP_GENERATORS="),f->sub(f,B));
Lgens=apply(flatten readKey("research/results/cube-hull-uniform-degree-review-20260927/low-polar-colon.txt","LINKED_GENERATORS="),f->sub(f,B));
T=ideal Tgens; Tp=ideal Lgens;
hT=numerator reduceHilbert hilbertSeries(B/T);
hTp=numerator reduceHilbert hilbertSeries(B/Tp);
<< "numerator for B/T:  " << toString hT << endl;
<< "numerator for B/T': " << toString hTp << endl;
<< "equal Hilbert series: " << (hT==hTp) << endl;
exit 0;

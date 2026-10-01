-- Hilbert-Burch relation matrix of the d = 2 dimension-four first-step ideal T_2 (5 October 2026; cycle bmd-20261005-u).
-- Question (consolidation review): are the relation entries built from the boundary coordinates G_j and the connection
-- delta?  Output: the minimal relation matrix, its entry degrees, and whether each entry lies in the subalgebra-module
-- spanned by G_(r-1), G_(r-2), ..., delta-images (tested by membership of entries in the ideal of boundary coordinates).
B=QQ[e_1,e_2,e_3,e_4,Degrees=>{1,2,3,4}];
readKey=(file,key)->(L:=separate("\n",get file); H:=select(L,l->substring(0,#key,l)==key); value substring(#key,last H));
Tgens=apply(flatten readKey("research/results/cube-weighted-first-step-resolution-20260926/resolution-qq.txt","TOP_GENERATORS="),f->sub(f,B));
G=apply(flatten readKey("research/results/cube-four-reflexive-hull-test-20260927/boundary-perfection.txt","BOUNDARY_VECTOR="),f->sub(f,B));
<< "boundary vector length " << #G << ", degrees " << apply(G,g->if g==0 then -1 else first degree g) << endl;
T=ideal Tgens;
C=res T;
<< "BETTI " << betti C << endl;
M=C.dd_2;
<< "RELATION_SOURCE_DEGREES=" << degrees source M << endl;
<< "RELATION_TARGET_DEGREES=" << degrees target M << endl;
<< "RELATION_MATRIX=" << toString entries M << endl;
Gideal=ideal select(G,g->g!=0);
<< "entries in ideal of boundary coordinates: " << apply(flatten entries M,f->f % Gideal==0) << endl;
<< "entry term counts: " << apply(flatten entries M,f->#terms f) << endl;
exit 0;

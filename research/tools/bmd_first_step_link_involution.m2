-- Is the d = 2 first-step ideal T exchanged with its link T' = (F, deltaF):T by the reflection a -> -a,
-- i.e. e_i -> (-1)^i e_i?  (5 October 2026; cycle bmd-20261005-t.)  Data: the recorded generators of T
-- (TOP_GENERATORS) and of the link (LINKED_GENERATORS).
B=QQ[e_1,e_2,e_3,e_4,Degrees=>{1,2,3,4}];
readKey=(file,key)->(L:=separate("\n",get file); H:=select(L,l->substring(0,#key,l)==key); value substring(#key,last H));
Tgens=apply(flatten readKey("research/results/cube-weighted-first-step-resolution-20260926/resolution-qq.txt","TOP_GENERATORS="),f->sub(f,B));
Lgens=apply(flatten readKey("research/results/cube-hull-uniform-degree-review-20260927/low-polar-colon.txt","LINKED_GENERATORS="),f->sub(f,B));
T=ideal Tgens; Tp=ideal Lgens;
sigma=map(B,B,{-e_1,e_2,-e_3,e_4});
<< "T degrees " << degrees source gens T << "; link degrees " << degrees source gens Tp << endl;
<< "T == link: " << (T==Tp) << endl;
<< "sigma(T) == T: " << (sigma(T)==T) << endl;
<< "sigma(T) == link: " << (sigma(T)==Tp) << endl;
exit 0;

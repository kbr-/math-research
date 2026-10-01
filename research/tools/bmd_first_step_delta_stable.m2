-- Is the d = 2 first-step ideal T_2 stable under the connection delta (degree +1)?  If delta(T) is contained in T,
-- delta shifts generators and relations (a Toeplitz mechanism); otherwise report the degrees of generators whose delta
-- leaves T.  delta = sum_j D_j d/de_j with D = (2e_2-e_1^2, 3e_3-e_1e_2, 4e_4-e_1e_3, -e_1e_4) as in
-- research/tools/bmd_cube_low_polar_colon.m2.  Also test the link T' and A = (F, deltaF).  (5 October 2026; cycle u.)
B=QQ[e_1,e_2,e_3,e_4,Degrees=>{1,2,3,4}];
readKey=(file,key)->(L:=separate("\n",get file); H:=select(L,l->substring(0,#key,l)==key); value substring(#key,last H));
Tgens=apply(flatten readKey("research/results/cube-weighted-first-step-resolution-20260926/resolution-qq.txt","TOP_GENERATORS="),f->sub(f,B));
Lgens=apply(flatten readKey("research/results/cube-hull-uniform-degree-review-20260927/low-polar-colon.txt","LINKED_GENERATORS="),f->sub(f,B));
Dv={2*e_2-e_1^2,3*e_3-e_1*e_2,4*e_4-e_1*e_3,-e_1*e_4};
delta=f->sum(toList(0..3),j->diff(B_j,f)*Dv#j);
T=ideal Tgens; Tp=ideal Lgens;
<< "delta(T gens) in T: " << apply(Tgens,f->(delta f) % T==0) << endl;
<< "delta(link gens) in link: " << apply(Lgens,f->(delta f) % Tp==0) << endl;
<< "delta(T gens) in link: " << apply(Tgens,f->(delta f) % Tp==0) << endl;
<< "delta(link gens) in T: " << apply(Lgens,f->(delta f) % T==0) << endl;
exit 0;

-- Does the inversion a -> 1/a (e_k -> e_(4-k)/e_4) exchange the d = 2 first-step ideal T_2 with its link T_2' ?
-- (5 October 2026; cycle bmd-20261005-v.)  Each generator f is mapped to e_4^k f(e_3/e_4, e_2/e_4, e_1/e_4, 1/e_4) with
-- the least k clearing denominators; the image ideal is saturated by e_4 and compared with T_2, T_2' (both saturated by e_4).
B=QQ[e_1,e_2,e_3,e_4,Degrees=>{1,2,3,4}];
x4=B_3;
F=frac B;
y=apply(4,i->promote(B_i,F));
readKey=(file,key)->(L:=separate("\n",get file); H:=select(L,l->substring(0,#key,l)==key); value substring(#key,last H));
Tgens=apply(flatten readKey("research/results/cube-weighted-first-step-resolution-20260926/resolution-qq.txt","TOP_GENERATORS="),f->sub(f,B));
Lgens=apply(flatten readKey("research/results/cube-hull-uniform-degree-review-20260927/low-polar-colon.txt","LINKED_GENERATORS="),f->sub(f,B));
inv=map(F,B,{y#2/y#3,y#1/y#3,y#0/y#3,1/y#3});
clear=f->(g:=inv f; k:=0; while denominator((y#3)^k*g)!=1 do k=k+1; numerator((y#3)^k*g));
T=ideal Tgens; Tp=ideal Lgens;
Ts=saturate(T,x4); Tps=saturate(Tp,x4);
I=saturate(ideal apply(Tgens,clear),x4);
<< "image generator degrees " << degrees source mingens I << endl;
<< "inv(T) == T (saturated): " << (I==Ts) << endl;
<< "inv(T) == link (saturated): " << (I==Tps) << endl;
exit 0;

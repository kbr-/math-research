default(parisizemax,2000000000);
default(nbthreads,1);
setrand(20261007);
read("research/tools/bmd_branch_state_core_20261007.gp");

{
my(cases=[[3,3,2,18],[3,5,2,18],[4,3,4,10]]);
for(cas=1,#cases,
 NN=cases[cas][1];PP=cases[cas][2];my(ext=cases[cas][3],last=cases[cas][4],modulus=ffinit(PP,ext,'a),a=ffgen(modulus,'a));OO=a^0;BB=2^(NN-1);CC=NN*BB;HH=(PP-1)/2;
 AA=vector(NN,i,random(a));while(#Set(AA)!=NN||prod(i=1,NN,AA[i])==0,AA=vector(NN,i,random(a)));
 my(coords=List());for(S=0,2^NN-1,for(i=1,NN,if(!bittest(S,i-1),listput(coords,[S,i]))));COORD=Vec(coords);assert(#COORD==CC,"coordinate count");
 ZZ=vector(CC,c,-OO/AA[COORD[c][2]]);
 RR=vector(CC,c,my(S=COORD[c][1],i=COORD[c][2]);AA[i]*prod(h=1,NN,if(h==i||bittest(S,h-1),OO,OO+AA[h]*ZZ[c])));
 my(prec=BB*last+1,ell=vector(NN,i,OO+AA[i]*T+O(T^prec)),roots=apply(sqrt,ell));for(i=1,NN,assert(valuation(roots[i]^2-ell[i],T)>=prec,"root equations"));
 CH=vector(2^NN,S,prod(i=1,NN,if(bittest(S-1,i-1),roots[i],OO)));
 CACHE=Map();CALLS=0;MAXCOLS=0;MAXDEG=0;
 assert(matrank(source_eval(NN))==#inds(NN)-1,"full-source branch map must lose W; faithfulness needs the marked bound");
 print("FULL_SOURCE_CONTROL: kernel of branch evaluation on V_n is the one-dimensional W line");
 print("CASE n=",NN," p=",PP," modulus=",modulus," slopes=",AA," branch_dimension=",CC);
 for(d=max(2,NN-2),last,
  my(N=BB*d-(NN-3)*BB/2,U=branch_state(d,N),K=matker(source_jet(d,N)),V=source_eval(d)*K,rankU=matrank(U));
  assert(rankU==matsize(K)[2] && matrank(matconcat([U,V]))==rankU,"recursive/direct branch spaces differ");
  print("DIRECT_MATCH d=",d," jets=",N," kernel_dimension=",rankU)
 );
 print("BOUNDED_CONTROL calls=",CALLS," max_columns=",MAXCOLS);
 CACHE=Map();CALLS=0;MAXCOLS=0;
 my(big=[10^3+7,10^6+11,10^12+13]);
 for(i=1,#big,my(d=big[i],N=BB*d-(NN-3)*BB/2,prior=CALLS,U=branch_state(d,N));print("LARGE_MARKED_QUERY d=",d," kernel_dimension=",matsize(U)[2]," new_states=",CALLS-prior," max_columns=",MAXCOLS));
 assert(MAXCOLS<=PP*CC,"fixed matrix width bound");
);
print("BRANCH_STATE_RECURSION_COMPLETED: specialized marked kernels only; no generic exception set claimed.")
}
quit;

\\ Controls for the low-degree compatibility rank defect in odd dimensions.
\\ No scan of generic failure degrees: tests the exact dimension identities and low-source map.
default(parisizemax,1000000000);
default(nbthreads,1);
read("research/tools/bmd_branch_state_core_20261007.gp");
countV(n,d)={if(d<0,return(0));sum(s=0,min(n,d),binomial(n,s)*(floor((d-s)/2)+1))};
{
my(count=0,childchecks=0);
forstep(n=3,25,2,forprime(p=3,97,
 my(c=(n-3)/2,B=2^(n-1),C=n*B,b=(p-1)/2,ar=vector(p,r,floor((c+(p-1)*n-2*(r-1))/p)),er=vector(p,r,countV(n,2*c-ar[r])),t=countV(n,c)-vecsum(er));
 assert(B*vecsum(ar)-p*c*B==b*C,"square minimal compatibility dimensions");
 for(r=0,p-1,assert(2*c-ar[r+1]==floor((c-2*(p-1-r))/p),"dual child index");assert(countV(n,ar[r+1])==B*(ar[r+1]-c)+er[r+1],"Riemann Roch child dimensions");if(n>=5,assert(ar[r+1]>c && ar[r+1]<n,"positive faithful child range"));childchecks++);
 assert(if(n==3,t==0,t>0),"proper power subspace defect");if(n==9&&p==3,print("GOAL_PARAMETERS n=9 p=3 child_degrees=",ar," child_excesses=",er," parent_dimension=",countV(n,c)," forced_defect=",t));count++
));
print("ARITHMETIC_CONTROLS parameter_pairs=",count," child_indices=",childchecks);
my(cases=[[3,3],[5,3],[5,5]]);for(t=1,#cases,
 NN=cases[t][1];PP=cases[t][2];BB=2^(NN-1);CC=NN*BB;HH=(PP-1)/2;my(c=(NN-3)/2,gen=ffgen(ffinit(PP,2),'a));OO=gen^0;T='x;AA=vector(NN,i,OO*(i%PP)+gen*(i\PP));assert(#Set(AA)==NN,"distinct labels");
 my(coords=List());for(S=0,2^NN-1,for(i=1,NN,if(!bittest(S,i-1),listput(coords,[S,i]))));COORD=Vec(coords);ZZ=vector(CC,c,-OO/AA[COORD[c][2]]);
 my(ar=vector(PP,r,floor((c+(PP-1)*NN-2*(r-1))/PP)),pool=vector(PP,r,source_eval(ar[r])),sizes=apply(U->matsize(U)[2],pool),total=vecsum(sizes),C=matrix(HH*CC,total,i,j,0*OO),off=0);
 for(r=0,PP-1,for(j=0,HH-1,for(i=1,CC,for(k=1,sizes[r+1],C[j*CC+i,off+k]=binomial(r,j)*ZZ[i]^(r-j)*pool[r+1][i,k]^PP)));off+=sizes[r+1]);
 my(rank=matrank(C),pred=total-countV(NN,c),defect=HH*CC-rank);assert(rank==pred,"low compatibility rank");
 print("EXACT_LOW_MAP n=",NN," p=",PP," size=",matsize(C)," rank=",rank," forced_defect=",defect)
);
print("SMOOTH_PRECISION_OBSTRUCTION_CONTROLS_COMPLETED")
}
quit;

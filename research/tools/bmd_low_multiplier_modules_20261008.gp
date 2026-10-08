\\ Complete H0(kappa+NQ), exact moving-divisor restriction, and Smith flags through z^9.
\\ Four positive families (negative signs follow by Serre duality), N=18,36,54,108.
\\ All field kernels/inverses use PARI; series Schur steps retain every coefficient needed.
default(parisize,256000000);
default(parisizemax,1500000000);
default(nbthreads,1);
T='T;
read("research/tools/bmd_root_jets.gp");
read("research/tools/bmd_low_multiplier_core_20261008.gp");

{
my(start=getwalltime(),P=if(getenv("BMD_LM_PRECISION"),eval(getenv("BMD_LM_PRECISION")),10),only34=(getenv("BMD_LM_ONLY")!=0),L=27*(4+P-1),a=ffgen(Mod(1,3)*(a^3+2*a+2),'a),one=a^0,labels=vector(9,i,a^(i-1)),I=rootbasis(9,3),roots=vector(9,i,sqrt(one+labels[i]*T+O(T^L))),products=vector(512),inverse=vector(512));
products[1]=one+O(T^L);inverse[1]=products[1];
for(S=1,511,my(bit=valuation(S,2));products[S+1]=products[S-2^bit+1]*roots[bit+1];inverse[S+1]=1/products[S+1]);
my(F=vector(140,i,T^I[i][2]*products[I[i][1]+1]),G=apply(f->f*inverse[512],F),FC=matrix(L,140,i,j,polcoef(F[j],i-1,T)),GC=matrix(108,140,i,j,polcoef(G[j],i-1,T)),field=vector(27,i,one*((i-1)%3)+a*(((i-1)\3)%3)+a^2*((i-1)\9)),codes=Map(),out=if(getenv("BMD_LM_OUT"),getenv("BMD_LM_OUT"),"research/results/bmd-exception-low-multipliers-20261008/modules.g"));
lm_assert(P>=10&&P<=27,"bounded declared precision");
if(only34,lm_assert(getenv("BMD_LM_ONLY")=="34","only requested residual family"));
for(i=1,27,mapput(codes,Str(field[i]),i-1));
write(out,"LOW_MULTIPLIER_PRECISION := ",P,";");write(out,"LOW_MULTIPLIER_MODULES := [");
for(b=2,3,for(ai=1,2,
 if(only34&&(b!=3||ai!=2),next());
 my(mult=2*ai,q=3^b,N=mult*q,J=lm_sub(FC,[1..N],[1..140]),Residue=matrix(140,N,i,j,GC[N+1-j,i]),PP=matker(Residue),extras=matsize(PP)[2],Kminus=matker(J),hminus=matsize(Kminus)[2],H=140+extras,nums=matrix(L,H),checks=0);
 lm_assert(extras==N-matrank(J)&&H==N+hminus,"complete principal-part and RR dimensions");
 for(i=N+1,L,for(j=1,140,nums[i,j]=FC[i-N,j]));
 for(j=1,extras,
  my(R=sum(i=0,N-1,PP[i+1,j]*T^i),total=0*one+O(T^L));
  for(S=0,511,
   my(pol=truncate(R*inverse[S+1]+O(T^N)),bound=N+floor((3-hammingweight(S))/2),term=pol*products[S+1]);
   lm_assert(poldegree(pol)<=bound&&valuation(term-R,T)>=N,"complete character lift");total+=term;checks++;
  );
  total/=512*one;
  for(i=1,L,nums[i,140+j]=polcoef(total,i-1,T));
  lm_assert(vector(N,i,nums[i,140+j])==vector(N,i,PP[i,j]),"exact principal part");
 );
 my(series=vector(P,k,matrix(N,H,i,j,
  my(res=(i-1)%q,jet=(i-1)\q,index=q*(k-1+jet)+res);
  binomial(k-1+jet,jet)*nums[index+1,j]
 )),result);
 lm_assert(matrank(series[1])==extras,"central unit contraction");
 print("LOW_MULTIPLIER_INPUT base=",b," multiplier=",mult," poles=",N," source=",H," jet_rank=",matrank(J)," fixed_kernel=",hminus," extras=",extras," lift_checks=",checks);
 result=lm_smith(series);
 my(complete=result[1],E0=result[3],E1=result[4],W=lm_sub(E0,[1..140],[1..matsize(E0)[2]]));
 if(complete,
  lm_assert(matsize(E0)[2]==hminus,"full generic row rank and primitive rank");
  if(extras,lm_assert(lm_sub(E0,[141..H],[1..hminus])==matrix(extras,hminus),"primitive central sections are holomorphic"));
  lm_assert(matrank(W)==hminus,"primitive specialization injective");
 );
 print("LOW_MULTIPLIER_RESULT base=",b," multiplier=",mult," complete=",complete," elementary_divisors=",result[2]," primitive_rank=",matsize(W)[2]," same_fixed_space=",if(complete,matrank(concat(Kminus,W))==hminus,-1)," first_derivative=",result[5]);
 write(out,"[",b,",",mult,",",N,",",extras,",",complete,",",result[2],",",lm_encode(Kminus,codes),",",lm_encode(E0,codes),",",lm_encode(E1,codes),",",vector(P,k,lm_encode(series[k],codes)),",",lm_encode(PP,codes),"]",if(b==3&&ai==2,"",","));
));
write(out,"];");print("LOW_MULTIPLIER_MODULES_COMPLETED precision=",P," max_pole108=true wall_ms=",getwalltime()-start);
}
quit;

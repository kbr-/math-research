\\ Complete references c=5,13 at baseline three for the unresolved central return classes.
\\ The coefficient-five run sizes the coefficient-thirteen run; retain complete sources and jets.
\\ All field kernels/inverses use PARI; series Schur steps retain every coefficient needed.
default(parisize,256000000);
default(parisizemax,4000000000);
default(nbthreads,1);
T='T;
read("research/tools/bmd_root_jets.gp");
read("research/tools/bmd_low_multiplier_core_20261008.gp");

{
my(start=getwalltime(),P=28,mult=eval(getenv("BMD_RESIDUAL_MULTIPLIER")),N=27*mult,L=27*(mult+P-1),a=ffgen(Mod(1,3)*(a^3+2*a+2),'a),one=a^0,labels=vector(9,i,a^(i-1)),I=rootbasis(9,3),roots=vector(9,i,sqrt(one+labels[i]*T+O(T^L))),products=vector(512),inverse=vector(512));
products[1]=one+O(T^L);inverse[1]=products[1];
for(S=1,511,my(bit=valuation(S,2));products[S+1]=products[S-2^bit+1]*roots[bit+1];inverse[S+1]=1/products[S+1]);
my(F=vector(140,i,T^I[i][2]*products[I[i][1]+1]),G=apply(f->f*inverse[512],F),FC=matrix(L,140,i,j,polcoef(F[j],i-1,T)),GC=matrix(N,140,i,j,polcoef(G[j],i-1,T)),field=vector(27,i,one*((i-1)%3)+a*(((i-1)\3)%3)+a^2*((i-1)\9)),codes=Map(),out=getenv("BMD_RESIDUAL_OUT"));
lm_assert((mult==5||mult==13)&&out!=0,"only the two necessary residual modules");
for(i=1,27,mapput(codes,Str(field[i]),i-1));
write(out,"LOW_MULTIPLIER_PRECISION := ",P,";");write(out,"LOW_MULTIPLIER_MODULES := [");
my(b=3,q=27,J=lm_sub(FC,[1..N],[1..140]),Residue=matrix(140,N,i,j,GC[N+1-j,i]),PP=matker(Residue),extras=matsize(PP)[2],Kminus=matker(J),hminus=matsize(Kminus)[2],H=140+extras,nums=matrix(L,H),checks=0);
 lm_assert(extras==N-matrank(J)&&H==N+hminus,"complete principal-part and RR dimensions");
 for(i=N+1,L,for(j=1,140,nums[i,j]=FC[i-N,j]));
 print("RESIDUAL_SIZE multiplier=",mult," poles=",N," source=",H," jet_rank=",matrank(J)," extra_lifts=",extras," series_coefficients=",P);
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
 write(out,"[",b,",",mult,",",N,",",extras,",",complete,",",result[2],",",lm_encode(Kminus,codes),",",lm_encode(E0,codes),",",lm_encode(E1,codes),",",vector(P,k,lm_encode(series[k],codes)),",",lm_encode(PP,codes),"]","");
write(out,"];");print("RESIDUAL_MODULE_COMPLETED multiplier=",mult," precision=",P," wall_ms=",getwalltime()-start);
}
quit;

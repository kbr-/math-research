\\ Actual primitive pairings, retaining equal-order baseline torsion instead of discarding it.
default(parisize,256000000);
default(parisizemax,1500000000);
default(nbthreads,1);
T='T;
read("research/tools/bmd_root_jets.gp");
read("research/tools/bmd_low_multiplier_core_20261008.gp");
read("research/results/bmd-exception-low-multipliers-20261008/comparison-input.gp");

{
my(start=getwalltime(),a=ffgen(Mod(1,3)*(a^3+2*a+2),'a),one=a^0,field=vector(27,i,one*((i-1)%3)+a*(((i-1)\3)%3)+a^2*((i-1)\9)),codes=Map(),I=rootbasis(9,3),polys=vector(512),off=vector(512),rows=vector(6,s,vector(769)),total=0,products=vector(512),roots=vector(9,i,sqrt(one+a^(i-1)*T+O(T^108))));
for(i=1,27,mapput(codes,Str(field[i]),i-1));
polys[1]=one;products[1]=one+O(T^108);
for(S=1,511,my(bit=valuation(S,2));polys[S+1]=polys[S-2^bit+1]*(one+a^bit*T);products[S+1]=products[S-2^bit+1]*roots[bit+1]);
for(S=0,511,
 my(g=max(0,(hammingweight(S)-1)\2));off[S+1]=total;if(!g,next());
 my(B=matrix(g,g,i,j,if(3*i-j>=0,polcoef(polys[S+1],3*i-j,T),0)*one),v=matrix(1,g,i,j,(j==1)*one));
 for(s=1,6,v=lm_frob(v,3)*B;for(j=1,g,rows[s][total+j]=v[1,j]));total+=g;
);
my(cups=vector(6,s,lm_cup(rows[s],polys,off,I)),G=vector(140,i,T^I[i][2]*products[I[i][1]+1]/products[512]),GC=matrix(108,140,i,j,polcoef(G[j],i-1,T)),out="research/results/bmd-exception-low-multipliers-20261008/comparisons.g",entries=List(),failures=0);
for(ci=1,4,
 my(case=LM_MODULES[ci],b=case[1],mult=case[2],N=case[3],extras=case[4],H=140+extras,P=LM_PRECISION,Kminus=lm_decode(case[7],field),E0=lm_decode(case[8],field),h=matsize(Kminus)[2],W=lm_sub(E0,[1..140],[1..h]),amax=vecmax(apply(v->v[1],case[6])),A=vector(P,i,lm_decode(case[10][i],field)),M=vector(P,k,matrix(H,H,i,j,if(i<=N,A[k][i,j],0*one))),RL=0,IR=matrix(H,140,i,j,(i==j)*one));
 lm_assert(case[5]==1&&matrank(concat(Kminus,W))==h,"actual primitive modules");
 if(amax==9,
  my(R=matrix(140,N,i,j,GC[N+1-j,i]),kp=matindexrank(Kminus)[1],B=lm_sub(Kminus,kp,[1..h])^-1*matrix(h,140,i,j,(kp[i]==j)*one),S=matrix(H,140,i,j,if(i<=N,R[j,i],B[i-N,j])),sp=matindexrank(S)[1]);
  RL=lm_sub(S,sp,[1..140])^-1*matrix(140,H,i,j,(sp[i]==j)*one);
  lm_assert(RL*S==matid(140)&&mattranspose(S)*M[1]==matrix(140,H),"exact central cohomology frame");
  lm_assert(mattranspose(S)*M[2]*IR==mult*cups[b],"actual first-cup sign and scale control");
 );
 my(jobs=List());
 for(vi=1,#LM_VECTORS,if(LM_VECTORS[vi][1]==b,
  my(v=LM_VECTORS[vi],degree=v[3],d=valuation(degree,3),mu=lm_cup(apply(x->field[x+1],v[4]),polys,off,I));
  for(u=-1,1,listput(jobs,[v[2],degree,u,mult*mu+u*cups[b+d]]));
 ));
 if(b==3,for(u=-1,1,if(u,listput(jobs,[0,9,u,u*cups[5]]))));
 for(ji=1,#jobs,
  my(job=jobs[ji],k=job[1],degree=job[2],u=job[3],C=job[4],rank,needed,kind,retained);
  if(degree>amax,
   retained=mattranspose(Kminus)*C*W;rank=matrank(retained);needed=h;kind=0;
   print("LOW_COMPARISON base=",b," multiplier=",mult," k=",k," order=",degree," tail=",u," mode=strict rank=",rank," needed=",needed);
  ,
   lm_assert(degree==9&&amax==9,"only justified equal-order test");
   my(D=mattranspose(RL)*C*mattranspose(IR),test=vector(P,k,M[k]+if(k==degree+1,D,0)),res=lm_smith(test),pivots=res[2],before=sum(i=1,#pivots,if(pivots[i][1]<degree,pivots[i][2],0)));
   needed=H-before;rank=if(pivots[#pivots][1]==degree,pivots[#pivots][2],0);kind=1;retained=D;
   print("LOW_COMPARISON base=",b," multiplier=",mult," k=",k," order=",degree," tail=",u," mode=equal rank=",rank," needed=",needed," complete=",res[1]);
  );
  if(rank<needed,failures++);
  listput(entries,[b,mult,k,degree,u,kind,needed,rank,lm_encode(retained,codes)]);
 );
);
write(out,"LOW_COMPARISONS := ",Vec(entries),";");
print("LOW_COMPARISON_COMPLETED cases=",#entries," residuals=",failures," wall_ms=",getwalltime()-start);
}
quit;

\\ Complete tangent maps, not rank-only comparison, at period4680.
default(parisizemax,1000000000);
default(nbthreads,1);
T='T;
read("research/tools/bmd_root_jets.gp");
st_assert(c,s)={if(!c,error(s));};
st_frob(A,e)={matrix(matsize(A)[1],matsize(A)[2],i,j,A[i,j]^e);};
{
my(start=getwalltime(),a=ffgen(Mod(1,3)*(a^3+2*a+2),'a),one=a^0,labels=vector(9,i,a^(i-1)),poly=vector(512),fail=vector(4,j,List()),ranks=vector(4),count=0);
poly[1]=one;
for(S=1,511,my(b=valuation(S,2));poly[S+1]=poly[S-2^b+1]*(one+a^b*T));
for(S=0,511,
 my(g=max(0,(hammingweight(S)-1)\2));if(g==0,next());count++;
 my(B=matrix(g,g,i,j,if(3*i-j>=0,polcoef(poly[S+1],3*i-j,T),0)*one),D=st_frob(B,9)*st_frob(B,3)*B,P=D^1560,A=matid(g)*one);
 for(j=1,4,A=st_frob(A,3)*B;ranks[j]+=matrank(A);if(A*P!=A,listput(fail[j],S)));
);
st_assert(count==466,"complete character maps");
for(j=1,4,print("SHORT_TANGENT base=",j," operator_rank=",ranks[j]," failed_blocks=",Vec(fail[j])));
my(I=rootbasis(9,3),FC=rootjets(labels,0,vector(9,i,one),I,81),nu=1/sqrt(poly[512]+O(T^81)),Toep=matrix(81,81,i,j,if(i>=j,polcoef(nu,i-j,T),0)*one),GC=Toep*FC,field=vector(27,i,one*((i-1)%3)+a*(((i-1)\3)%3)+a^2*((i-1)\9)),codes=Map(),out="research/results/bmd-exception-short-returns-20261008/low-kernels.g");
for(i=1,27,mapput(codes,Str(field[i]),i-1));
write(out,"LOW_DATA := [");
for(j=1,4,
 my(q=3^j,J=matrix(q,140,u,v,FC[u,v]),G=matrix(140,q,u,v,GC[q+1-v,u]),C=G*J,K=matker(C),rank=matrank(C));
 st_assert(C==mattranspose(C),"symmetric low cup");
 st_assert(matrank(J)==rank&&J*K==matrix(q,140-rank),"complete jet/cup kernel identity");
 print("LOW_SIGNED_KERNEL base=",j," q=",q," cup_rank=",rank," jet_rank=",matrank(J)," kernel=",140-rank," identity=true");
 write(out,"[",j,",",q,",",vector(q,u,vector(140,v,mapget(codes,Str(J[u,v])))),",",vector(140,u,vector(140,v,mapget(codes,Str(C[u,v])))),",",vector(140,u,vector(140-rank,v,mapget(codes,Str(K[u,v])))),"]",if(j<4,",",""));
);
write(out,"];");
print("SHORT_TANGENT_COMPLETED characters=466 wall_ms=",getwalltime()-start);
}
quit;

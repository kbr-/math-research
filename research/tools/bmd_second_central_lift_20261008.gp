\\ Exact second lifting map for the F27 central theta bundle at q=81.
\\ First cup has rank79 on V3 dimension140. Keep its full61-dimensional kernel and cokernel.
\\ Complete all liftable principal parts by character orthogonality once, then reuse them.
\\ Prediction/control: unit exponents agree modw^3 with a +/-1 family, so at least h0(kappa-qQ) survive.
\\ Largest ranks140-square; at most2 independent principal-part directions need512 completions.
read("research/tools/bmd_root_jets.gp");
default(parisizemax,1500000000);
default(nbthreads,1);
assert(c,s)={if(!c,error(s));};
submat(M,rr,cc)=matrix(#rr,#cc,i,j,M[rr[i],cc[j]]);
{
my(start=getwalltime(),Q=81,N=2*Q,modulus=Mod(1,3)*(a^3+2*a+2),a=ffgen(modulus,'a),one=a^0,labels=vector(9,i,a^(i-1)),I=rootbasis(9,3),h=#I,roots=vector(9,i,sqrt(one+labels[i]*T+O(T^N))),products=vector(512),inverse=vector(512));
assert(h==140 && #Set(labels)==9,"same complete source");
for(i=1,9,assert(polcoef(roots[i],0,T)==one && valuation(roots[i]^2-(one+labels[i]*T),T)>=N,"normalized roots"));
products[1]=one+O(T^N);inverse[1]=products[1];
for(S=1,511,my(b=valuation(S,2));products[S+1]=products[S-2^b+1]*roots[b+1];inverse[S+1]=1/products[S+1]);
my(F=vector(h,i,T^I[i][2]*products[I[i][1]+1]),G=apply(f->f*inverse[512],F),FC=matrix(N,h,i,j,polcoef(F[j],i-1,T)),GC=matrix(N,h,i,j,polcoef(G[j],i-1,T)),J=submat(FC,[1..Q],[1..h]),Residue=matrix(h,Q,i,j,GC[Q+1-j,i]),C=Residue*J,K=matker(C),r1=matrank(C),rj=matrank(J),k=matsize(K)[2],PP=matker(Residue),rp=matsize(PP)[2]);
assert(C==mattranspose(C) && r1==79 && k==61 && C*K==matrix(h,k),"actual first cup/kernel");
assert(matrank(Residue)==rj && rp==Q-rj && rp>=1 && rp<=2,"complete liftable principal parts");
my(F0=FC*K,G0=GC*K,low=submat(F0,[1..Q],[1..k]),piv=matindexrank(PP)[1],coeff=matsolve(submat(PP,piv,[1..rp]),submat(low,piv,[1..k])));
assert(PP*coeff==low && Residue*PP==matrix(h,rp),"principal-part decomposition");
my(Hnum=matrix(N,rp),completion_checks=0);
for(j=1,rp,
 my(R=sum(i=0,Q-1,PP[i+1,j]*T^i),total=0*one+O(T^N));
 for(S=0,511,
  my(P=truncate(R*inverse[S+1]+O(T^Q)),bound=Q+floor((3-hammingweight(S))/2),term=P*products[S+1]);
  assert(poldegree(P)<=bound,"global infinity pole bound");
  assert(valuation(term-R,T)>=Q,"all character principal parts agree");
  total+=term;completion_checks++
 );
 total/=512*one;
 for(i=1,N,Hnum[i,j]=polcoef(total,i-1,T));
 assert(vector(Q,i,Hnum[i,j])==vector(Q,i,PP[i,j]),"selected lift has the exact principal part")
);
my(Hall=Hnum*coeff,RevG=matrix(k,N,i,j,G0[N+1-j,i]),A=RevG*Hall,C2=RevG*F0);
assert(A+mattranspose(A)==C2,"global residue/duality identity");
assert(mattranspose(K)*C==matrix(k,h),"full gauge quotient");
my(outforms=List(),survivors=List());
for(unit=1,2,
 my(gamma=unit*one,beta=gamma*(gamma+one)/2,O2=-gamma^2*A+beta*C2,rank=matrank(O2),gauge=matrix(N,k,i,j,if(j==1 && i>Q,FC[i-Q,3],0*one)));
 assert(RevG*(-gamma^2*(Hall+gauge)+beta*F0)==O2,"free V3 correction does not change quotient");
 assert(k-rank>=h-rj,"unit-digit survivor lower bound");
 listput(outforms,O2);listput(survivors,k-rank);
 print("SECOND_LIFT unit=",unit," first_rank=",r1," first_kernel=",k," jet_rank=",rj," kappa_minus_q_sections=",h-rj," principal_part_directions=",rp," second_rank=",rank," surviving_initial_sections=",k-rank)
);
assert(outforms[1]==-mattranspose(outforms[2]),"unit sign duality");
assert(low==matrix(Q,k),"first kernel equals q-vanishing sections");
my(Third=matrix(k,Q,i,j,G0[N+1-j,i])*submat(F0,[Q+1..N],[1..k]));
assert(Third==mattranspose(Third),"next restricted cup symmetry");
print("THIRD_RESTRICTED_CUP rank=",matrank(Third)," target=",k," determinant=",matdet(Third));

my(field=vector(27,j,one*((j-1)%3)+a*(((j-1)\3)%3)+a^2*((j-1)\9)),codes=Map(),out="research/results/bmd-exception-second-lift-20261008/data.g");
for(j=1,27,mapput(codes,Str(field[j]),j-1));
write(out,"LIFT_FIELD := [2,2,0,1];");
write(out,"LIFT_Q := ",Q,";");
write(out,"LIFT_J := ",vector(Q,i,vector(h,j,mapget(codes,Str(J[i,j])))),";");
write(out,"LIFT_C := ",vector(h,i,vector(h,j,mapget(codes,Str(C[i,j])))),";");
write(out,"LIFT_K := ",vector(h,i,vector(k,j,mapget(codes,Str(K[i,j])))),";");
write(out,"LIFT_PP := ",vector(Q,i,vector(rp,j,mapget(codes,Str(PP[i,j])))),";");
write(out,"LIFT_HNUM := ",vector(N,i,vector(rp,j,mapget(codes,Str(Hnum[i,j])))),";");
write(out,"LIFT_COEFF := ",vector(rp,i,vector(k,j,mapget(codes,Str(coeff[i,j])))),";");
write(out,"LIFT_F0 := ",vector(N,i,vector(k,j,mapget(codes,Str(F0[i,j])))),";");
write(out,"LIFT_G0 := ",vector(N,i,vector(k,j,mapget(codes,Str(G0[i,j])))),";");
write(out,"LIFT_O2 := ",vector(2,t,vector(k,i,vector(k,j,mapget(codes,Str(outforms[t][i,j]))))),";");
write(out,"LIFT_RANKS := ",vector(2,t,k-survivors[t]),";");
write(out,"LIFT_THIRD := ",vector(k,i,vector(k,j,mapget(codes,Str(Third[i,j])))),";");
write(out,"LIFT_THIRD_RANK := ",matrank(Third),";");
write(out,"LIFT_THIRD_DET := ",mapget(codes,Str(matdet(Third))),";");
print("SECOND_CENTRAL_LIFT_COMPLETED character_checks=",completion_checks," sign_duality=true gauge_invariant=true wall_ms=",getwalltime()-start);
}
quit;

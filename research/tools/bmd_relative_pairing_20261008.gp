\\ Test the actual relative pairing K_P x V2 at Q=(0,1,...,1), Cartier iterate4.
\\ K_P is the kernel of 256 marked jets on the complete303-column V4 of the fixed n9 curve.
\\ Prediction: a full47-rank pairing may exist away from P=Q; it is NOT a normality certificate.
\\ Stages: first distinct F_(3^8) point; cached complete jets; actual kernel;
\\ small Cartier blocks checked against81 direct coefficients; restricted pairing and stacked rank.
\\ Largest matrix303-square, smaller than the archived1024-square5s control; bounded to20s.
default(parisizemax,1500000000);
default(nbthreads,1);
assert(c,s)={if(!c,error(s));};
basis(d)={my(v=List());for(S=0,511,if(hammingweight(S)<=d,for(j=0,(d-hammingweight(S))\2,listput(v,[S,j]))));Vec(v);};
jetmat(labels,mark,wval,I,N)={
 my(one=labels[1]^0,roots=vector(9,i,wval[i]*sqrt(one+labels[i]/(one+labels[i]*mark)*T+O(T^N))),products=vector(512),co=vector(#I));
 for(i=1,9,assert(valuation(roots[i]^2-(one+labels[i]*mark+labels[i]*T),T)>=N,"marked square identity"));
 products[1]=one+O(T^N);
 for(S=1,511,if(hammingweight(S)<=4,my(b=valuation(S,2));products[S+1]=products[S-2^b+1]*roots[b+1]));
 for(j=1,#I,my(v=(mark+T)^I[j][2]*products[I[j][1]+1]);co[j]=vector(N,r,polcoef(v,r-1,T)));
 matrix(N,#I,r,j,if(r<=#co[j],co[j][r],0*one))
};
{
my(start=getwalltime(),modulus=ffinit(3,8,'a),a=ffgen(modulus,'a),one=a^0,q=6561,lc=[508,5690,5164,3098,2894,6147,276,4463,174],labels=apply(c->sum(j=0,7,(c\3^j)%3*a^j),lc));
assert(vector(9,j,lift(polcoef(modulus,j-1)))==[1,2,2,1,0,0,2,1,1],"same field");
my(I=basis(4),II=basis(2),point=0,wval=0,pc=-1,inspected=0);
assert(#I==303 && #II==47,"complete source dimensions");
for(code=1,q-1,
 my(v=sum(j=0,7,(code\3^j)%3*a^j),vals=apply(b->one+b*v,labels));
 inspected++;
 if(prod(i=1,9,vals[i])!=0 && prod(i=1,9,if(vals[i]^((q-1)/2)==one,1,0)),
  point=v;wval=apply(sqrt,vals);pc=code;break
 )
);
assert(pc>0,"no distinct unramified rational mark found");
print("RELATIVE_SETUP field=",modulus," labels=",lc," P_T_code=",pc," points_inspected=",inspected," Q_T=0 P_roots=",wval);
my(J=jetmat(labels,point,wval,I,256),K=matker(J),rk=matrank(J));
assert(rk==256 && matsize(K)==[303,47] && J*K==matrix(256,47),"actual47-dimensional kernel");
print("JET_KERNEL rank=",rk," dimension=",matsize(K)[2]," wall_ms=",getwalltime()-start);
my(polys=vector(512),rows=vector(512),direct=vector(512));
for(S=0,511,
 polys[S+1]=prod(i=1,9,if(bittest(S,i-1),one+labels[i]*T,one));
 my(h=(hammingweight(S)-1)\2);
 if(h>0,
  my(B=matrix(h,h,i,j,polcoef(polys[S+1],3*(i-1)+2-(j-1),T)),r=vector(h,j,if(j==1,one,0*one)));
  for(t=1,4,r=apply(x->x^3,r)*B);
  rows[S+1]=r;
  my(inv=1/sqrt(polys[S+1]+O(T^81)));
  assert(polcoef(inv,0,T)==one,"normalized inverse root atQ");
  direct[S+1]=vector(81,j,polcoef(inv,j-1,T))
 )
);
my(checks=0,C=matrix(303,47,i,j,
 my(S=I[i][1],R=II[j][1],U=bitxor(511,bitxor(S,R)),f=polys[bitand(S,R)+1]*T^(I[i][2]+II[j][2]),r=rows[U+1],value=sum(k=0,#r-1,r[k+1]*polcoef(f,k,T)),raw=sum(k=0,poldegree(f),polcoef(f,k,T)*direct[U+1][81-k]));
 assert(poldegree(f)<#r,"holomorphic product");
 assert(value==raw,"Cartier versus direct coefficient");checks++;value
));
my(Pair=mattranspose(K)*C,pr=matrank(Pair),stack=matconcat([J;mattranspose(C)]),sr=matrank(stack));
assert(sr==256+pr,"independent stacked rank identity");
print("RELATIVE_PAIRING iterate=4 q=81 rank=",pr," target=47 determinant=",matdet(Pair)," stacked_rank=",sr," direct_checks=",checks);
my(J0=jetmat(labels,0*one,vector(9,i,one),I,256),K0=matker(J0));
assert(J0*K0==matrix(256,matsize(K0)[2]),"same-mark kernel");
assert(mattranspose(K0)*C==matrix(matsize(K0)[2],47),"same-mark low-jet vanishing control");
print("SAME_MARK_CONTROL rank=",matrank(J0)," pairing_zero=true");
my(field=vector(q,j,sum(k=0,7,((j-1)\3^k)%3*a^k)),codes=Map(),out="research/results/bmd-exception-relative-pairing-20261008/matrices.g");
for(j=1,q,mapput(codes,Str(field[j]),j-1));
write(out,"REL_FIELD := ",vector(9,j,lift(polcoef(modulus,j-1))),";");
write(out,"REL_J := ",vector(256,i,vector(303,j,mapget(codes,Str(J[i,j])))),";");
write(out,"REL_C := ",vector(303,i,vector(47,j,mapget(codes,Str(C[i,j])))),";");
write(out,"REL_RANK := ",pr,";");
print("EXPORTED_MATRICES=",out);

print("RELATIVE_PAIRING_COMPLETED wall_ms=",getwalltime()-start," full_pairing=",pr==47," no_normality_claim=true");
}
quit;

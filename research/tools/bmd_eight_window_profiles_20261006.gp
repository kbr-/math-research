\\ Complete ternary support-window/profile inventory, not a normality sample.
\\ Nine Lucas-period profiles and32 powers of3 mod128; no original jet matrices.
default(parisizemax,500000000);
default(nbthreads,1);
if(default(nbthreads)!=1,error("threads"));
assert(c,s)={if(!c,error(s));};
profile(c,m)={
 my(top=2*c+if(m==3,1,3),rows=if(m==3,[1,3,5],[1,3,5,2*c+2]),piv=List(),B=matrix(#rows,0),rank=0);
 forstep(j=top,0,-1,
  my(col=vector(#rows,i,Mod(binomial(j,rows[i]),3))~,C=matconcat([B,Mat(col)]));
  if(matrank(C)>rank,listput(piv,j);B=C;rank++);
  if(rank==#rows,break);
 );
 assert(rank==#rows,"profile rank");
 my(E=select(j->!setsearch(Set(Vec(piv)),j),[0..top]),first=0);
 while(setsearch(Set(E),first),first++);
 [first-1+m-2*c,apply(j->j-2*c,select(j->j>first-1,E)),apply(j->j-2*c,Vec(piv))];
};
shape(c)={my(A=profile(c,3),B=profile(c,2),ta=A[1],tb=B[1]);if(#A[2],ta=max(ta,3+vecmax(A[2])));if(#B[2],tb=max(tb,2+vecmax(B[2])));my(K=max(3+2*ta,4+2*tb),kap=2*K-7);assert(2*c+A[1]+1+#A[2]==2*c+2,"A dimension");assert(2*c+B[1]+1+#B[2]==2*c+2,"B dimension");[A,B,K,kap];};
{
my(S=vector(9,j,shape(54+j-1)),count=0,maxdim=0);
print("PROFILE columns: residue, A_bound_offset,A_outlier_offsets,A_pivot_offsets, B_bound_offset,B_outlier_offsets,B_pivot_offsets,K,codimension");
for(r=0,8,
 assert(shape(63+r)==S[r+1] && shape(81+r)==S[r+1],"Lucas-period shape");
 print("PROFILE ",r," ",S[r+1]);
);
assert(lift(Mod(3,128)^32)==1 && lift(Mod(3,128)^16)!=1,"period32");
print("WINDOW columns: exponent_mod32,residue128,delta=q-N,gap=r-alpha,d_mod27,upper_profile,lower_profile,upper_cuts,lower_cuts,free,extra,matching_dim,z_denominator_power,first_valid_exponent");
for(e=0,31,
 my(R=lift(Mod(3,128)^e));
 if(R<64,next);
 my(delta=R-64,gap=(63-delta)/2,dr=((320-delta)*23)%27,cu=(8*dr-17)%9,cl=(cu+1)%9,U=S[cu+1],V=S[cl+1],nu=U[4],nl=V[4],free=max(nl-gap,0),extra=max(gap-nl,0),dim=nu+max(nl,gap),m0=26+U[3]-V[3],first=e);
 while(first<6,first+=32);
 assert(gap>=0 && gap<=31 && nu+gap+free==dim && nu+nl+extra==dim,"square matching count");
 assert(dim<=52,"uniform matching size");
 print("WINDOW ",[e,R,delta,gap,dr,cu,cl,nu,nl,free,extra,dim,m0,first]);
 count++;maxdim=max(maxdim,dim);
);
assert(count==16,"complete support count");
print("PASS profiles9, supported residue classes=",count," maximum matching dimension=",maxdim);
}
quit;

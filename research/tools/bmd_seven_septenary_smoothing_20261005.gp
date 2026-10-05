\\ Actual first-survivor smoothing at p7,c=7t. One smallest-family control d10.
\\ Effective parameter q=epsilon^7, y=sqrt(1+q*T^7), psi=2*T^7/(1+y).
\\ Exact full saturated blocks: y*T^j (j<m), g*T^r*psi^k (0<=k<=Kr).
\\ Two effective orders test whether the first or quadratic kernel-cokernel term repairs the boundary.
default(parisizemax,3000000000);
default(threadsize,64000000);
default(threadsizemax,512000000);
default(nbthreads,1);
setrand(20261005);
if(default(nbthreads)!=1,quit(1));
assert(c,s)={if(!c,error(s));};
{
my(d=10,p=7,c=8*d-17,t=c/7,N=8*c+8,g=ffgen(p^4,'a),o=g^0,u=random(g));
while(u==0 || u^4==o,u=random(g));
assert(c%7==0 && c>=23,"remaining bulk family");
my(L=o+u^2/(u^2+1)^2*T+O(T^N),H=o+u^2/(u^2-1)^2*T+O(T^N),v=sqrt(L),w=sqrt(H));
my(pref=[v,w^3,L,v*w^3],factors=[L*H^2,L*H^2,H^2,H^2],prefix=vector(8));
for(a=1,4,prefix[2*a-1]=vector(N,j,polcoef(pref[a],j-1,T));prefix[2*a]=vector(N,j,polcoef(pref[a]*factors[a],j-1,T)));
my(cols=List());
for(a=1,4,
 my(m=if(a<=2,3,2));
 for(j=0,m-1,listput(cols,[2*a-1,j,-1]));
 for(r=0,6,
  my(A=(c-r)\7,B=(c-m-r)\7,Kr=A+B+1);
  assert(A==B || A==B+1,"consecutive polynomial-in-y block");
  for(k=0,Kr,listput(cols,[2*a,r+7*k,k]));
 );
);
assert(#cols==N,"full source dimension");
print("d=",d," p=",p," c=",c," N=",N," effective_parameter=epsilon^7 u=",u," seed=20261005 threads=",default(nbthreads));
my(J=vector(3));
for(h=0,2,
 J[h+1]=matrix(N,N,i,j,
  my(b=cols[j],index=i-b[2]-7*h,k=b[3],cf=if(h==0,o,if(k<0,if(h==1,o/2,-o/8),if(h==1,-k*o/4,k*(k+3)*o/32))));
  if(index<=0,0*o,cf*prefix[b[1]][index])
 );
);
print("three cached-prefix coefficient matrices prepared");
my(ij=matindexrank(J[1]),I=ij[1],K=ij[2],rank=#I);
print("boundary_rank=",rank," corank=",N-rank);
assert(rank==N-1,"corank-one control required");
my(fi=setminus(vector(N,j,j),Set(I))[1],fj=setminus(vector(N,j,j),Set(K))[1],B=vecextract(J[1],I,K));
my(r=vector(N,j,0*o)~,l=vector(N,j,0*o),rr=-matsolve(B,vector(N-1,i,J[1][I[i],fj])~),ll=-matsolve(B~,vector(N-1,j,J[1][fi,K[j]])~));
r[fj]=o;l[fi]=o;for(i=1,N-1,r[K[i]]=rr[i];l[I[i]]=ll[i]);
assert(J[1]*r==vector(N,i,0*o)~ && l*J[1]==vector(N,i,0*o),"exact boundary kernels");
my(rhs=J[2]*r,first=l*rhs);print("first_effective_obstruction=",first);
if(first==0,
 my(correction=vector(N,j,0*o)~,sol=-matsolve(B,vector(N-1,i,rhs[I[i]])~));
 for(i=1,N-1,correction[K[i]]=sol[i]);
 assert(J[1]*correction+rhs==vector(N,j,0*o)~,"first lift solves every marked equation");
 my(second=l*(J[3]*r+J[2]*correction));
 print("second_effective_obstruction=",second);
 if(second!=0,print("PASS: quadratic effective repair, epsilon order14, at this exact control"),print("INCONCLUSIVE: repair needs higher effective order or another source"));
,
 print("PASS: first effective repair, epsilon order7, at this exact control")
);
print("DONE: finite deformation check only; uniform coefficient remains unproved.");
}
quit;

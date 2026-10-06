\\ First/second effective coefficient at the smallest p7,D0mod7 member, d10.
\\ Reuse the established full Frobenius basis; every character has the degree-three cut g=r^2*s^4.
\\ One pivot inverse supplies both kernels and any needed correction; stop at the first nonzero obstruction.
default(parisizemax,3000000000);
default(nbthreads,1);
assert(c,s)={if(!c,error(s));};
{
my(d=10,p=7,D=16*d-41,N=8*(D+1),modulus=ffinit(7,4,'a),a=ffgen(modulus,'a),o=a^0,u=a);
assert(D%7==0 && u!=0 && u^4!=1,"ordinary failed-family source and admissible mark");
my(R=o+u^2/(u^2+1)^2*T+O(T^N),S=o+u^2/(u^2-1)^2*T+O(T^N),r=sqrt(R),s=sqrt(S),g=R*S^2,pref=[r^3,R,s^3,r*s^3],prefix=vector(8));
for(ch=1,4,prefix[2*ch-1]=vector(N,j,polcoef(pref[ch],j-1,T));prefix[2*ch]=vector(N,j,polcoef(pref[ch]*g,j-1,T)));
my(cols=List());
for(ch=1,4,
 for(j=0,2,listput(cols,[2*ch-1,j,-1]));
 for(res=0,6,my(A=(D-res)\7,B=(D-3-res)\7,K=A+B+1);assert(A==B || A==B+1,"balanced Frobenius block");for(k=0,K,listput(cols,[2*ch,res+7*k,k])));
);
assert(#cols==N,"complete full-source frame count");
my(J0=matrix(N,N,i,j,my(b=cols[j],ix=i-b[2]);if(ix<=0,0*o,prefix[b[1]][ix])));
print("FIELD=",modulus," d=",d," D=",D," N=",N," u=",u," effective_parameter=epsilon^7");
my(ij=matindexrank(J0),I=ij[1],K=ij[2],rk=#I);print("BOUNDARY_RANK=",rk);assert(rk==N-1,"corank-one calibration");
my(fi=setminus(vector(N,j,j),Set(I))[1],fj=setminus(vector(N,j,j),Set(K))[1],Pivot=vecextract(J0,I,K),Inv=Pivot^-1,ker=vector(N,j,0*o)~,coker=vector(N,j,0*o));
my(right=-Inv*vector(N-1,i,J0[I[i],fj])~,left=-vector(N-1,j,J0[fi,K[j]])*Inv);
ker[fj]=o;coker[fi]=o;for(j=1,N-1,ker[K[j]]=right[j];coker[I[j]]=left[j]);
assert(J0*ker==vector(N,j,0*o)~ && coker*J0==vector(N,j,0*o),"both exact normalized kernels");
my(J1=matrix(N,N,i,j,my(b=cols[j],ix=i-b[2]-7,k=b[3]);if(ix<=0,0*o,if(k<0,o/2,-k*o/4)*prefix[b[1]][ix])),rhs=J1*ker,first=coker*rhs);
print("OMITTED_ROW=",fi," OMITTED_COLUMN=",fj);print("RIGHT_KERNEL=",ker);print("LEFT_KERNEL=",coker);print("FIRST_EFFECTIVE_OBSTRUCTION=",first);
if(first==0,
 my(correction=vector(N,j,0*o)~,sol=-Inv*vector(N-1,i,rhs[I[i]])~);for(j=1,N-1,correction[K[j]]=sol[j]);assert(J0*correction+rhs==vector(N,j,0*o)~,"first lift solves every row");
 my(J2=matrix(N,N,i,j,my(b=cols[j],ix=i-b[2]-14,k=b[3]);if(ix<=0,0*o,if(k<0,-o/8,k*(k+3)*o/32)*prefix[b[1]][ix])),second=coker*(J2*ker+J1*correction));
 print("SECOND_EFFECTIVE_OBSTRUCTION=",second);
 if(second!=0,print("PASS quadratic effective repair at this point"),print("INCONCLUSIVE through effective order2"));
,
 print("PASS first effective repair, epsilon order7, at this point");
);
print("DONE finite effective-order control; no larger degree sampled.");
}
quit;

\\ Does the actual elliptic source survive the smallest p7,d3mod7 failed conic family?
\\ Two independent admissible points at d10 only; stop at the first nonzero determinant.
default(parisizemax,3000000000);
default(nbthreads,1);
assert(c,s)={if(!c,error(s));};
{
my(d=10,D=16*d-41,N=8*(D+1),modulus=ffinit(7,4,'a),a=ffgen(modulus,'a),o=a^0,success=0);
assert((D-5)%7!=0,"ordinary elliptic source");print("FIELD=",modulus," d=",d," D=",D," N=",N);
for(trial=1,2,
 my(slopes=if(trial==1,[o,a,a^2],[o,a+o,a^2+a]));
 assert(#Set(slopes)==3 && !setsearch(Set(slopes),0*o),"distinct nonzero slopes");
 my(v=sqrt(o+slopes[1]*T+O(T^N)),w=sqrt(o+slopes[2]*T+O(T^N)),z=sqrt(o+slopes[3]*T+O(T^N)),pre=[v^3*w^4,v^2*w^7,v^2*z^7,v*w^3*z^7,v^2*w^4,v*w^7,v*z^7,w^3*z^7]);
 my(R=vector(N,j,pre[(j-1)\(D+1)+1]*T^((j-1)%(D+1))),M=matrix(N,N,i,j,polcoef(R[i],j-1,T)),rk=matrank(M));
 print("trial=",trial," slopes=",slopes," rank=",rk," corank=",N-rk);
 if(rk==N,success=1;break);
);
print("FULL_ELLIPTIC_CERTIFIED=",success,"; failed points alone do not establish generic nonnormality.");
}
quit;

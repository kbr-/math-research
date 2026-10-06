\\ Smallest failed conic state: does the full less-degenerate elliptic source survive?
default(parisizemax,1000000000);
default(nbthreads,1);
assert(c,s)={if(!c,error(s));};
{
my(d=6,D=16*d-41,N=8*(D+1),modulus=ffinit(3,10,'a),a=ffgen(modulus,'a),o=a^0,slopes=[o,a,a^2]);
assert(#Set(slopes)==3 && !setsearch(Set(slopes),0*o),"distinct nonzero slopes");
my(v=sqrt(o+slopes[1]*T+O(T^N)),w=sqrt(o+slopes[2]*T+O(T^N)),z=sqrt(o+slopes[3]*T+O(T^N)),pre=[v^3*w^4,v^2*w^7,v^2*z^7,v*w^3*z^7,v^2*w^4,v*w^7,v*z^7,w^3*z^7]);
assert((16*d-46)%3!=0,"ordinary elliptic source");
my(R=vector(N,j,pre[(j-1)\(D+1)+1]*T^((j-1)%(D+1))),M=matrix(N,N,i,j,polcoef(R[i],j-1,T)),rank=matrank(M));
print("FIELD=",modulus," slopes=",slopes," d=",d," D=",D," N=",N," rank=",rank);
assert(rank==N,"elliptic source not certified at chosen control");
print("PASS full elliptic source normal at d6,p3; the failed conic boundary is not an original nonnormality witness.");
}
quit;

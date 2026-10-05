\\ Smallest unresolved d=10,p7: does the actual full elliptic source retain the lost direction?
\\ The proved paired-criterion table owns the source; compute eight coefficient prefixes once.
\\ One finite exact rank test, no all-degree inference or duplicate ambient reductions.
default(parisizemax,3000000000);
default(threadsize,64000000);
default(threadsizemax,512000000);
default(nbthreads,1);
setrand(20261005);
if(default(nbthreads)!=1,quit(1));
{
my(d=10,p=7,c=8*d-17,N=8*(c+1),M=2*c+11,e=6,g=ffgen(p^e,'a),o=g^0);
my(aa=vector(3,i,random(g)));
while(#Set(aa)!=3 || prod(i=1,3,aa[i])==0,aa=vector(3,i,random(g)));
print("seed=20261005 effective_threads=",default(nbthreads)," d=",d," p=",p," N=",N," M=",M," extension_degree=",e," slopes=",aa);
my(ll=vector(3,i,o+aa[i]*T+O(T^N)),ww=apply(sqrt,ll));
my(exps=[[2,2,0],[2,2,0],[1,3,0],[1,3,0],[1,0,3],[1,0,3],[0,1,3],[0,1,3]]);
my(prefix=vector(8,s,vector(N,j,0*o)));
for(s=0,7,
 my(row=prod(i=1,3,ll[i]^exps[s+1][i]*if(bittest(s,i-1),ww[i],o)));
 prefix[s+1]=vector(N,j,polcoef(row,j-1,T));
);
print("eight complete coefficient prefixes prepared; building sole marked matrix");
my(J=matrix(N,N,i,j,if(i-1<(j-1)%(c+1),0*o,prefix[(j-1)\(c+1)+1][i-(j-1)%(c+1)])));
print("marked matrix prepared; exact rank");
my(r=matrank(J));
print("full_source_rank=",r," source_dimension=",N," corank=",N-r);
print("DONE: exact finite elliptic test; no uniform inference.");
}
quit;

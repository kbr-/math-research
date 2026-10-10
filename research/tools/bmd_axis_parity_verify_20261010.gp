\\ Independent full determinant, norm, and weighted-linear-basis-bound replay.
default(parisizemax,1000000000);
default(parisize,128000000);
default(nbthreads,1);
x='x;z='z;T=varhigher("T");
assert(c,s)={if(!c,error(s));};
normpoly(P,p,e)={if(P==0,return(0));my(NP=1);for(j=0,e-1,NP*=sum(k=0,poldegree(P,x),polcoef(P,k,x)^(p^j)*x^k));NP};
read(getenv("BMD_AXIS_DATA"));
{
my(d=DATA,n=d[1],p=d[2],e=d[3],N=n+1,m=n*N/2+2,g,o,field=Mod(1,p)*Polrev(d[4],z));
assert(polisirreducible(field),"irreducible field");
if(e==1,g=Mod(0,p);o=Mod(1,p),g=ffgen(field,'g);o=g^0);
my(al=concat([0*o],vector(n,i,sum(j=0,e-1,d[5][i][j+1]*g^j))),
 be=concat([0*o],vector(n,i,sum(j=0,e-1,d[6][i][j+1]*g^j))));
assert(#Set(al[1..n])==n&&al[N]==0,"distinct old roots and zero axis intercept");
assert(be[N]==1&&vector(n,i,be[i])==vector(n,i,0*o),"exact one-root direction");
my(S=sqrt(Mod(1,p)+T+O(T^(m+1))),bs=vector(m+1,i,polcoef(S,i-1,T)),J=select(j->bs[j+1]!=0,[0..m-1]),t=#J,penalty=d[8],labels=List(),weights=List());
for(j=2,t,listput(labels,[0,j]);listput(weights,J[j]));
for(j=0,m-1,listput(labels,[1,j]);listput(weights,j+penalty));
my(order=vecsort(Vec(weights),,5));
\\ Independent greedy rank checks on one small transfer matrix, not a production series.
my(B=matrix(t,0),ranknow=0,total=0);
for(ii=1,#order,
 my(c=order[ii],lab=labels[c],v=if(lab[1]==0,vector(t,i,Mod(i==lab[2],p))~,vector(t,i,if(lab[2]>=J[i],bs[lab[2]-J[i]+1],Mod(0,p)))~),trial=concat(B,v),rr=matrank(trial));
 if(rr>ranknow,B=trial;ranknow=rr;total+=weights[c]);
 if(ranknow==t,break)
);
assert(ranknow==t&&total-sum(i=1,t,J[i])-penalty*n==d[7],"independent weighted basis upper bound");
print("AXIS_BOUND_REPLAY n=",n," p=",p," upper=",d[7]," penalty=",penalty);
my(aa=vector(N,i,al[i]+x*be[i]),L=m+1,rows=List([vector(L,j,if(j==1,o,0*o)),vector(L,j,if(j==2,o,0*o))]));
for(i=1,N,for(j=i+1,N,
 my(F=sqrt((o+aa[i]*T)*(o+aa[j]*T)+O(T^L)));
 listput(rows,vector(L,c,polcoef(F,c-1,T)))
));
my(M=matrix(m,L,i,j,rows[i][j]),V=prod(i=1,N,prod(j=i+1,N,aa[j]-aa[i])));
print("AXIS_FULL_DETERMINANTS n=",n," p=",p," size=",m);
my(D=matdet(matrix(m,m,i,j,M[i,j])),A=matdet(matrix(m,m,i,j,if(j<m,M[i,j],M[i,m+1]))),
 ND=normpoly(D,p,e),NA=normpoly(A,p,e),NV=normpoly(V,p,e),lc=pollead(ND),GD=Mod(1,p)*Polrev(d[9],x),GA=Mod(1,p)*Polrev(d[10],x));
assert(poldegree(ND,x)==e*d[7],"full axis degree");
assert(o*GD==ND/lc&&o*GA==NA/lc,"every coefficient of both original determinant norms");
assert(o*Mod(1,p)*Polrev(d[11],x)==NV,"complete Vandermonde norm");
my(G=gcd(GD,GA));
for(ii=1,#d[13],
 my(pos=d[13][ii][1]+1,raw=matdet(matrix(m,m,i,j,if(j==pos,M[i,m+1],M[i,j]))),nr=normpoly(raw,p,e),stored=Mod(1,p)*Polrev(d[13][ii][2],x));
 assert(o*stored==nr/lc,"complete additional cofactor norm");G=gcd(G,stored)
);
my(storedg=Mod(1,p)*Polrev(d[12],x),storedv=Mod(1,p)*Polrev(d[11],x),VP=storedv^N);
G/=pollead(G);VP/=pollead(VP);
assert(G==storedg&&G==VP,"exact common frame and no residual gcd");
print("AXIS_CERTIFICATE_PASS n=",n," p=",p," e=",e," original_norm_degree=",poldegree(GD,x)," residual_degree=",d[7]-n*N," minors=",2+#d[13]);
print("AXIS_PARITY_INDEPENDENT_COMPLETED");
}
quit;

\\ Actual Frobenius-top coefficient of adjacent K_s and its first deformation.
\\ Test n=6 (known sharp coefficient control), then n=18 (next n=2*3^m).
\\ One shifted matrix replaces the last root by tau^alpha, alpha=(q+1)/2.
\\ Matrices are N=23,173; no whole-polynomial expansion or normality survey.
default(parisizemax,2000000000);
default(nbthreads,1);
setrand(20261005);
if(default(nbthreads)!=1,error("threads"));
C(j)=if(j==0,1,(-1)^(j-1)*binomial(2*j-2,j-1)/2^(2*j-1)/j);
root(a,N)={my(v=vector(N));v[1]=a^0;for(j=1,N-1,v[j+1]=Mod(numerator(C(j)),3)/Mod(denominator(C(j)),3)*a^j);my(f=Polrev(v,'t));if((f^2-1-a*t)%t^N!=0,error("root"));f};
col(f,N)=vector(N,j,polcoef(f,j-1,'t))~;
test(n,F)={
my(s=n-4,N=n*(n+1)/2+2,q=3,aa=F^0,g=1-aa*t);
while(q<N,q*=3);
my(alpha=(q+1)/2,v=root(-aa,N),bs=vector(s-1,i,F^i+1),w=vector(s-1,i,root(bs[i],N)),B=List(),D=List());
if(#Set(concat([-aa,0],bs))!=s+1,error("slopes"));
for(j=0,5,listput(B,t^j);listput(D,if(j==5,2*t^6,-j*t^(j+1))));
for(j=0,4,listput(B,v*t^j);listput(D,-j*v*t^(j+1)));
listput(B,v*t^6);listput(D,0);
for(i=1,s-1,
 for(j=0,1,listput(B,v*w[i]*t^j);listput(D,0));
 for(j=0,2,listput(B,g*w[i]*t^j);listput(D,-j*g*w[i]*t^(j+1))));
for(i=1,s-1,for(j=i+1,s-1,listput(B,g*w[i]*w[j]);listput(D,0)));
\\ New root columns with w_s replaced by tau^alpha, order moved to the end.
for(j=0,1,listput(B,t^alpha*v*t^j);listput(D,0));
for(j=0,2,listput(B,t^alpha*g*t^j);listput(D,-j*t^alpha*g*t^(j+1)));
for(i=1,s-1,listput(B,t^alpha*g*w[i]);listput(D,0));
if(#B!=N,error("count"));
my(J=Mat(vector(N,j,col(B[j],N))),JD=Mat(vector(N,j,col(D[j],N))),r=matrank(J),R=matker(J),L=matker(J~),repair=if(r<N,L~*JD*R,0));
print("n=",n," N=",N," q=",q," alpha=",alpha," top_parameter_degree=",n*alpha," rank=",r," corank=",N-r);
print("parameters=",bs);
print("first_repair_rank=",if(r<N,matrank(repair),0)," repair_matrix=",repair);
if(r==N,print("moving_boundary_determinant=",matdet(J)));
if(n==6,
 my(chi=0);
 for(i=1,N,if(JD[,i]!=vector(N,j,0)~,my(Q=J);Q[,i]=JD[,i];chi+=matdet(Q)));
 print("moving_first_coefficient=",chi);
 if(chi!=F^4+2*F^3+F^2+F,error("saved symbolic coefficient mismatch"));
);
};
{
my(F=ffgen(ffinit(3,5,'a),'a));print("field=",F.mod);
test(6,F);
test(18,F);
}

\\ Test the full adjacent second-merge source K_s, not original normality.
\\ s=0,1,2,3 tests constant-corank and first-order-repair assumptions.
\\ Exact F_(3^5) controls; no dimension sweep or all-dimensional rank claim.
default(parisizemax,1000000000);
default(nbthreads,1);
setrand(20261005);
if(default(nbthreads)!=1,error("thread setting"));
C(j)=if(j==0,1,(-1)^(j-1)*binomial(2*j-2,j-1)/2^(2*j-1)/j);
root(a,N)={my(v=vector(N));v[1]=a^0;for(j=1,N-1,v[j+1]=Mod(numerator(C(j)),3)/Mod(denominator(C(j)),3)*a^j);my(f=Polrev(v,'t));if((f^2-1-a*t)%t^N!=0,error("square root"));f};
col(f,N)=vector(N,j,polcoef(f,j-1))~;
make(s,aa)={my(N=12+5*s+s*(s-1)/2,g=1-aa[1]*t,v=root(-aa[1],N),w=vector(s,i,root(aa[i+1],N)),B=List(),D=List(),z=aa[1]*0);
for(j=0,5,listput(B,t^j);listput(D,if(j==5,2*t^6,z)));
for(j=0,4,listput(B,v*t^j);listput(D,if(j==4,2*v*t^5,z)));
listput(B,v*t^6);listput(D,z);
for(i=1,s,
 for(j=0,1,listput(B,v*w[i]*t^j);listput(D,z));
 for(j=0,2,listput(B,g*w[i]*t^j);listput(D,if(j==2,g*w[i]*t^3,z))));
for(i=1,s,for(j=i+1,s,listput(B,g*w[i]*w[j]);listput(D,z)));
if(#B!=N,error("dimension"));
[Mat(vector(N,j,col(B[j],N))),Mat(vector(N,j,col(D[j],N)))];
};
{
my(ep=Mod(1,3)*e,bet=Mod(1,3)*b,y=2*(x-1)/ep,H=vector(7,i,sum(j=0,i-1,if(j%2,binomial(i-1,j)*(-1)^(i-1-j)*(1+ep*bet)^((j-1)/2),0))));
if(H[7]!=1+ep*bet,error("unit denominator"));
for(i=0,5,
 my(ci=2^(i-6)*ep^(6-i)*H[i+1]/H[7],f=y^i-ci*y^6,cut=sum(j=0,6,if(j%2,polcoef(f,j,x)*(1+ep*bet)^((j-1)/2),0)));
 if(cut!=0,error("finite cut"));
 if(polcoef(ci+O(e^2),1,e)!=if(i==5,Mod(2,3),0),error("first correction"));
);
for(i=0,6,if(i!=5 && polcoef(y^i,5,x)!=0,error("odd degree cut")));
print("all_saturated_basis_cut_identities=passed; first_corrections=passed");
my(F=ffgen(ffinit(3,5,'a),'a));
print("field=",F.mod);
my(aa=F+1,bb=F^2+1,v=root(-aa,12),x=root(bb,12),g=1-aa*t,B=List());
for(j=0,3,listput(B,t^j);listput(B,v*t^j));
for(j=0,1,listput(B,v*x*t^j);listput(B,g*x*t^j));
print("s0_undeformed_one_merge_rank=",matrank(Mat(vector(12,j,col(B[j],12)))));
for(s=0,3,
 my(aa=vector(s+1,j,F^j+1),JD=make(s,aa),J=JD[1],D=JD[2],N=matsize(J)[1],R=matker(J),L=matker(J~),rank=matrank(J));
 print("s=",s," n=",s+4," N=",N," parameters=",aa," boundary_rank=",rank," corank=",N-rank);
 print("first_variation_cokernel_rank=",if(N==rank,0,matrank(L~*D*R)));
 if(s==0 && (rank!=11 || matrank(L~*D*R)!=0),error("rational obstruction control"));
);
}

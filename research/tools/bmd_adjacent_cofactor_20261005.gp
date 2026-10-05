\\ Test candidate all-dimensional recurrence: the adjacent first repair
\\ coefficient is divisible by the smaller one-merge determinant, up to
\\ collision factors. Cases s=1 and s=2 test the first coupled extension, a=1.
\\ Exact F3[b] and F_(3^5)[b], N=17,23. No dimension sweep.
default(parisizemax,1000000000);
default(nbthreads,1);
if(default(nbthreads)!=1,error("threads"));
C(j)=if(j==0,1,(-1)^(j-1)*binomial(2*j-2,j-1)/2^(2*j-1)/j);
root(a,N)={my(v=vector(N));v[1]=a^0;for(j=1,N-1,v[j+1]=Mod(numerator(C(j)),3)/Mod(denominator(C(j)),3)*a^j);my(f=Polrev(v,'t));if((f^2-1-a*t)%t^N!=0,error("root"));f};
col(f,N)=vector(N,j,polcoef(f,j-1,'t))~;
test(aa,bs,label)={
my(s=#bs,N=12+5*s+s*(s-1)/2,M=N-s-4,g=1-aa*t,v=root(-aa,N),w=vector(s,i,root(bs[i],N)),B=List(),D=List(),E=List());
for(j=0,5,listput(B,t^j);listput(D,if(j==5,2*t^6,0)));
for(j=0,4,listput(B,v*t^j);listput(D,if(j==4,2*v*t^5,0)));
listput(B,v*t^6);listput(D,0);
for(i=1,s,
 for(j=0,1,listput(B,v*w[i]*t^j);listput(D,0));
 for(j=0,2,listput(B,g*w[i]*t^j);listput(D,if(j==2,g*w[i]*t^3,0))));
for(i=1,s,for(j=i+1,s,listput(B,g*w[i]*w[j]);listput(D,0)));
my(J=Mat(vector(N,j,col(B[j],N))),JD=Mat(vector(N,j,col(D[j],N))),bd=matdet(J),chi=0);
print("case=",label," parameters=",bs," N=",N," lower_N=",M," boundary_det=",bd);
if(bd!=0,error("boundary normal: reconsider target"));
for(i=1,N,if(JD[,i]!=vector(N,j,0)~,my(Q=J);Q[,i]=JD[,i];chi+=matdet(Q)));
for(j=0,3,listput(E,t^j);listput(E,v*t^j));
for(i=1,s,for(j=0,1,listput(E,v*w[i]*t^j);listput(E,g*w[i]*t^j)));
for(i=1,s,for(j=i+1,s,listput(E,g*w[i]*w[j])));
if(#E!=M,error("lower source dimension"));
my(old=matdet(Mat(vector(M,j,col(E[j],M)))),rem=chi%old);
print("lower_det=",old);print("repair_coefficient=",chi);
print("lower_factors=",factor(old));print("repair_factors=",factor(chi));
print("division_remainder=",rem);

if(rem==0,print("quotient=",chi/old," quotient_factors=",factor(chi/old)));
if(s==2,
 my(z=b,oldcut=z^18*(z+1)^14*(z-bs[1])^10,newcut=z^31*(z+1)^20*(z-bs[1])^15);
 if(old%oldcut!=0 || chi%newcut!=0,error("collision division"));
 my(P=old/oldcut,Q=chi/newcut);
 P/=pollead(P);Q/=pollead(Q);
 print("primitive_lower=",P);print("primitive_repair=",Q);print("primitive_gcd=",gcd(P,Q));
 if(poldegree(gcd(P,Q))!=0,error("primitive gcd"));
 my(fac=factor(P),c0=0,got=0);
 for(i=1,matsize(fac)[1],if(poldegree(fac[i,1])==1,c0=-polcoef(fac[i,1],0);got=1;break));
 if(!got,error("linear witness"));
 my(Jpoint=subst(J,z,c0),pointChi=subst(chi,z,c0),pointOld=subst(old,z,c0));
 if(c0==0 || c0==-1 || c0==bs[1] || pointOld!=0 || pointChi==0,error("witness"));
 print("off_collision_witness=",c0," old=",pointOld," chi=",pointChi," boundary_rank=",matrank(Jpoint));
 my(ip=matindexrank(Jpoint),minor=matdet(matrix(#ip[1],#ip[2],i,j,J[ip[1][i],ip[2][j]])),qfac=factor(Q),h=0);
 for(i=1,matsize(qfac)[1],if(poldegree(qfac[i,1])==3,h=qfac[i,1];break));
 if(h==0,error("cubic witness"));
 print("pivot_rows=",ip[1]," pivot_columns=",ip[2]);
 print("witness_gcd_degrees=",vector(3,i,poldegree(gcd([old,minor,z*(z+1)*(z-bs[1])][i],h))));
 if(poldegree(gcd(old,h))!=0 || poldegree(gcd(minor,h))!=0 || poldegree(gcd(z*(z+1)*(z-bs[1]),h))!=0,error("witness common root"));
 print("reverse_witness_irreducible=",h," lower_mod_h=",old%h," cofactor_mod_h=",minor%h);
 if(old%h==0 || minor%h==0 || chi%h!=0,error("reverse witness"));
 print("reverse_witness=lower_normal_boundary_corank1_first_repair_zero");
);

};
{
b=varlower("parameter",'t);
test(Mod(1,3),[Mod(1,3)*b],"s1 symbolic");
my(F=ffgen(ffinit(3,5,'a),'a));
print("field=",F.mod);
test(F^0,[F+1,F^0*b],"s2 one symbolic root");
}

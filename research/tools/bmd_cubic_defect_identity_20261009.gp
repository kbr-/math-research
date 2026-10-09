\\ Exact polynomial identities over F3[A,B,t,u], not sampled field values.
\\ Keep3x3 cubic remainders; verify the original square-root coefficients,
\\ both mixed coefficient tables, and the first nonzero defect at q10.
default(parisizemax,500000000);
default(parisize,64000000);
x='x;y='y;A='A;B='B;t='t;u='u;o=Mod(1,3);
FX=o*(x^3+A*x^2+B*x-t);FY=o*(y^3+A*y^2+B*y-u);
red(P)={my(R=P%FX,Z=0*o);for(i=0,2,Z+=x^i*(polcoef(R,i,x)%FY));Z};
coef(P,i,j)=polcoef(polcoef(P,i,x),j,y);
{
my(s=o*(x+y),v=o*x*y,d=o*(x-y)^2,Q=vector(11,i,0*o),G=vector(13,i,0*o));
Q[1]=o;G[1]=o;G[2]=s/2;
for(l=1,10,Q[l+1]=red(s*Q[l]+if(l>=2,d*sum(h=0,l-2,Q[h+1]*Q[l-1-h]),0*o)));
for(l=2,12,G[l+1]=red((if(l==2,v,0*o)-sum(h=1,l-1,G[h+1]*G[l-h+1]))/2));
for(l=0,10,if(G[l+3]!=red(d*Q[l+1]),error("original root coefficient mismatch")));
my(expected=[0,0,0,0,A,-B,A*B,-A^4+A^2*B-A*(t+u),-A^3*B+A*B^2+B*(t+u),0]*o);
for(l=0,9,
 if(coef(Q[l+1],2,1)!=expected[l+1]||coef(Q[l+1],1,2)!=expected[l+1],error("mixed coefficient table"));
 print("INDEX = ",l,"; BOTH_MIXED_COEFFICIENTS = ",expected[l+1])
);
if(Q[11]!=red(s^10),error("pure power q10"));
my(first=coef(Q[11],2,1)-coef(Q[11],1,2));
if(first!=-o*A^4*(t-u),error("first defect response"));
print("FIRST_NONZERO_RESPONSE = ",first);
\\ Verify the tensor residue representation on its entire9-element basis.
for(i=0,2,for(j=0,2,my(P=o*x^i*y^j);
 if(coef(red((y-x)*P),2,2)!=coef(P,2,1)-coef(P,1,2),error("residue functional encoding"))
));
my(D=t-u);
my(L2(P)=-A^2*coef(P,1,0)+A^2*coef(P,0,1)+A*B*coef(P,2,0)-A*B*coef(P,0,2)+A*D*coef(P,2,1)-B*D*coef(P,2,2));
my(L3(P)=A^2*B*coef(P,1,0)-A^2*B*coef(P,0,1)-A*B^2*coef(P,2,0)+A*B^2*coef(P,0,2)+A^2*D*coef(P,1,1)-B^2*D*coef(P,2,2));
for(l=0,6,if(L2(Q[l+1])!=0||L3(Q[l+1])!=0,error("H9 functional basis")));
my(F=A^3*(t+u)-A^2*B^2+B^3,pivot=L2(Q[8])*L3(Q[9])-L3(Q[8])*L2(Q[9]));
if(pivot!=o*A*D^2*F*(F+A^6),error("factorized rank chart"));
print("RANK_CHART_IDENTITY = A*(t-u)^2*F*(F+A^6), F=A^3*(t+u)-A^2*B^2+B^3");
print("ORIGINAL_SOURCE_IDENTITIES = 11; RESIDUE_BASIS_IDENTITIES = 9");
print("CUBIC_DEFECT_IDENTITIES_COMPLETED")
}
quit;

\\ Exact source control: jets of <1,T,f,T*f>, f^2=(1+a*T)(1+b*T).
\\ One 4-dimensional symbolic calculation, not a dimension series.
\\ Compare binomial convolution with the defining square recursion.
\\ Test the proposed collision-only factorization by its residual quadratic.
default(parisizemax, 64000000);
default(nbthreads, 1);
if(default(nbthreads)!=1,error("thread setting failed"));
{
my(a='a,b='b,c=vector(4,j,sum(k=0,j-1,binomial(1/2,k)*a^k*binomial(1/2,j-1-k)*b^(j-1-k))));
my(rec=vector(4,j,0),square=[1,a+b,a*b,0]);
rec[1]=1;
for(j=1,3,rec[j+1]=(square[j+1]-sum(k=1,j-1,rec[k+1]*rec[j-k+1]))/2);
if(c!=rec,error("independent square recursion failed"));
my(J=matrix(4,4,i,j,if(j==1,if(i==1,1,0),if(j==2,if(i==2,1,0),if(j==3,c[i],if(i==1,0,c[i-1]))))));
my(delta=matdet(J),expected=-(a-b)^2*(a^2+6*a*b+b^2)/64);
if(delta!=expected,error("full jet determinant identity failed"));
my(q=b^2+6*b+1);
if(poldisc(q,b)!=32,error("quadratic discriminant failed"));
if(subst(q,b,0)!=1 || subst(q,b,1)!=8 || subst(q,b,-1)!=-4,error("boundary values failed"));
my(F=ffgen(Mod(1,3)*('v^2+1),'u),J3=matrix(4,4,i,j,subst(subst(J[i,j],a,1),b,F)));
if(matrank(J3)!=3 || matdet(J3)!=0,error("ternary off-collision control failed"));
if(F==0 || F==1 || F==-1,error("invalid ternary slopes"));
my(bad=J);bad[4,3]+=1;
if(matdet(bad)==expected,error("mutated coefficient escaped determinant comparison"));
print("f coefficients through T^3: ",c);
print("det J = ",delta);
print("nonconstant factors = ",factor(delta));
print("residual q(b)=b^2+6b+1; discriminant=32; q(0)=1; q(1)=8; q(-1)=-4");
print("F9 control: a=1,b=u,u^2+1=0; full jet rank=3; determinant=0; separated nonzero slopes");
print("independent square recursion agrees; mutated jet coefficient fails the determinant identity");
print("PASS");
}

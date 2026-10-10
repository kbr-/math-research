\\ Test a general mechanism, not a dimension grid: does the formal secant determinant
\\ remain unchanged under ti=zi^3+B*zi? N4 symbolic identity says yes; test N5 once.
\\ Original matrix10 square; beta-degree <=sum floor(j/3)=12, exact GF27 polynomials.
default(parisize,128000000);
B='B;x='x;T=varhigher("T");
{
my(field=Mod(1,3)*(x^3-x+1),g=ffgen(field,'g),o=g^0,z=[0*o,o,g,g^2,g+o],N=5,r=10,a=3,rows=List(),oldrows=List());
if(!polisirreducible(field)||#Set(z)!=N,error("Invalid original roots"));
for(i=1,N,for(j=i+1,N,
 my(ti=z[i]^3+B*z[i],tj=z[j]^3+B*z[j],H=1/sqrt((o+ti*T)*(o+tj*T)+O(T^(a+1))),
 u=vector(a+1,k,polcoef(H,k-1,T)),out=vector(r));
 for(k=0,r-1,
  my(m=k\3,num,qr);
  if(k%3==0,out[k+1]=u[m+1],
   if(k%3==1,num=z[i]*(u[m+2]+tj*u[m+1])-z[j]*(u[m+2]+ti*u[m+1]),
    num=-z[i]^2*(u[m+2]+tj*u[m+1])+z[j]^2*(u[m+2]+ti*u[m+1]));
   qr=divrem(num,ti-tj,B);if(qr[2]!=0,error("Secant quotient not polynomial"));out[k+1]=qr[1]
  );
 );
 listput(rows,out);
 my(S=sqrt((o+z[i]*T)*(o+z[j]*T)+O(T^(r+2))),delta=(z[i]-z[j])^2);
 listput(oldrows,vector(r,k,polcoef(S,k+1,T)/delta));
));
my(D=matdet(matrix(r,r,i,j,rows[i][j])),D0=matdet(matrix(r,r,i,j,oldrows[i][j])));
if(subst(D,B,0)!=D0,error("Original source control"));
if(poldegree(D,B)>12,error("Degree budget"));
print("SHEAR_POINT field=",field," roots=",z," original_det=",D0," beta_degree=",poldegree(D,B));
print("SHEAR_DETERMINANT=",D);
print("SHEAR_INVARIANCE=",D==D0);
print("SECANT_SHEAR_TEST_COMPLETED");
}
quit;

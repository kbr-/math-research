\\ Test the proposed all-q fixed-mark certificate a_b=b+t*b^2, b in Fq,
\\ q=3^e>=9, on its smallest nonvacuous q=9. Work over F9(t), not sampled t.
\\ Original degree-two pair prefix: R=36, full root-space dimension D=38.
\\ Stages: construct all 36 rows from Motzkin recurrence; independently verify
\\ all 1296 entries by the original square-root recursion; check the deficient
\\ t=0 control; compute the exact symbolic determinant (degree at most 630).
\\ No larger q or parameter sweep. Zero at this mark does not settle a moving mark.
default(parisizemax,2000000000);
default(parisize,128000000);
t='t;
{
my(ffpoly=ffinit(3,2,'b),b=ffgen(ffpoly,'b),one=b^0,base=vector(9,i,((i-1)%3)*one+((i-1)\3)*b),a=vector(9,i,base[i]+t*base[i]^2),R=36,M=matrix(R,R,i,j,0*one),row=0,checks=0);
for(i=1,9,if(base[i]^9!=base[i],error("subfield construction")));
for(i=1,9,for(j=i+1,9,
 if(a[i]==a[j],error("generic collision"));row++;
 my(s=a[i]+a[j],v=a[i]*a[j],delta=(a[i]-a[j])^2,Q=vector(R,k,0*one),G=vector(R+2,k,0*one));
 Q[1]=one;G[1]=one;G[2]=s/2;
 for(l=1,R-1,Q[l+1]=s*Q[l]+if(l>=2,delta*sum(h=0,l-2,Q[h+1]*Q[l-1-h]),0*one));
 for(l=2,R+1,G[l+1]=(if(l==2,v,0*one)-sum(h=1,l-1,G[h+1]*G[l-h+1]))/2);
 for(l=0,R-1,if(G[l+3]!=delta*Q[l+1],error("original-source mismatch"));checks++;M[row,l+1]=Q[l+1]);
));
print("FIELD = F9(t), F9 generator ",b,"; defining polynomial ",ffpoly);
print("LABELS = ",a);print("SOURCE_IDENTITIES = ",checks);
my(M0=subst(M,t,0),rk0=matrank(M0));
if(M0[,10]!=M0[,2],error("finite-field q9=q1 control"));
print("CENTRAL_PAIR_RANK = ",rk0," OF ",R);
print("SYMBOLIC_MATRIX = ",M);
print("DETERMINANT_STARTED");
my(det=matdet(M));
print("DETERMINANT = ",det);
if(det!=0,
 print("DETERMINANT_DEGREE = ",poldegree(det,t));print("DETERMINANT_VALUATION = ",valuation(det,t)),
 print("FIXED_MARK_GENERIC_DETERMINANT_ZERO; moving-point question remains"));
print("QUADRATIC_FIELD_IMAGE_COMPLETED")
}
quit;

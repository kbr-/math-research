\\ Reuse the saved F9(t) matrix; do not rebuild its checked polynomial entries.
\\ Test whether moving the mark rescues the quadratic-image mechanism at q=9.
\\ One exact F81 specialization can prove nonvanishing of the family, but a
\\ failed specialization is not a generic refutation. Then retain the exact
\\ fixed-mark kernel to understand the failure already certified.
default(parisizemax,2000000000);
default(parisize,128000000);
t='t;b=ffgen(ffinit(3,2,'b),'b);
buildPair(a)={
 my(n=#a,R=n*(n-1)/2,o=a[1]^0,M=matrix(R,R,i,j,0*o),row=0,count=0);
 for(i=1,n,for(j=i+1,n,
  row++;my(s=a[i]+a[j],v=a[i]*a[j],delta=(a[i]-a[j])^2,Q=vector(R,k,0*o),G=vector(R+2,k,0*o));
  if(delta==0,error("label collision"));Q[1]=o;G[1]=o;G[2]=s/2;
  for(l=1,R-1,Q[l+1]=s*Q[l]+if(l>=2,delta*sum(h=0,l-2,Q[h+1]*Q[l-1-h]),0*o));
  for(l=2,R+1,G[l+1]=(if(l==2,v,0*o)-sum(h=1,l-1,G[h+1]*G[l-h+1]))/2);
  for(l=0,R-1,if(G[l+3]!=delta*Q[l+1],error("original root mismatch"));count++;M[row,l+1]=Q[l+1]);
 ));print("MOVING_SOURCE_IDENTITIES = ",count);return(M)
};
{
my(lines=readstr("research/results/bmd-effective-recursion-20261007/quadratic-fixed.txt"),M=0);
for(i=1,#lines,my(parts=strsplit(lines[i],"="));if(#parts>=2&&parts[1]=="SYMBOLIC_MATRIX ",M=eval(parts[2])));
if(type(M)!="t_MAT"||matsize(M)!=[36,36],error("saved matrix missing or wrong size"));
print("SAVED_MATRIX_LOADED 36 by 36 over F9(t)");
my(modulus=ffinit(3,4,'g),gen=ffgen(modulus,'g),theta=ffprimroot(gen),bb=theta^10,o=theta^0,base=vector(9,i,((i-1)%3)*o+((i-1)\3)*bb));
if(bb^9!=bb||bb^3==bb||theta^9==theta,error("field/subfield control"));
my(a=vector(9,i,base[i]+theta*base[i]^2),tau=0,chosen=0,startpow=if(getenv("MARK_START")!=""&&getenv("MARK_START")!=0,eval(getenv("MARK_START")),1));
for(j=startpow,startpow+8,my(candidate=theta^j);if(prod(i=1,9,1+a[i]*candidate)!=0,tau=candidate;chosen=j;break));
if(!chosen,error("no unramified control mark"));
my(alpha=vector(9,i,a[i]/(1+a[i]*tau)),A=buildPair(alpha));
print("F81_MODULUS = ",modulus,"; FIELD_GENERATOR = ",gen,"; THETA = ",theta,"; F9_GENERATOR = ",bb);
print("LABELS = ",a,"; MARK = ",tau," = THETA^",chosen);
print("TRANSPORTED_LABELS = ",alpha);
print("MOVING_MATRIX = ",A);
print("MOVING_PAIR_RANK = ",matrank(A)," OF 36; MOVING_DETERMINANT = ",matdet(A));
if(getenv("MOVING_ONLY")=="1",print("QUADRATIC_MOVING_ONLY_COMPLETED");return());
print("FIXED_KERNEL_STARTED");
my(K=matker(M));
if(M*K!=matrix(36,matsize(K)[2],i,j,0*b^0),error("fixed kernel reconstruction"));
print("FIXED_GENERIC_PAIR_RANK = ",36-matsize(K)[2]);
print("FIXED_GENERIC_KERNEL = ",K);
print("QUADRATIC_FOLLOWUP_COMPLETED")
}
quit;

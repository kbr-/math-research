\\ Test a permanent generic marked defect on the old two-triple path.
\\ Stages: exact common-cubic identity; one bounded list of valid smooth marks;
\\ original-root vs pair entries; first full-rank witness; Singular export.
\\ Size15 pair matrix, original size17. At most8 candidates, stop on success.
default(parisizemax,500000000);
default(parisize,64000000);
z='z;e='e;v='v;
{
my(o=Mod(1,3),D=v^2-1,A=D*e^2,B=D^2*e^4-e^2,F=o*(z^3+A*z^2+B*z));
my(a=[0,e+D*e^2,-e+D*e^2,1,1+v*e+D*e^2,1-v*e+D*e^2]*o);
if(prod(i=1,3,z-a[i])!=F,error("first fibre identity"));
if(prod(i=4,6,z-a[i])!=F-subst(F,z,1),error("second fibre identity"));
print("COMMON_CUBIC_IDENTITIES_PASSED; F = ",F);
my(ffpoly=ffinit(3,4,'g),g=ffgen(ffpoly,'g),one=g^0,ep=g,vv=g+one,DD=vv^2-one,labels=[0,ep+DD*ep^2,-ep+DD*ep^2,1,1+vv*ep+DD*ep^2,1-vv*ep+DD*ep^2]*one,success=0);
print("FIELD_POLYNOMIAL = ",ffpoly);print("EPSILON = ",ep,"; V = ",vv,"; LABELS = ",labels);
if(#Set(labels)!=6,error("candidate labels collide"));
for(attempt=1,8,
 my(tau=g^(attempt+1),den=vector(6,i,one+labels[i]*tau));
 if(vecprod(den)==0,print("RAMIFIED_MARK_SKIPPED = ",tau);next);
 my(al=vector(6,i,labels[i]/den[i]),M=matrix(15,15,i,j,0*one),row=0,checks=0);
 for(i=1,6,for(j=i+1,6,row++;
  my(s=al[i]+al[j],vvv=al[i]*al[j],delta=(al[i]-al[j])^2,Q=vector(15,k,0*one),G=vector(17,k,0*one));
  Q[1]=one;G[1]=one;G[2]=s/2;
  for(l=1,14,Q[l+1]=s*Q[l]+if(l>=2,delta*sum(h=0,l-2,Q[h+1]*Q[l-1-h]),0*one));
  for(l=2,16,G[l+1]=(if(l==2,vvv,0*one)-sum(h=1,l-1,G[h+1]*G[l-h+1]))/2);
  for(l=0,14,if(G[l+3]!=delta*Q[l+1],error("original source mismatch"));checks++;M[row,l+1]=Q[l+1])
 ));
 my(det=matdet(M)); print("MARK = ",tau,"; CHECKS = ",checks,"; PAIR_RANK = ",matrank(M),"; DET = ",det);
 if(det!=0,
  success=1;print("WITNESS_MATRIX = ",M);print("TRANSPORTED_LABELS = ",al);
  my(path="research/results/bmd-cubic-fibre-coupling-20261009/check.sing");
  write(path,"ring r=(3,g),(x),dp;");write(path,Str("minpoly=",lift(ffpoly),";"));
  write(path,"matrix M[15][15];");
  for(i=1,15,for(j=1,15,write(path,Str("M[",i,",",j,"]=",M[i,j],";"))));
  write(path,Str("number expected=",det,";"));
  write(path,"poly actual=det(M); actual; if(actual!=expected || actual==0){ ERROR(\"determinant mismatch\"); } else { print(\"INDEPENDENT_DETERMINANT_PASSED\"); } quit;");
  break
 )
);
if(!success,error("no witness in bounded candidates; no generic conclusion"));
print("CUBIC_FIBRE_WITNESS_COMPLETED")
}
quit;

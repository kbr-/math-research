\\ Exact encoding controls for the coface residue split and generic pivot.
\\ Exhaust all ordered distinct nonzero labels in GF(9) for m=1,2.
\\ Check one fixed GF(3^10) instance for m=3..6, including the first support gap.
\\ Compare every available coefficient, original/pivoted ranks, and Schur determinant.
\\ This validates a proved encoding; it is not a new normality-range survey.
default(parisizemax,1000000000);
cantor(j)={my(v=0,p=1);while(j, v+=(j%2)*p;j=j\2;p*=3);v;}
support(j)=3*cantor(j\3)+(j%3);
verify(labels)={
  my(m=#labels,D=3+2*m+m*(m-1)/2,L=(D+2)\3,o=labels[1]^0,zero=0*o);
  if(#Set(labels)!=m || setsearch(Set(labels),zero),error("labels must be distinct nonzero"));
  my(w=vector(m,i,sqrt(o+labels[i]*T+O(T^(D+3)))));
  my(u=vector(m,i,1/sqrt(o+labels[i]^3*X+O(X^(L+2)))));
  my(rows=List([o,T*o,T^2*o]),parts=List([[o,zero,zero],[zero,o,zero],[zero,zero,o]]));
  for(i=1,m,
    listput(rows,w[i]^3);listput(parts,[1/u[i],zero,zero]));
  for(i=1,m,
    listput(rows,T*w[i]);listput(parts,[labels[i]^2*X*u[i],u[i],-labels[i]*u[i]]));
  for(i=1,m,for(j=i+1,m,
    my(s=labels[i]+labels[j],v=labels[i]*labels[j],delta=s^2-v,h=u[i]*u[j]);
    listput(rows,w[i]*w[j]);
    listput(parts,[(1-s*v*X)*h,(-s+v^2*X)*h,delta*h])));
  if(#rows!=D,error("source dimension"));
  my(M=matrix(D,D,i,j,polcoeff(rows[i],j-1,T)));
  for(i=1,D,for(k=0,D-1,
    if(M[i,k+1]!=polcoeff(parts[i][k%3+1],k\3,X),error("residue reconstruction"))));
  my(original=List([o,T*o,T^2*o]));
  for(i=1,m,listput(original,w[i]);listput(original,T*w[i]));
  for(i=1,m,for(j=i+1,m,listput(original,w[i]*w[j])));
  my(O=matrix(D,D,i,j,polcoeff(original[i],j-1,T)));
  if(matrank(O)!=matrank(M),error("row change rank"));
  my(piv=concat([1,2,3],vector(m,j,3*support(j)+1)),rest=List());
  if(vecmax(piv)>D,error("pivot outside jet"));
  for(j=1,D,if(!setsearch(Set(piv),j),listput(rest,j)));
  rest=Vec(rest);
  my(first=vector(m+3,j,j),last=vector(D-m-3,j,j+m+3));
  my(A=vecextract(M,first,piv),B=vecextract(M,first,rest),C=vecextract(M,last,piv),E=vecextract(M,last,rest),da=matdet(A));
  if(!da,error("chosen control has singular generic pivot"));
  my(S=E-C*A^-1*B,permuted=vecextract(M,"..",concat(piv,rest)));
  if(matdet(permuted)!=da*matdet(S),error("Schur determinant"));
  if(matrank(M)!=m+3+matrank(S),error("Schur rank"));
  [D,apply(x->x-1,piv),matrank(S),da];
}
{
my(g=ffgen(3^2,'a),count=0,els=vector(8,i,(i%3)+(i\3)*g));
for(i=1,8,verify([els[i]]);count++);
for(i=1,8,for(j=1,8,if(i!=j,verify([els[i],els[j]]);count++)));
print("Exhaustive GF(9) ordered distinct nonzero controls m=1,2: ",count," passed.");
my(h=ffgen(3^10,'b));
for(m=3,6,print("m=",m," labels=",vector(m,j,h^j)," result[D,pivot orders,residual rank,pivot determinant]=",verify(vector(m,j,h^j))));
print("PASS: every retained coefficient, row-change rank, pivot range, Schur determinant and rank.");
}
quit;

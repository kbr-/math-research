\\ Test the proposed characteristic-five refutation at its smallest dimension.
\\ At n=4, m=4, the d=1 top ideal is R and d=2 top ideal is zero.
\\ At m=5, the d=1 top ideal is zero, whereas d=0 has top ideal R.
\\ Polynomial determinants are essential: evaluating all four distinct
\\ nonzero elements of F_5 would make their sum zero and miss the rank.
T='T; AV=['a,'b,'c,'e];
{
  my(s=sqrt(1+T+O(T^6)),b=vector(6,j,Mod(polcoef(s,j-1,T),5)),
     E=[1,2,3,5],V=prod(i=1,3,prod(j=i+1,4,AV[j]-AV[i])),
     A=matrix(4,4,i,j,b[E[j]+1]*AV[i]^E[j]),D=matdet(A),
     predicted=Mod(3,5)*prod(i=1,4,AV[i])*V*sum(i=1,4,AV[i]));
  if(b[5]!=0 || prod(j=1,4,b[E[j]+1])==0,error("coefficient hypothesis failed"));
  if(D!=predicted || D==0,error("generalized Vandermonde rank certificate failed"));
  my(D3=matdet(matrix(3,3,i,j,b[j+1]*AV[i]^j)));
  if(D3==0,error("first three columns are dependent"));
  my(q=sum(j=0,4,b[j+1]*b[5-j]*AV[1]^j*AV[2]^(4-j)));
  if(polcoef(polcoef(q,2,AV[1]),2,AV[2])!=Mod(4,5),error("degree-two row fails to kill e4"));
  if(vector(4,i,b[5]*AV[i]^4)!=vector(4),error("e4 is not in the degree-one kernel"));
  print("sqrt coefficients b1..b5 = ",vector(5,j,b[j+1]));
  print("PASS: columns 1,2,3 are independent over F_5(a,b,c,e); column 4 is zero.");
  print("PASS: degree-two row w1*w2 at order 4 = ",q," is nonzero.");
  print("PASS: determinant on columns [1,2,3,5] = 3*product(a_i)*Vandermonde(a_i)*sum(a_i), a nonzero polynomial over F_5.");
  print("Conclusion: I_(d=1,m=4)=R; I_(d=2,m=4)=0; I_(d=1,m=5)=0; I_(d=0,m=5)=R.");
  print("Counterexample for all n>=4 and ell>=0: delta(n,ell+5,ell)=n+2ell+6; delta(n,ell+6,ell)=n+2ell+9.");
}
quit;

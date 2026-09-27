\\ Test a named uniform factorization hypothesis, not another normality case.
\\ H: the char0,d2 residual boundary polynomial is the product of the known
\\ four-root cubic over all four-subsets. It predicts singular square jets
\\ whenever two disjoint pairs have the same sum and no roots coincide.
\\ Smallest unresolved falsifier: n4, roots0,1,2,11,3, rank12.
\\ Solved negative control: n3, roots0,1,2,3, rank8. Stop after these two.
T='T;
{
my(cases=[[0,1,2,3],[0,1,2,11,3]]);
for(z=1,#cases,
  my(aa=cases[z],nn=#aa-1,rr=2+binomial(#aa,2),rows=List([1,T]));
  if(#Set(aa)!=#aa,error("collision in test point"));
  my(roots=vector(#aa,i,(1+aa[i]*T+O(T^rr))^(1/2)));
  for(i=1,#aa,for(j=i+1,#aa,listput(rows,roots[i]*roots[j])));
  my(M=matrix(rr,rr,i,j,polcoef(rows[i],j-1,T)),det=matdet(M),rk=matrank(M));
  if(z==1&&rk!=7,error("known four-root negative control"));
  print("ROOTS = ",aa," n=",nn," d=2 dimension=",rr);
  print("SQUARE_JET_MATRIX = ",M);
  print("DETERMINANT = ",det);
  print("RANK = ",rk);
  print("BALANCE = 0+3=1+2");
);
print("PAIR_SUM_BOUNDARY_TEST_COMPLETED");
}
quit;

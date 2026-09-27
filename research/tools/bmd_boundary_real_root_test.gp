\\ Uniform hypothesis tested: for each N and real separated old roots with
\\ nonzero lower boundary, the noncollision degree-two boundary polynomial
\\ in the final root has only simple real zeros. One N5 falsifier; no size series.
\\ Pair h_j columns follow the exact Schur hull. Polynomial determinant and
\\ Sturm count use PARI kernels. Raw degree<=24, expected quotient degree12.
N=5; r=N*(N-1)/2;
aa=[0,1,2,4,x];
ga=vector(r,j,binomial(-3/2,j-1));
pairs=List();
for(i=1,N,for(j=i+1,N,listput(pairs,[i,j])));
MM=matrix(r,r,i,j,sum(a=0,j-1,ga[a+1]*ga[j-a]*aa[pairs[i][1]]^a*aa[pairs[i][2]]^(j-1-a)));
vv=prod(i=1,N-1,prod(j=i+1,N,aa[j]-aa[i]));
dd=matdet(MM);
dv=divrem(dd,vv^(N-2));
if(dv[2]!=0,error("Schur quotient is not polynomial"));
ff=dv[1]; ff=ff/pollead(ff);
if(poldegree(ff)!=12,error("unexpected quotient degree"));
gg=gcd(ff,deriv(ff));
print("roots=",aa);
print("matrix_rows=",r,"; raw_degree=",poldegree(dd),"; boundary_degree=",poldegree(ff));
print("monic_boundary=",ff);
print("squarefree_gcd=",gg);
print("real_root_count=",polsturm(ff));
print("real_rooted_hypothesis=",if(polsturm(ff)==poldegree(ff)&&poldegree(gg)==0,"PASSED_FIXED_CONTROL","FALSIFIED"));
quit;

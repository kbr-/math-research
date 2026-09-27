\\ One calibration of a uniform coalescence face: M=3 small roots and two large.
\\ R=binom(M,2); internal leading columns0..R-1, cross jets0..M-1.
\\ Required question: is the remaining binary face squarefree away from0,1?
M=3; R=M*(M-1)/2; sz=2*M+1;
ga=vector(R+2*M+1,j,binomial(-3/2,j-1));
hh(j)=sum(a=0,j,ga[a+1]*ga[j-a+1]*x^a);
H=matrix(sz,sz,i,j,if(i<=M,ga[i]*ga[R+j-i+1],if(i<=2*M,ga[i-M]*ga[R+j-i+M+1]*x^(R+j-i+M),hh(R+j-1))));
dt=matdet(H);
dv=divrem(dt,x^(M^2)*(x-1)^M);
if(dv[2]!=0,error("face Schur quotient not polynomial"));
ff=dv[1]/pollead(dv[1]);
print("M=",M,"; matrix_rows=",sz,"; quotient_degree=",poldegree(ff));
print("binary_face=",factor(ff));
while(subst(ff,x,0)==0,ff=ff/x);
while(subst(ff,x,1)==0,ff=ff/(x-1));
gg=gcd(ff,deriv(ff));
print("noncollision_face=",ff);
print("noncollision_degree=",poldegree(ff),"; repeated_degree=",poldegree(gg));
print("noncollision_face_simple=",if(poldegree(gg)==0,"PASSED_FIXED_CONTROL","FALSIFIED"));
quit;

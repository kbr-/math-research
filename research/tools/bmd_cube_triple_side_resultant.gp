\\ Symbolic multiple-root obstruction for the triple-side polynomial.
\\ F_n(t)=H(t,t^n)/t, integer n >=2, char 0. At a nonzero repeated root,
\\ H=0 and t*H_t+n*z*H_z=0. Compute their resultant in z with n symbolic.
\\ The Sylvester matrix is only 6 by 6, regardless of n; no degree sweep.
\\ Usage: gp -q research/tools/bmd_cube_triple_side_resultant.gp
z='z; t='t; n='n;
A=n*(2*n-1); B=4*n^2-1; C=n*(2*n+1);
q=A-B*t+C*t^2; qs=C-B*t+A*t^2;
H=t*z^3-qs*z^2-q*z+t;
J=t*deriv(H,t)+n*z*deriv(H,z);
R=polresultant(H,J,z);
want=n^5*(n^2-1)*(4*n^2-1)^2*t^2*(t-1)^8;
if(R!=want,error("symbolic resultant identity failed"));
u=(n+1)*qs-t*deriv(qs,t);
v=(2*n+1)*q-t*deriv(q,t);
w=-3*n*t;
K=u*z^2+v*z+w;
if(K!=J-(3*n+1)*H,error("quadratic remainder failed"));
S=[t,-qs,-q,t,0;0,t,-qs,-q,t;u,v,w,0,0;0,u,v,w,0;0,0,u,v,w];
if(t*matdet(S)!=want,error("Sylvester determinant identity failed"));
print("Symbolic identities in Q[n,t]:");
print("Res_z(H,J) = n^5*(n^2-1)*(4*n^2-1)^2*t^2*(t-1)^8");
print("K=J-(3*n+1)*H and t*det(Sylvester(H,K))=Res_z(H,J): PASS");
exps=[0,3*n,n-1,n,n+1,2*n-1,2*n,2*n+1];
coeffs=[1,1,-A,B,-C,-C,B,-A];
{
  for(j=0,6,
    my(moment=sum(i=1,8,coeffs[i]*prod(r=0,j-1,exps[i]-r)));
    if(j<6,if(moment!=0,error("lower derivative does not vanish")),
      if(moment!=4*n^2*(n^2-1)*(4*n^2-1),error("sixth derivative failed")));
    print("F_n^(",j,")(1)=",moment);
  );
}
\\ A sign error in the middle coefficient must fail the asserted identity.
badH=H+2*B*t*z;
badJ=t*deriv(badH,t)+n*z*deriv(badH,z);
if(polresultant(badH,badJ,z)==want,error("negative control did not distinguish the sign error"));
print("Negative control (flip the t^n coefficient): distinguished");
quit;

\\ Double-side repeated-root equations, symbolic in the exponent M.
\\ At t not 0,+-1, set u=t^M, v=((t-1)/(t+1))^M.
\\ P=t*W_M(t)/(t+1)^M. Repeated roots require P=DP=0,
\\ D=t(t^2-1)d_t+M*u*(t^2-1)d_u+2*M*t*v*d_v.
\\ This fixed-size elimination tests whether treating u,v independently
\\ excludes nonspecial roots, rather than checking additional degrees.
v='v; u='u; t='t; M='M;
A=M*u*(1+t^2); B=t*(u-1)^2;
P=(A-B)*v-(A+B);
DP=t*(t^2-1)*deriv(P,t)+M*u*(t^2-1)*deriv(P,u)+2*M*t*v*deriv(P,v);
Q1=M*u*(1+t^2)-(u-1)*(u*t^2-1);
Q2=M*u*(1+t^2)-(u-1)*(t^2-u);
R=polresultant(P,DP,v);
if(R!=2*M*t*Q1*Q2,error("double-side resultant identity failed"));
print("Res_v(P,DP)=2*M*t*Q1*Q2: PASS");
print("Q1=",Q1);
print("Q2=",Q2);
\\ Recover v on either component without dividing by u-1 or other
\\ potentially vanishing factors: verify the cleared identities modulo Qi.
V1=(t+1)*(t*u-1)/((t-1)*(t*u+1));
V2=-(t-1)*(u+t)/((t+1)*(u-t));
print("P at V1 modulo Q1=",numerator(subst(P,v,V1))%Q1);
print("P at V2 modulo Q2=",numerator(subst(P,v,V2))%Q2);
if(numerator(subst(P,v,V1))%Q1!=0,error("first recovery failed"));
if(numerator(subst(P,v,V2))%Q2!=0,error("second recovery failed"));
\\ At t=2 the relaxed system has genuine solutions for every M>=12:
\\ choose a root u of 4u^2-5(M+1)u+1=0, then v=3(2u-1)/(2u+1).
q1at2=subst(Q1,t,2);
if(q1at2!=-(4*u^2-5*(M+1)*u+1),error("relaxed component failed"));
print("At t=2, Q1=0 is 4*u^2-5*(M+1)*u+1=0; nonspecial relaxed solutions remain.");
\\ Test a proposed sufficient arithmetic mechanism at the first two
\\ non-prime-power exponents M+/-1 occurring for M=8d-4: L=21,35.
\\ No Wronskian degree sweep: irreducibility of this residual Chebyshev
\\ polynomial would exclude a common factor with a lower-degree companion.
{
  my(x='x,y='y,a=1,b=x,c,L,R);
  for(j=2,35,
    c=2*x*b-a; a=b; b=c;
    if(j==21 || j==35,
      L=j; R=(b-(-1)^((L-1)/2)*L*x)/x^3;
      R=substpol(R,x^2,y);
      print("L=",L," residual Chebyshev degree=",poldegree(R),
            "; irreducible factor degrees=",apply(f->poldegree(f),factor(R)[,1]~));
    );
  );
}
quit;

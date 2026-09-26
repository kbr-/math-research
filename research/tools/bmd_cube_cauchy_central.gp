/* Symbolic central-annulus expansion of the actual Cauchy obstruction.
   q=x^4, p=u*x, N=4m, m odd. Q=u^N is kept independent during expansion.
   All theta coefficients are exact; N remains the polynomial variable n.
   Tests which leading terms cancel before interpreting a candidate edge. */
default(parisizemax,2000000000);
prec=5;
th(z)={my(v=1-z+O(x^prec));for(k=1,2,v*=(1-x^(4*k)*z)*(1-x^(4*k)/z));v;};
ld(z)={my(v=-z/(1-z)+O(x^prec));for(k=1,2,v+=-x^(4*k)*z/(1-x^(4*k)*z)+x^(4*k)/z/(1-x^(4*k)/z));v;};
{
  my(tp=-prod(k=1,2,(1-x^(4*k))^2)+O(x^prec),
     Ap=exp(n*log(th(u*x))),Am=exp(n*log(th(-u*x))),
     Bp=exp(n*log(th(x/u))),Bm=exp(n*log(th(-x/u))),
     Kr=tp*th(Q*x^2)/(th(Q)*th(x^2)),
     Km=tp*th(-Q*x^2)/(th(Q)*th(-x^2)),
     K1=tp*th(-Q)/(th(Q)*th(-1)),phi);
  print("SCOPE exact central annulus q=x^4, p=u*x, N=n=4m; Q=u^n remains independent");
  phi=-2+4*ld(Q)-2*n*ld(u^2*x^2)
    +K1*(Ap/Am+Am/Ap+Bp/Bm+Bm/Bp)
    -Q*(Kr*(Bp/Ap+Bm/Am)+Km*(Bm/Ap+Bp/Am))
    -(Kr*(Ap/Bp+Am/Bm)+Km*(Am/Bp+Ap/Bm));
  for(j=0,4,print("COEFFICIENT x^",j," = ",factor(polcoef(phi,j))));
  my(t=u^4,m=n/4,aa=m*(2*m-1),bb=4*m^2-1,cc=m*(2*m+1),
     H=t*Q^3-(cc-bb*t+aa*t^2)*Q^2-(aa-bb*t+cc*t^2)*Q+t);
  for(j=0,3,if(polcoef(phi,j)!=0,error("central coefficient failed to cancel")));
  if(polcoef(phi,4)!=-4*(n^2-1)*H/(Q*(Q-1)*t),error("central cubic identity failed"));
  print("PASS central leading coefficient = -4*(n^2-1)*H(t,Q)/(Q*(Q-1)*t), t=u^4");
}
{
  my(t=I+x,nn=exp(n*log(1+x/I+O(x^7))),
     minus=exp(n*log(1+x/(I-1)+O(x^7))),
     plus=exp(n*log(1+x/(I+1)+O(x^7))),W);
  W=n*nn/t*(1+t^2)*(minus-plus)-(nn-1)^2*(minus+plus);
  print("SCOPE normalized Taylor series W_n(i+x)/(i+1)^n for n divisible by four");
  for(j=0,6,print("W_COEFFICIENT x^",j," = ",factor(polcoef(W,j))));
  print("EXACT_W_SIXTH_COEFFICIENT=",polcoef(W,6));
  for(j=0,5,if(polcoef(W,j)!=0,error("special W coefficient failed to cancel")));
  if(polcoef(W,6)!=-n^2*(n^2-1)*(n^2-4)/90,error("sixth W coefficient incorrect"));
  print("PASS both special roots have order exactly six for n divisible by four, n>=4");
}
{
  my(a=(1-u*x+O(x^3))^1,aa=(1+u*x+O(x^3))^1,
     b=(1-v*x+O(x^3))^1,bb=(1+v*x+O(x^3))^1,
     Ap=exp(n*log(a)),Am=exp(n*log(aa)),Bp=exp(n*log(b)),Bm=exp(n*log(bb)),
     kr=(1+(2-Q-1/Q)*u*v*x^2)/(Q-1),
     km=(1-(2-Q-1/Q)*u*v*x^2)/(Q-1),cross);
  cross=-Q*(kr*(Bp/Ap+Bm/Am)-km*(Bm/Ap+Bp/Am));
  if(polcoef(cross,0)!=0 || polcoef(cross,1)!=0,error("even annulus cancellation failed"));
  if(polcoef(cross,2)/(u*v)!=4*((Q-1)^2+n^2*Q)/(Q-1),error("even annulus leading coefficient failed"));
  print("PASS even-annulus cross coefficient = 4*((Q-1)^2+n^2*Q)/(Q-1)");
  if(4+polcoef(cross,2)/(u*v)!=4*Q*(Q+n^2-1)/(Q-1),error("last annulus identity failed"));
  print("PASS last even annulus adds 4, giving 4*Q*(Q+n^2-1)/(Q-1)");
}
{
  my(C=p+1/p,BQ=2-Q-1/Q,
     leading=2*Q/(Q-1)*((n*C-BQ)/A-(n*C+BQ)/B),
     W=n*Q*C*(A-B)-(Q-1)^2*(A+B));
  if(leading!=-2*W/((Q-1)*A*B),error("outer W identity failed"));
  print("PASS outer coefficient = -2*W_n(p)/((p^n-1)*(1-p^2)^n)");
  if((24*m-24)+(24*m-48)+(16*m^2-48*m)+16*m+72!=16*m^2+16*m,error("root count failed"));
  print("PASS all constructed simple points plus 12*6 branch weights exhaust N*(N+4)");
}

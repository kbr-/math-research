/* Exact Puiseux audit of the uniform Tate proof at the smallest d=2.
   q=x^N, p=zeta*x^b, zeta in mu_N, 0<=b<=N/2. Inversion covers the
   other labels. All valuation regimes and tied leading terms occur here.
   Exact cyclotomic coefficients; no floating-point rank or theta values.
   This checks the formulas, not the all-degree conclusion (proved in record). */
must(ok,msg)=if(!ok,error(msg));
theta0(c,b,N,P)=(1-c*x^b)*(1-c*x^(N+b))*(1-c^(-1)*x^(N-b))+O(x^P);
leading(f,v,c,msg)={must(valuation(f,x)==v,Str(msg," valuation"));must(polcoef(f,v)==c,Str(msg," coefficient"));};
{
  my(m=3,N=12,P=13,zeta=Mod(y,polcyclo(12,y)),cases=0,controls=0,skip=0);
  print("SCOPE d=2,m=3,N=12; 84 labels with 0<=b<=6; exact Q(zeta_12)((x)), q=x^12");
  print("One theta product factor beyond (1-z) suffices through x^12: omitted factors start at x^18 or later.");
  for(b=0,2*m,for(a=0,N-1,
    my(z=zeta^a,s=(-1)^(b+1),A,B,Am,Bm,Sp,Sm,vp,vm,cp,cm);
    if((b==0 || b==2*m) && z^2==1,skip++;next);
    A=theta0(z,b,N,P);B=theta0(1/z,2*m-b,N,P);
    Am=theta0(-z,b,N,P);Bm=theta0(-1/z,2*m-b,N,P);
    Sp=A^N+s*Am^N-x^(N*(b-m)/2)*(B^N+s*Bm^N);
    Sm=A^(-N)+s*Am^(-N)-x^(N*(m-b)/2)*(B^(-N)+s*Bm^(-N));
    if(b%m==0 && z^4==1,
      must(truncate(Sp)==0 && truncate(Sm)==0,"excluded E[4] control failed");
      controls++;print("EXCLUDED_E4 a=",a," b=",b," both sums vanish to computed precision");next);
    if(b==0,
      vp=N*(1-m)/2;cp=2*N*(z+1/z);vm=0;cm=(1-z)^(-N)-(1+z)^(-N),
    if(b==2*m,
      vp=N/2;cp=-2*N*(z+1/z);vm=-N*m/2;cm=-((1-1/z)^(-N)-(1+1/z)^(-N)),
    if(b%2,
      if(b<m,vp=N*(b-m)/2;cp=-2;vm=0;cm=2,
      if(b>m,vp=0;cp=2;vm=N*(m-b)/2;cm=-2,
        vp=N/2;vm=N/2;cp=N*(N-1)*(z^2-z^(-2));cm=N*(N+1)*(z^2-z^(-2)))),
      if(b<m,vp=N*(b-m)/2+N/2-b;cp=2*N/z;vm=b;cm=2*N*z,
        vp=b;cp=-2*N*z;vm=N*(m-b)/2+N/2-b;cm=-2*N/z)
    )));
    must(cp!=0 && cm!=0,"predicted coefficient vanishes on an allowed label");
    leading(Sp,vp,cp,"positive sum");leading(Sm,vm,cm,"reciprocal sum");
    print("LABEL a=",a," b=",b," Splus valuation=",vp," coefficient=",cp,
          " Sminus valuation=",vm," coefficient=",cm);
    cases++;
  ));
  must(cases==72 && controls==8 && skip==4,"label inventory mismatch");
  print("PASS 72 allowed representatives (covering all 128 non-E[4] N-torsion points by inversion), 8 excluded-E[4] controls, 4 E[2] pole cases skipped");
  must((b-m)/2+1/2-b/(2*m)==(m-1)*(b-m)/(2*m),"positive valuation comparison");
  must((m-b)/2+1/2-b/(2*m)==(m+1)*(m-b)/(2*m),"reciprocal valuation comparison");
}

\\ Finite-field reference: Mumford arithmetic and Frobenius pullback for y^2=f(x).
\\ Uses PARI's compiled polynomial arithmetic, extended gcd and exact division.
hc_assert(c,s)={if(!c,print("FAIL: ",s);quit(1));};
hc_quot(a,b)={if(poldegree(b,x)==0,return(a/b));my(q=divrem(a,b));hc_assert(q[2]==0,"nonexact polynomial quotient");q[1];};
hc_monic(u)={u/pollead(u);};
hc_rem(v,u)={if(poldegree(u,x)==0,0*HC_ONE,lift(Mod(v,u)));};
hc_valid(D,f)={my(u=D[1],v=D[2]);hc_assert(u!=0 && pollead(u)==1,"nonmonic Mumford u");hc_assert(v==0 || poldegree(v,x)<poldegree(u,x),"Mumford v degree");hc_assert(hc_rem(v^2-f,u)==0,"Mumford divisibility");};
hc_setup(f,p)={HC_F=f;HC_P=p;HC_G=(poldegree(f,x)-1)/2;HC_ONE=pollead(f)^0;hc_assert(p>2 && isprime(p),"odd characteristic required");hc_assert(HC_G>=1 && 2*HC_G+1==poldegree(f,x),"odd hyperelliptic degree");hc_assert(poldegree(gcd(f,deriv(f,x)),x)==0,"singular curve");};
hc_zero()={[HC_ONE,0*HC_ONE];};
hc_red(D)={my(u=hc_monic(D[1]),v=hc_rem(D[2],u));hc_valid([u,v],HC_F);while(poldegree(u,x)>HC_G,my(w=hc_monic(hc_quot(HC_F-v^2,u)));v=hc_rem(-v,w);u=w);hc_valid([u,v],HC_F);[u,v];};
hc_xgcd(a,b)={if(a!=0 && poldegree(a,x)==0,return([1/a,0*HC_ONE,HC_ONE]));if(b==0,my(c=pollead(a));return([1/c,0*HC_ONE,a/c]));if(poldegree(b,x)==0,return([0*HC_ONE,1/b,HC_ONE]));my(d=gcdext(a,b),c=pollead(d[3]));d/c;};
hc_add(D,E)={
 if(poldegree(D[1],x)==0,return(E));if(poldegree(E[1],x)==0,return(D));
 my(u1=D[1],v1=D[2],u2=E[1],v2=E[2],a=hc_xgcd(u1,u2),b=hc_xgcd(a[3],v1+v2),d=b[3]);
 my(u=hc_quot(u1*u2,d^2),v=hc_quot(b[1]*a[1]*u1*v2+b[1]*a[2]*u2*v1+b[2]*(v1*v2+HC_F),d));
 hc_red([u,hc_rem(v,u)]);
};
hc_mul(D,n)={my(R=hc_zero(),T=D);if(n<0,T=[T[1],hc_rem(-T[2],T[1])];n=-n);while(n,if(n%2,R=hc_add(R,T));n=n\2;if(n,T=hc_add(T,T)));R;};
hc_coeff_fr(f)={sum(i=0,poldegree(f,x),polcoef(f,i,x)^HC_P*x^i);};
hc_fr(D)={[hc_coeff_fr(D[1]),if(D[2]==0,0*HC_ONE,hc_coeff_fr(D[2]))];};
hc_v(D)={
 my(ft=hc_coeff_fr(HC_F));hc_valid(D,ft);
 my(ub=hc_monic(gcd(D[1],ft)),un=hc_quot(D[1],ub),B=hc_zero(),N=hc_zero());
 if(poldegree(ub,x)>0,B=[hc_monic(gcd(HC_F,subst(ub,x,x^HC_P))),0*HC_ONE];hc_valid(B,HC_F));
 if(poldegree(un,x)>0,my(U=subst(un,x,x^HC_P));hc_assert(poldegree(gcd(U,HC_F),x)==0,"unremoved branch component");my(V);if(U==HC_ONE*x^poldegree(U,x),V=truncate(subst(D[2],x,x^HC_P)*(HC_F+O(x^poldegree(U,x)))^(-(HC_P-1)/2)),V=lift(Mod(subst(D[2],x,x^HC_P),U)*Mod(HC_F,U)^(-(HC_P-1)/2)));N=hc_red([U,V]));
 hc_add(B,N);
};
hc_derivn(f,n)={for(j=1,n,f=deriv(f,x));f;};
hc_connection(D)={
 hc_valid(D,HC_F);
 my(u=D[1],v=D[2],A=deriv(u,x)/(2*u),B=deriv(u,x)*v/(2*u),b=(HC_P-1)/2);
 hc_assert(A^HC_P+hc_derivn(A,HC_P-1)==0,"logarithmic rational connection control");
 my(beta=B^HC_P+hc_derivn(B*HC_F^b,HC_P-1),w=hc_quot(HC_F-v^2,u));
 my(Q=deriv(u,x)/2*sum(j=1,b,binomial(b,j)*u^(j-1)*v^(HC_P-2*j)*w^j));
 hc_assert(beta==hc_derivn(Q,HC_P-1),"polynomial curvature cancellation mismatch");
 my(H=matrix(HC_G,HC_G,i,j,polcoef(HC_F^b,HC_P*i-j,x)));
 hc_assert(poldegree(denominator(beta),x)==0,"curvature has a finite pole");
 hc_assert(beta==0 || poldegree(beta,x)<=HC_P*(HC_G-1),"curvature exceeds holomorphic degree");
 for(i=0,max(0,poldegree(beta,x)),if(i%HC_P,hc_assert(polcoef(beta,i,x)==0,"curvature not a Frobenius-variable polynomial")));
 [vector(HC_G,i,polcoef(beta,HC_P*(i-1),x)),H];
};

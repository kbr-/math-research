T='T; \\ Keep the series variable above the algebraic coefficient variable.
rr_assert(c,s)={if(!c,error(s));};
rr_sigma(c,A,aa)={subst(lift(c),aa,A);};
rr_setup(K)={
 my(modulus=3^K,aa='a,av=Mod(aa,Mod(1,modulus)*(aa^3-aa-1)),sa=av+1);
 for(i=1,K,sa-=(sa^3-sa-1)*(-sum(j=0,K-1,(3*sa^2)^j)));
 rr_assert(sa^3-sa-1==0,"Frobenius lift root");
 rr_assert(rr_sigma(rr_sigma(sa,sa,aa),sa,aa)==av,"Frobenius lift order3");
 [av,sa,aa,modulus];
};
rr_context(R,K,setup)={
 my(A=3^(K-1),q0=R^A,q1=sum(j=0,poldegree(q0,T),rr_sigma(polcoef(q0,j,T),setup[2],setup[3])*T^j),q2=sum(j=0,poldegree(q1,T),rr_sigma(polcoef(q1,j,T),setup[2],setup[3])*T^j));
 rr_assert(polcoef(R,0,T)==1,"normalized input");
 [R^((A-1)/2),[q0,q1,q2],floor(A*poldegree(R,T)/2)];
};
rr_step(H,Q,digit,bound)={
 my(P=H*Q);if(P==0,return(0));my(D=poldegree(P,T),next=sum(j=0,max(-1,floor((D-digit)/3)),polcoef(P,3*j+digit,T)*T^j));
 rr_assert(next==0 || poldegree(next,T)<=bound,"bounded coefficient state");
 next;
};
rr_coeff(ctx,N,twist=1)={
 my(H=ctx[1],j=0);
 while(N,H=rr_step(H,ctx[2][if(twist,j%3+1,1)],N%3,ctx[3]);N=N\3;j++);
 polcoef(H,0,T);
};

\\ Independent PARI extraction uses the generic coefficient routine, not shared-prefix code.
default(parisizemax,1000000000);
default(nbthreads,1);
read("research/tools/bmd_prime_power_coeff_core_20261008.gp");
read("research/results/bmd-exception-return-vectors-20261008/vector-check-input.gp");
{
my(start=getwalltime(),checks=0,degrees=[3,6,9,24,27,78,81]);
for(ii=1,#VECTOR_CHECK_CASES,
 my(row=VECTOR_CHECK_CASES[ii],mask=row[1],g=row[2],coefficients=row[3],expected=row[4],contexts=vector(5),setups=vector(5));
 for(j=1,#degrees,
  my(m=degrees[j],v=valuation(m,3),K=v+1,divisor=3^v,unit=m/divisor);
  if(contexts[K]==0,
   my(setup=rr_setup(K),av=setup[1],one=av^0,R=prod(i=0,8,if(bittest(mask,i),one+av^i*T,one)));
   setups[K]=setup;contexts[K]=rr_context(R,K,setup)
  );
  my(setup=setups[K],A=matrix(g,2*g,ell,h,rr_coeff(contexts[K],m*3^(4+3*(h-1))-ell)));
  for(k=1,27,if(VECTOR_CHECK_ORDERS[k]>=m,
   for(ell=1,g,
    my(raw=sum(h=1,2*g,(coefficients[k][h]-(h==1))*A[ell,h]),vals=vector(3,t,lift(polcoef(lift(raw),t-1,setup[3]))),res,code);
    rr_assert(vector(3,t,vals[t]%divisor)==[0,0,0],"independent pre-leading divisibility");
    res=vector(3,t,lift(Mod(vals[t]/divisor,3)/unit));code=res[1]+3*res[2]+9*res[3];
    rr_assert(code==if(VECTOR_CHECK_ORDERS[k]==m,expected[k][ell],0),"independent leading vector");
    checks++
   )
  ));
 );
 print("RETURN_VECTOR_COMPONENT mask=",mask," genus=",g," all27_leading_components=true")
);
my(m=4612667318440142838161351077120075366400,B=256,L=28080,ord=znorder(Mod(3,B*m)),k0=ord/gcd(ord,L),r0=L*k0);
rr_assert(lift(Mod(3,B*m)^r0)==1,"normal degree integrality and annihilator");
print("NORMALITY_EXPONENT_PERIOD multiplicative_order=",ord," k_multiple=",k0," r_multiple=",r0," graph_degree_bound=",81*769);
print("RETURN_VECTOR_CHECK_COMPLETED comparisons=",checks," wall_ms=",getwalltime()-start);
}
quit;

\\ Actual mask83 is supersingular and delta_k=-beta4 through order242 for allk>=1.
\\ Its first formal return term is proved to have exact order81.
\\ Recover it via the Picard logarithm residues, retaining only the precision needed at each m.
default(parisizemax,1000000000);
default(nbthreads,1);
read("research/tools/bmd_prime_power_coeff_core_20261008.gp");
{
my(start=getwalltime(),contexts=vector(5),setups=vector(5),out="research/results/bmd-exception-return-vectors-20261008/log-control.txt",first=0);
for(K=1,5,
 my(setup=rr_setup(K),av=setup[1],one=av^0,R=prod(i=0,8,if(bittest(83,i),one+av^i*T,one)));
 setups[K]=setup;contexts[K]=rr_context(R,K,setup)
);
for(m=1,81,
 my(v=valuation(m,3),K=v+1,setup=setups[K],raw=-rr_coeff(contexts[K],81*m-1),coeff=vector(3,j,lift(polcoef(lift(raw),j-1,setup[3]))),divisor=3^v,unit=m/divisor,res);
 rr_assert(vector(3,j,coeff[j]%divisor)==[0,0,0],"pre-leading logarithm numerator not divisible");
 res=vector(3,j,lift(Mod(coeff[j]/divisor,3)/unit));
 if(res!=[0,0,0],
  rr_assert(m==81,"supersingular return appeared at wrong order");first=m;
  print("SUPERSINGULAR_LOG_LEADING order=",m," tangent_coefficients=",res);
  write(out,"SUPERSINGULAR_LOG_LEADING order=",m," tangent_coefficients=",res)
 )
);
rr_assert(first==81,"proved nonlinear return was not recovered");
my(setup=setups[5],av=setup[1],one=av^0,R=prod(i=0,8,if(bittest(83,i),one+av^i*T,one)),direct=1/sqrt(R+O(T^6561)),value=polcoef(direct,6560,T),extracted=rr_coeff(contexts[5],6560));
rr_assert(value==extracted,"direct actual coefficient6560");
print("RETURN_LOG_CONTROL_COMPLETED all81_preleading_tests=true direct6560=true wall_ms=",getwalltime()-start);
write(out,"RETURN_LOG_CONTROL_COMPLETED all81_preleading_tests=true direct6560=true wall_ms=",getwalltime()-start);
}
quit;

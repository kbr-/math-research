\\ Reference extraction of [T^N]R(T)^(-1/2) modulo3^K in the unramified cubic ring.
\\ R(0)=1. Polynomial degrees depend on K,degR, not on N.
\\ Installed PARI polynomial arithmetic; all contexts/powers are shared per R,K.
default(parisizemax,1000000000);
default(nbthreads,1);
read("research/tools/bmd_prime_power_coeff_core_20261008.gp");
{
my(start=getwalltime(),masks=[7,83,511],indices=[0,1,2,3,8,9,26,27,80,81,100,242],checks=0,hugechecks=0,detected=0,out="research/results/bmd-exception-return-vectors-20261008/coefficient-controls.gp");
my(plain="research/results/bmd-exception-return-vectors-20261008/coefficient-controls.txt");
write(plain,"195");
write(out,"{");
write(out,"COEFFICIENT_CONTROLS=[");
for(K=1,5,
 my(setup=rr_setup(K),av=setup[1],one=av^0);
 for(ii=1,#masks,
  my(mask=masks[ii],R=prod(i=0,8,if(bittest(mask,i),one+av^i*T,one)),ctx=rr_context(R,K,setup),direct=1/sqrt(R+O(T^243)));
  for(j=1,#indices,
   my(N=indices[j],val=rr_coeff(ctx,N));
   rr_assert(val==polcoef(direct,N,T),"direct-series coefficient");
   write(out,"[",K,",",mask,",",N,",",vector(3,t,lift(polcoef(lift(val),t-1,setup[3]))),"],");
   write(plain,K," ",mask," ",N," ",lift(polcoef(lift(val),0,setup[3]))," ",lift(polcoef(lift(val),1,setup[3]))," ",lift(polcoef(lift(val),2,setup[3])));
   checks++
  )
 );
 my(b=av+2,R=(one+b*T)^2,ctx=rr_context(R,K,setup));
 for(j=1,3,
  my(N=[81*3^25-1,3^17+5,3^8+2][j],val=rr_coeff(ctx,N),expected=(-b)^N);
  rr_assert(val==expected,"huge geometric coefficient");
  if(rr_coeff(ctx,N,0)!=expected,detected++);
  write(out,"[",K,",0,",N,",",vector(3,t,lift(polcoef(lift(val),t-1,setup[3]))),"],");
  write(plain,K," 0 ",N," ",lift(polcoef(lift(val),0,setup[3]))," ",lift(polcoef(lift(val),1,setup[3]))," ",lift(polcoef(lift(val),2,setup[3])));
   hugechecks++
 );
 print("COEFFICIENT_PRECISION K=",K," modulus=",3^K," direct_checks=",#masks*#indices," huge_checks=3")
);
rr_assert(detected>0,"wrong Frobenius transport was not detected");
write(out,"[]];");
write(out,"}");
print("PRIME_POWER_COEFFICIENT_COMPLETED direct=",checks," huge=",hugechecks," missing_twist_rejections=",detected," wall_ms=",getwalltime()-start);
}
quit;

\\ Test exact integer endomorphism polynomial congruences modulo3^5.
\\ [3^5] has no formal terms of degree<243; this bounds all jets through81.
\\ This is a finite-precision map certificate, not a theta/normality certificate.
default(parisizemax,500000000);
default(nbthreads,1);
assert(c,msg)={if(!c,error(msg));};
read("research/results/bmd-exception-return-defect-20261008/weil-polynomials.gp");
{
my(start=getwalltime(),out="research/results/bmd-exception-return-defect-20261008/ring-certificate.gp",periods=[1,3,9,27,81],counts=vector(5),globalperiod=1,plain="research/results/bmd-exception-return-defect-20261008/ring-input.txt");
write(plain,"466 243 9360");
assert(#RETURN_POLYNOMIALS==466,"complete character list");
write(out,"{");
write(out,"RETURN_MODULUS=243;");
write(out,"RETURN_POWER=9360;");
write(out,"RETURN_CERTIFICATES=[");
for(i=1,#RETURN_POLYNOMIALS,
 my(row=RETURN_POLYNOMIALS[i],S=row[1],g=row[2],poly=row[4],v=Mod(x,Mod(1,243)*poly),tau=v^9360,found=0);
 assert(poldegree(poly)==2*g && polcoef(poly,2*g)==1 && polcoef(poly,0)==27^g,"Weil degree and endpoints");
 assert(subst(poly,x,1)==row[3],"recorded group order");
 for(j=1,#periods,if(!found && tau^(periods[j]+1)==tau,found=j;globalperiod=lcm(globalperiod,periods[j]);counts[j]++));
 assert(found>0,"proposed finite return period does not hold");
 my(coeff=vector(2*g,j,lift(polcoef(lift(tau),j-1))));
 write(plain,S," ",g," ",periods[found]);
 for(j=0,2*g,write(plain,polcoef(poly,j)));
 for(j=1,2*g,write(plain,coeff[j]));
 assert(Mod(Polrev(coeff)*Mod(1,243),Mod(1,243)*poly)==tau,"all retained residue coefficients");
 write(out,"[",S,",",periods[found],",",coeff,"]",if(i<#RETURN_POLYNOMIALS,",","];\n"));
 if(S==7,assert(poly==x^2-4*x+27,"ordinary control polynomial");print("ORDINARY_CONTROL subset7 period=",periods[found]," tau_coefficients=",coeff));
 if(S==83,assert(poly==x^2+27 && tau==0,"supersingular actual quotient");print("SUPERSINGULAR_CONTROL subset83 tau=0 mod243 exact_power=3^14040"));
);
write(out,"RETURN_GLOBAL_PERIOD=",globalperiod,";");
write(out,"}");
print("RETURN_RING_COMPLETED characters=466 modulus=243 return_power=9360 global_period=",globalperiod," period_counts=",counts," wall_ms=",getwalltime()-start);
}
quit;

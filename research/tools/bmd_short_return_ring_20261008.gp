\\ Short-return integer polynomial certificates and all bounded return powers.
default(parisizemax,500000000);
default(nbthreads,1);
read("research/results/bmd-exception-return-defect-20261008/weil-polynomials.gp");
{
my(start=getwalltime(),periods=[1,2,3,6,9,18,27,54,81,162],counts=vector(10),globalperiod=1,rows=List(),plain="research/results/bmd-exception-short-returns-20261008/ring-input.txt",out="research/results/bmd-exception-short-returns-20261008/vector-input.txt");
if(#RETURN_POLYNOMIALS!=466,error("complete quotient list"));
write(plain,"466 243 1560");
for(i=1,466,
 my(row=RETURN_POLYNOMIALS[i],g=row[2],P=row[4],tau=Mod(x,Mod(1,243)*P)^1560,found=0);
 if(poldegree(P)!=2*g || polcoef(P,2*g)!=1 || subst(P,x,1)!=row[3],error("quotient polynomial scope"));
 for(j=1,#periods,if(!found&&tau^(periods[j]+1)==tau,found=j;counts[j]++;globalperiod=lcm(globalperiod,periods[j])));
 if(!found,error("short return needs a larger period"));
 listput(rows,[row[1],g,tau]);
 write(plain,row[1]," ",g," ",periods[found]);
 for(j=0,2*g,write(plain,polcoef(P,j)));
 for(j=0,2*g-1,write(plain,lift(polcoef(lift(tau),j))));
);
write(out,"466");
for(i=1,466,
 my(row=rows[i],tau=row[3],v=tau,g=row[2]);write(out,row[1]," ",g);
 for(k=1,globalperiod,
  for(j=0,2*g-1,write(out,lift(polcoef(lift(v),j))));v*=tau
 );
 if(v!=tau,error("positive-index closure"));
);
print("SHORT_RETURN_RING_COMPLETED power1560 modulus243 period=",globalperiod," candidates=",periods," counts=",counts," characters466 wall_ms=",getwalltime()-start);
}
quit;

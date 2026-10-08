\\ Reuse every proved character polynomial; generate all27 reduced endomorphism powers once.
default(nbthreads,1);
read("research/results/bmd-exception-return-defect-20261008/weil-polynomials.gp");
{
my(out="research/results/bmd-exception-return-vectors-20261008/vector-input.txt");
write(out,"466");
for(i=1,#RETURN_POLYNOMIALS,
 my(row=RETURN_POLYNOMIALS[i],g=row[2],v=Mod(x,Mod(1,243)*row[4]),tau=v^9360,power=tau);
 write(out,row[1]," ",g);
 for(k=1,27,
  for(j=0,2*g-1,write(out,lift(polcoef(lift(power),j))));
  power*=tau
 );
 if(power!=tau,error("positive-index return relation"))
);
print("RETURN_VECTOR_INPUT_COMPLETED characters466 returns27 shared_incremental_powers=true");
}
quit;

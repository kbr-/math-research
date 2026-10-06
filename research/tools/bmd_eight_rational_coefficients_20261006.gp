\\ Exact integer-factor audit of the six nonzero flat coefficients and exceptional source scalars.
default(nbthreads,1);
{
my(states=[1,2,3,4,5,8],values=[-4064256,476160,-34560,3072,31934976,4171059200],all=Set([]));
for(j=1,#values,my(f=factor(abs(values[j])));if(factorback(f)!=abs(values[j]),error("factor roundtrip"));all=setunion(all,Set(Vec(f[,1])));print("STATE=",states[j]," COEFFICIENT=",values[j]," FACTORS=",f));
print("COEFFICIENT_PRIMES=",all," MAX=",vecmax(all));
for(j=1,4,my(a=[37752,-44040192/143,917504/33,-11088][j]);print("SOURCE_SCALAR=",a," NUMERATOR_FACTORS=",factor(abs(numerator(a)))," DENOMINATOR_FACTORS=",factor(denominator(a))));
}
quit;

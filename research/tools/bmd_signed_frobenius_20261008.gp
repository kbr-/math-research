\\ Verify the complete small-index control for signed sums on x^2-10x+6561.
\\ BHV primitive divisors exclude equality U_a=U_b whenever a>b>=1 and a>30.
\\ Stages: compute all U_0..U_30 once; independent quadratic-power coefficients;
\\ test distinctness; negative control x^2-2x+3 has U_3=U_1 and lambda^3-lambda=-6.
\\ Fixed 31 coefficients, 465 pair comparisons; no unbounded exponent enumeration.
default(nbthreads,1);
assert(c,s)={if(!c,error(s));};
lucas(t,q,N)={my(u=vector(N+1));u[2]=1;for(n=2,N,u[n+1]=t*u[n]-q*u[n-1]);u;};
{
my(N=30,u=lucas(10,6561,N),f=x^2-10*x+6561,z=Mod(x,f),pow=1,checks=0);
assert(gcd(10,6561)==1 && polisirreducible(f),"Lucas hypotheses");
for(n=0,N,
 assert(u[n+1]==polcoef(lift(pow),1),"quadratic quotient-ring verification");
 print("LUCAS n=",n," value=",u[n+1]);
 for(m=0,n-1,assert(u[n+1]!=u[m+1],"small-index repetition");checks++);
 pow*=z
);
my(v=lucas(2,3,3),bad=Mod(x,x^2-2*x+3));
assert(v[4]==v[2] && bad^3-bad==-6,"nonvacuous repeated-value control");
assert(u[2]==1 && u[3]==10 && u[4]==-6461,"initial recurrence control");
print("SIGNED_FROBENIUS_COMPLETED distinct_values=",#Set(u)," pair_comparisons=",checks," independent_power_checks=",N+1," negative_control_difference=-6");
}
quit;

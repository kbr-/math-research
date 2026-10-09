\\ Factor only the residual norm gcds from the3 bounded inconclusive lines.
\\ A norm common factor is not asserted to be a generic cofactor divisor.
default(parisizemax,500000000);
default(parisize,64000000);
x='x;
read("research/results/bmd-reduced-boundary-20261010/diagnostic-data.gp");
{
for(i=1,#DATA,
 my(G=Mod(1,3)*Polrev(DATA[i][2],x),F=factor(G));
 print("LINE = ",DATA[i][1],"; DEGREE = ",poldegree(G),"; FACTORS = ",F);
 print("FACTOR_DEGREES_MULTIPLICITIES = ",matrix(matsize(F)[1],2,j,k,if(k==1,poldegree(F[j,1]),F[j,2])));
 print("DIVIDES_X81_MINUS_X = ",((x^81-x)%G==0))
);
print("NORM_GCD_DIAGNOSTIC_COMPLETED")
}
quit;

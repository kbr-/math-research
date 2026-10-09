\\ Test the concrete multiple-collision explanation of the three failed norm lines.
\\ Enumerate all81 line parameters, retain every collision pattern, and compare
\\ the entire gcd polynomial with the norm of the predicted squared factors.
default(parisizemax,500000000);
default(parisize,64000000);
x='x;z='z;
read("research/results/bmd-reduced-boundary-20261010/collision-data.gp");
normp(P)={my(Z=1);for(j=0,3,Z*=sum(k=0,poldegree(P,x),polcoef(P,k,x)^(3^j)*x^k));Z};
{
for(ci=1,#DATA,
 my(d=DATA[ci],f=Mod(1,3)*Polrev(d[2],z),g=ffgen(f,'g),o=g^0,al=concat([0*o],vector(9,i,sum(j=0,3,d[3][i][j+1]*g^j))),be=concat([0*o],vector(9,i,sum(j=0,3,d[4][i][j+1]*g^j))),G=Mod(1,3)*Polrev(d[5],x),CP=o,bad=0,support=0);
 if(!polisirreducible(f),error("field modulus"));
 for(code=0,80,
  my(v=sum(j=0,3,((code\3^j)%3)*g^j),aa=vector(10,i,al[i]+v*be[i]),unique=Set(aa),sizes=vector(#unique,j,sum(i=1,10,aa[i]==unique[j])),pairs=sum(j=1,#sizes,sizes[j]*(sizes[j]-1)/2),disjoint=sum(j=1,#sizes,sizes[j]\2));
  if(subst(o*G,x,v)==0,support++);
  if(pairs>=2,print("LINE = ",d[1],"; POINT_CODE = ",code,"; CLUSTERS = ",sizes,"; DISJOINT_PAIRS = ",disjoint));
  if(disjoint>=2,bad++;CP*=(x-v)^2)
 );
 my(predicted=normp(CP));
 print("LINE = ",d[1],"; MULTIPLE_COLLISION_POINTS = ",bad,"; NORM_GCD_SUPPORT = ",support,"; EXACT_PREDICTED_GCD = ",(predicted==o*G))
);
print("COLLISION_DIAGNOSTIC_COMPLETED")
}
quit;

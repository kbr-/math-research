\\ Named test: can the doubled four-cycle with equal metric lengths rule out
\\ a section of 2K-12P at an edge midpoint? This is a proposed skeleton control,
\\ NOT an established degeneration of the root curve or a normality theorem.
\\ Subdivide each of its eight edges once: 12 vertices,16 edges,genus5.
\\ The residual degree is4; at most binomial(15,4)=1365 effective divisors.
\\ Use one exact grounded Laplacian inverse; stop at the first witness.
{
my(nv=12,L=matrix(nv,nv),a,b,c,h);
for(i=1,4,for(j=1,2,
 a=i;b=i%4+1;c=4+2*(i-1)+j;
 for(k=1,2,h=if(k==1,a,b);L[h,h]++;L[c,c]++;L[h,c]--;L[c,h]--);
));
my(K=vector(nv,i,L[i,i]-2)~,D=2*K);D[5]-=12;
if(vecsum(K)!=8||vecsum(D)!=4,error("genus/degree control"));
my(A=L[1..nv-1,1..nv-1],Ai=A^-1,count=0,found=0,E,z,zz);
print("GRAPH_LAPLACIAN = ",L);
print("CANONICAL = ",K);print("TARGET_2K_minus_12P = ",D);
print("GROUNDED_DETERMINANT = ",matdet(A));
for(i=1,nv,for(j=i,nv,for(k=j,nv,for(l=k,nv,
 count++;E=vector(nv)~;E[i]++;E[j]++;E[k]++;E[l]++;
 z=Ai*(D-E)[1..nv-1];
 if(denominator(z)==1,
  zz=concat(z,[0]~);
  if(L*zz!=D-E,error("integer witness verification"));
  print("EFFECTIVE_WITNESS = ",E);
  print("INTEGER_POTENTIAL = ",zz);
  found=1;break(4);
 );
))));
if(!found&&count!=binomial(15,4),error("enumeration incomplete"));
print("CANDIDATES_TESTED = ",count," FOUND = ",found);
print("GRAPH_CONTROL_COMPLETED");
}
quit;

\\ Fixed h=16 arithmetic for the existing joint leading coefficient.
\\ Exhausts the required residue tables, not root-curve determinants by degree.
assert(c,s)={if(!c,error(s));};
H(B)={prod(i=1,15,prod(j=i,15,(2*B+i+j)/(i+j)));};
{
my(allcounts=0);
forprime(p=3,29,
 my(q=p,levels=List());
 while(q<=30,
   my(C=vector(q,r,sum(i=1,15,sum(j=i,15,(i+j)%q==r-1))));
   assert(C[1]==vecmin(C),"baseline not minimal");
   my(R=select(r->C[r+1]==C[1],vector(q,r,r-1)));
   print("q=",q," baseline=",C[1]," zero_excess_residues=",R);
   listput(levels,[q,R]);q*=p;
 );
 my(PER=q,good=List());
 for(r=0,PER-1,
   my(d=r+2*PER,B=16*d-32,x=-2*B,ok=!(2<=x%PER && x%PER<=30));
   for(k=1,#levels,ok=ok && setsearch(Set(levels[k][2]),x%levels[k][1])!=0);
   my(h=H(B));assert(denominator(h)==1,"nonintegral H");
   assert(ok==(valuation(h,p)==0),"residue criterion disagrees with exact product");
   if(ok,listput(good,r));allcounts++;
 );
 print("p=",p," period=",PER," unit_degree_residues=",Vec(good)," count=",#good);
);
my(B=32,A=B+16,S=vecsort(concat(vector(A,i,2*(i-1)),vector(B,i,2*(i-1)+1))),N=A+B);
my(V=prod(i=1,N,prod(j=i+1,N,S[j]-S[i]))/prod(i=0,N-1,i!));
assert(V==2^120*H(B),"branch binomial normalization");
print("PASS: d=4 branch binomial determinant equals 2^120 H_32^(16)");
print("d=4 scalar H factorization=",factor(H(B)));
print("PASS: all ",allcounts," small-prime period residues match the exact integral product");
}
quit;

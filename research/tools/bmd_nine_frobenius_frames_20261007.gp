\\ Compile three common short-jet frames for all n9 prime-power leaves.
\\ Reuse the accepted degree-four point; this constructs the new frame, not a new degree certificate.
default(parisizemax,3000000000);
default(nbthreads,1);
setrand(20261007);
assert(c,s)={if(!c,error(s));};
source_columns(d)={my(cols=List());for(mask=0,511,if(hammingweight(mask)<=d,for(q=0,(d-hammingweight(mask))\2,listput(cols,[mask,q]))));Vec(cols);};
prefixes(roots,N)={
 my(o=polcoef(roots[1],0,T),products=vector(512),coefs=vector(512));
 products[1]=o+O(T^N);coefs[1]=vector(N,j,if(j==1,o,0*o));
 for(mask=1,511,if(hammingweight(mask)<=9,
  my(bit=valuation(mask,2),previous=mask-2^bit);
  products[mask+1]=products[previous+1]*roots[bit+1];
  coefs[mask+1]=vector(N,j,polcoef(products[mask+1],j-1,T));
 ));coefs;
};
marked(coefs,cols,N,o)={matrix(N,N,i,j,if(i<=cols[j][2],0*o,coefs[cols[j][1]+1][i-cols[j][2]]));};
{
my(modulus=ffinit(3,8,'a),a=ffgen(modulus,'a),o=a^0,N=256);
my(aa=[2*a^6+2*a^4+2*a^2+a+2,2*a^7+2*a^6+a^5+2*a^3+a^2+a+2,2*a^7+a^6+2*a^4+2*a^3+a^2,2*a^7+a^6+a^5+a^4+2*a^2+2,a^7+2*a^5+a+2,2*a^7+a^4+a^3,a^6+a^4,a^4+2*a^3+1,2*a^7+a^6+2*a^5+2*a^4+a+1]);
my(ell=vector(9,i,o+aa[i]*T+O(T^N)),roots=apply(sqrt,ell));
for(i=1,9,assert(valuation(roots[i]^2-ell[i],T)>=N,"root equations"));
my(coefs=prefixes(roots,N),I4=source_columns(4),I9=source_columns(9),lookup=Map());
for(i=1,#I9,mapput(lookup,I9[i],i));
my(J=matrix(N,#I9,i,j,if(i<=I9[j][2],0*o,coefs[I9[j][1]+1][i-I9[j][2]])),cols4=vector(#I4,j,mapget(lookup,I4[j])),B=matrix(N,#I4,i,j,J[i,cols4[j]]),piv=matindexrank(B)[2]);
assert(#piv==N,"degree-four short jets not onto");
my(indices=vector(N,i,cols4[piv[i]]),A=matrix(N,N,i,j,J[i,indices[j]]),detA=matdet(A));assert(detA!=0,"pivot minor");
print("FIELD = ",modulus,"; SLOPES = ",aa);
print("PIVOT_SOURCE_INDICES = ",vector(N,j,I9[indices[j]]));
print("PIVOT_DETERMINANT = ",detA);
print("MASTER_NORMALIZATION_STARTED rows256 cols",#I9);
my(C=matsolve(A,J));assert(A*C==J,"master reconstruction");
assert(matrix(N,N,i,j,C[i,indices[j]])==matid(N)*o,"normalized common frame");
my(dims=vector(3,j,#source_columns(j+6)));assert(dims==[1024,1280,1536],"three fixed source dimensions");
print("MASTER_DIMENSIONS = ",dims,"; COMMON_JET_FRAME = ",N,"; RECONSTRUCTION_ENTRIES = ",N*#I9);
print("NINE_MASTER_FRAMES_COMPLETED: fixed source indices define the generic rational frame via the formal 256-square inverse; no generic coefficient expansion or complete exception set is asserted.")
}
quit;

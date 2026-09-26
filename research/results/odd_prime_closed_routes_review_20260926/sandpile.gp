\\ Critical (sandpile) group of K_{m,n}: Smith normal form of the reduced Laplacian (route review bridge test).
crit(m,n)={my(N=m+n,L=matrix(N,N)); for(i=1,m,for(j=1,n,L[i,m+j]=-1;L[m+j,i]=-1)); for(i=1,m,L[i,i]=n); for(j=1,n,L[m+j,m+j]=m); my(R=matrix(N-1,N-1,a,b,L[a,b])); select(x->x>1, matsnf(R))};
for(k=2,6, print([k+1,k], " ", crit(k+1,k)));
quit;

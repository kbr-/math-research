\\ Symbolic seven-cut profile for the existing general-even-cut lemma on Y_(4,d).
\\ This is an exact polynomial identity/profile audit, not a degree-normality grid.
default(parisizemax,1000000000);
default(nbthreads,1);
assert(c,s)=if(!c,print("FAIL ",s);quit(1));
binompoly(t,k)=prod(j=0,k-1,t-j)/k!;
A=matrix(7,7,i,j,binompoly(z-j+1,2*i-1));D=matdet(A);
assert(poldegree(D,z)==28,"predicted determinant degree");
F=factor(D);roots=List();multiplicities=List();
{for(i=1,matsize(F)[1],assert(poldegree(F[i,1],z)==1,"all ordinary determinant factors linear");my(rr=-polcoef(F[i,1],0,z)/polcoef(F[i,1],1,z));listput(roots,rr);listput(multiplicities,F[i,2]));}
assert(Set(Vec(roots))==vector(13,j,j-1),"exact ordinary excluded residues zero through twelve");
assert(D==pollead(D,z)*prod(i=1,matsize(F)[1],F[i,1]^F[i,2]),"factorization multiplied back");
print("ORDINARY_DETERMINANT ",D);print("ORDINARY_FACTORIZATION ",F);print("ORDINARY_CONTENT ",content(D));
exceptionPrimes=List();factorprimes(t)={my(f=factor(abs(t)));for(i=1,matsize(f)[1],listput(exceptionPrimes,f[i,1]));};
factorprimes(numerator(content(D)));factorprimes(denominator(content(D)));
profiles=vector(13);profileCoordinates=vector(13);profilesChecked=0;controlsChecked=0;
{for(r=0,12,my(A=matrix(7,14,i,j,binomial(r-j+1,2*i-1)),idx=matindexrank(A)[2]);assert(#idx==7,"full fourteen-column rank");idx=Vec(vecsort(idx));my(C=matrix(7,7,i,j,A[i,idx[j]]),det=matdet(C),coords=C^-1*A);assert(denominator(det)==1&&det!=0,"nonzero integer pivot minor");
for(j=1,14,for(i=1,7,if(idx[i]>j,assert(coords[i,j]==0,"each skipped column uses only earlier pivots"))));
profileCoordinates[r+1]=coords;factorprimes(det);profiles[r+1]=apply(x->x-1,idx);profilesChecked++;print("PROFILE residue=",r," pivot_offsets=",profiles[r+1]," determinant=",det," prime_factors=",factor(abs(det)));
);}
print("ALL_TEMPLATE_BAD_PRIMES ",Set(Vec(exceptionPrimes)));
\\ Direct full Pascal constraints validate the tail rule at every residue in two fields.
{my(checked=0);forprime(p=17,53,if(p!=17&&p!=53,next);for(c=63,63+p-1,my(N=2*c+1,A=matrix(7,N+1,i,j,Mod(binomial(N-j+1,2*i-1),p)),idx=Vec(vecsort(matindexrank(A)[2])),tail=matrix(7,14,i,j,A[i,j]),ti=Vec(vecsort(matindexrank(tail)[2])));assert(idx==ti,"full exact coefficient matrix and fourteen-column profile agree");assert(#idx==7,"full constraint rank");my(r=N%p);if(r>12,assert(idx==[1,2,3,4,5,6,7],"ordinary consecutive profile"),assert(apply(x->x-1,idx)==profiles[r+1],"symbolic residue profile reduction"));checked++;controlsChecked++));print("FULL_PASCAL_CONTROLS ",checked," fields17and53 all_residues=true");}
assert(profilesChecked==13&&controlsChecked==70,"all symbolic and finite controls completed");
write("research/results/bmd-normality-synthesis-20261009/profiles.gp","ordinaryDet=",D,";profileOffsets=",profiles,";profileCoordinates=",profileCoordinates,";templateBadPrimes=",Set(Vec(exceptionPrimes)),";");
print("COMPLETE symbolic ordinary identity, all thirteen profiles and exact full-matrix controls.");
quit;

\\ Exact controls for the branch-leading osculating obstruction.
\\ One 17-dimensional monomial model and one 3-dimensional higher-term repair.
\\ No original root-curve normality is inferred from these tests.
default(parisizemax, 200000000);
A=vecsort(concat(vector(12,i,2*(i-1)),vector(5,i,2*i-1)));
print("exponents=",A);
for(h=1,3,q=3^h;print("counts_mod_",q,"=",vector(q,r,sum(i=1,#A,(A[i]%q)==r-1))));
B=matrix(16,17,i,j,Mod(binomial(A[j],i-1),3));
cof=vector(17,j,(-1)^(j-1)*matdet(matrix(16,16,r,c,B[r,c+(c>=j)])));
support=select(j->cof[j]!=0,vector(17,j,j));
assert(x,s)=if(!x,error(s));
assert(vector(#support,i,A[support[i]])==[0,9,18],"wrong cofactor support");
print("omitted_exponents=",vector(#support,i,A[support[i]]));
print("nonzero_signed_constants=",vector(#support,i,lift(cof[support[i]])));
print("cofactor_powers=",vector(#support,i,sum(j=1,#A,A[j])-A[support[i]]-binomial(16,2)));
assert(matrank(B)==16,"prefix rank");
assert(matdet(matrix(17,17,i,j,Mod(binomial(A[j],i-1),3)))==0,"full leading determinant");
f=[1,x,x^3+x^5];
J=matrix(3,3,i,j,sum(k=i-1,5,polcoef(f[j],k)*binomial(k,i-1)*x^(k-i+1))*Mod(1,3));
c=vector(3,j,(-1)^(j-1)*matdet(matrix(2,2,r,k,J[r,k+(k>=j)])));
assert(c==[x^5-x^3,x^4,1]*Mod(1,3),"repaired cofactors");
assert(matdet(J)==x^3*Mod(1,3),"repaired full determinant");
print("abstract_repair_cofactors=",c);
print("abstract_repair_determinant=",matdet(J));
print("PASS: all 17 leading cofactors and the exact higher-term repair");
quit;

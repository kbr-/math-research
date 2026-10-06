\\ Exact characteristic-three two-label coface and smaller-prefix comparison.
\\ Proves polynomial identities by exact symbolic arithmetic, not sampling.
default(parisizemax,1000000000);
{
my(o=Mod(1,3),beta=[1,2,1,1,2,1,0,0,0,1],wa=sum(k=0,9,o*beta[k+1]*a^k*T^k),wb=subst(wa,a,b));
for(k=0,9,if(polcoeff(wa^2-o-o*a*T,k,T)!=0,error("exact square-root prefix")));
my(rows=[o,o*T,o*T^2,wa,T*wa,wb,T*wb,wa*wb],M=matrix(8,8,i,j,polcoeff(rows[i],j-1,T)),delta=matdet(M));
my(old=[o,o*T,wa,wb,wa*wb],O=matrix(5,5,i,j,polcoeff(old[i],j-1,T)),small=matdet(O));
if(delta!=-a^8*b^8*(a+b)*(a-b)^6*o,error("coface identity"));
if(small!=a^3*b^3*(b-a)^3*o,error("original identity"));
if(delta!=-a^2*b^2*(a+b)*small^2,error("factor comparison"));
my(pure=vecextract(M,[4,5,6,7],[4,5,6,7]));
if(matdet(pure)!=-a^6*b^6*(a-b)^4*o,error("four-row minor"));
my(pivotrows=[o,o*T,o*T^2,wa^3,wb^3,T*wa,T*wb,wa*wb],P=matrix(8,8,i,j,polcoeff(pivotrows[i],j-1,T)));
my(I=[1,2,3,4,7],J=[5,6,8],A=vecextract(P,[1,2,3,4,5],I),B=vecextract(P,[1,2,3,4,5],J),C=vecextract(P,[6,7,8],I),E=vecextract(P,[6,7,8],J),S=E-C*A^-1*B);
if(matdet(A)!=a^3*b^3*(a-b)^3*o,error("pivot identity"));
if(matdet(S)!=a^5*b^5*(a+b)*(a-b)^3*o,error("residual identity"));
my(Mopp=subst(M,b,-a),Oopp=subst(O,b,-a),Sopp=subst(S,b,-a));
if(matrank(Mopp)!=7 || matrank(Oopp)!=5 || matrank(Sopp)!=2,error("opposite ranks"));
my(f=subst(wa*wb-a*T*wa+a*T*wb+wa+wb+a^2*T^2,b,-a));
for(k=0,7,if(polcoeff(f,k,T)!=0,error("witness lower coefficient")));
if(polcoeff(f,8,T)!=-a^8*o,error("witness order eight"));
print("coface determinant = ",delta);
print("smaller original determinant = ",small);
print("four-row minor = ",matdet(pure));
print("pivot determinant = ",matdet(A));
print("residual matrix = ",S);
print("residual determinant = ",matdet(S));
print("opposite-label ranks [coface,original,residual] = ",[matrank(Mopp),matrank(Oopp),matrank(Sopp)]);
print("opposite-label witness through order nine = ",sum(k=0,9,polcoeff(f,k,T)*T^k));
print("PASS: symbolic identities and exact ranks over F3(a); a nonzero, b=-a remains admissible.");
}
quit;

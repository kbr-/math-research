\\ Exact controls for f_t=x^9+x^8+x^5+x-t over F_3.
\\ Test a simple critical value and ordinary quadratic subset quotients.
\\ Stdout is the full certificate; retain with save-run-output.py.
default(parisizemax,1000000000);
default(nbthreads,1); setrand(20261007);
check(c,s)={if(!c,print("FAIL: ",s);quit(1));};
{
f=Mod(1,3)*(x^9+x^8+x^5+x-t);
df=deriv(f,x); disc=polresultant(f,df,x);
print("pencil=",f); print("derivative=",df); print("critical_values=",disc);
check(poldegree(gcd(df,deriv(df,x)),x)==0,"critical points not simple");
check(poldegree(disc,t)==7,"wrong critical value degree");
dc=factormod(disc); print("critical_value_factorization=",dc);
check(sum(i=1,matsize(dc)[1],dc[i,2]==1)>0,"no simple critical value");
H=matrix(4,4,i,j,polcoef(f,3*i-j,x));
print("full_Cartier=",H); print("full_Cartier_determinant=",matdet(H));
check(matdet(H)!=0,"full quotient not ordinary");
best=0; ext=10^9;
for(v=0,2,if(subst(disc,t,v)!=0,my(fac=factormod(subst(f,t,v)),e=1);for(i=1,matsize(fac)[1],e=lcm(e,poldegree(fac[i,1])));print("specialization=",v," factorization=",fac," splitting_degree=",e);if(e<ext,ext=e;best=v)));
check(ext<=60,"splitting extension exceeds control budget");
a=ffgen(ffinit(3,ext,'a),'a); roots=polrootsmod(subst(f,t,best),a);
check(#roots==9,"specialized pencil must have nine distinct roots");
print("selected_parameter=",best," field_polynomial=",a.mod," roots=",roots);
counts=vector(9); good=vector(9); witnesses=vector(9); dets=vector(9);
for(mask=1,511,my(m=hammingweight(mask));if(m>=3,my(R=1,g=(m-1)\2);for(i=1,9,if(bittest(mask,i-1),R*=x-roots[i]));my(C=matrix(g,g,i,j,polcoef(R,3*i-j,x)),d=matdet(C));counts[m]++;if(d!=0,good[m]++;if(witnesses[m]==0,witnesses[m]=mask;dets[m]=d))));
print("subset_counts=",counts);print("ordinary_counts=",good);print("witness_masks=",witnesses);print("witness_determinants=",dets);
for(m=3,9,check(counts[m]==binomial(9,m),"subset count mismatch");check(good[m]>0,"no ordinary witness for subset size"));
check(vecsum(counts)==466,"wrong total quotient count");
\\ Negative control: repeated-root polynomial must fail the squarefree test.
bad=(x-roots[1])^2*prod(i=2,8,x-roots[i]);
check(poldegree(gcd(bad,deriv(bad)))>0,"repeated-root control accepted");
\\ Exhaust all 81 products of the nine coefficient basis vectors under CRT.
for(i=0,8,for(j=0,8,my(rr=lift(Mod(x^(i+j),subst(f,t,best))));for(k=1,9,check(subst(rr,x,roots[k])==roots[k]^(i+j),"CRT multiplication mismatch"))));
ww=vector(9,j,eval(Str("w",j-1))); W=sum(j=1,9,ww[j]*x^(j-1));
rr=lift(Mod(W^2+x*z^2,f));
print("DESCENDED_X=",polcoef(rr,0,x));
for(j=1,8,print("DESCENDED_QUADRIC_",j,"=",polcoef(rr,j,x)));
print("PASS: simple branch value, ordinary witnesses, repeated-root control, 729 CRT product evaluations");
}
quit;

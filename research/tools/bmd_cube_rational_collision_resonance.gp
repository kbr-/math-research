\\ Exact tests of the rational four-block Hasse determinant and its smoothing.
\\ General identity: residual determinant = -(N^2-1) times the old eight-term form.
\\ Smallest cube control d=2: A=4, N=12, four blocks of sizes 5,3,3,1.
\\ Primes 11,13 must kill the constant collision determinant; 7 is a control.
\\ The next coefficients test repair by the actual balanced square-root smoothing.
\\ All binomial/Catalan quotients are evaluated over Q/Z before reduction mod p.
\\ Full stdout is retained with tools/save-run-output.py; no parameter sweep.

N='N; Q='Q; v='v;
b2=N*(N-1)/2; b3=N*(N-1)*(N-2)/6;
b4=N*(N-1)*(N-2)*(N-3)/24;
alpha=b2-N^2; beta=b4-N*b3;
if(alpha != -N*(N+1)/2, error("alpha identity"));
if(beta != -N*(N^2-1)*(N-2)/8, error("beta identity"));
residual=(Q-1)*(beta*Q/v*(1-v^2)+(1-N^2)*(Q^2-1))-alpha*b2*Q*(1-v)*(Q/v-1);
lo=N*(N-2)/8; hi=N*(N+2)/8; mid=N^2/4-1;
eight=1+Q^3-Q/v*(lo-mid*v+hi*v^2)-Q^2/v*(hi-mid*v+lo*v^2);
if(residual != -(N^2-1)*eight, error("integral residual identity"));
print("GENERAL_RESIDUAL_IDENTITY = -(N^2-1) * eight_term_form");
print("ALPHA = ",alpha); print("BETA = ",beta);
print("EIGHT_TERM_FORM = ",eight);

eps='eps;
sqrtcoef(a,j)=binomial(1/2,j)*a^j;
paircoef(a,b,j)=sum(i=0,j,sqrtcoef(a,i)*sqrtcoef(b,j-i));
raney(r,k)=if(k==0,1,if(r==0,0,(-1)^k*(r*binomial(r+2*k,k)/(r+2*k))/4^k));
{
my(A=4,sz=12,K=4,a=1,b=2, rows=List(), S,r,j,k,p,M,M0,delta,coeffs,rk);
for(S=0,3,
  my(s=if(S==0,0,if(S==3,2,1)));
  for(r=0,A-2*s,listput(rows,[S,r]));
);
rows=Vec(rows); if(#rows!=sz,error("row count"));
print("ROWS = ",rows);
print("PARAMETERS A=",A," N=",sz," a=",a," b=",b," smoothing_order=",K);
for(pi=1,3,
  p=[7,11,13][pi];
  M=matrix(sz,sz,ii,jj,
    S=rows[ii][1];r=rows[ii][2];j=jj-1;
    if(j<r,Mod(0,p),
      sum(k=0,min(K,j-r),
        my(w=if(S==0,if(j-r-k==0,1,0),if(S==1,sqrtcoef(a,j-r-k),if(S==2,sqrtcoef(b,j-r-k),paircoef(a,b,j-r-k)))));
        Mod(raney(r,k)*w,p)*eps^k
      )
    )
  );
  M0=subst(M,eps,0);rk=matrank(M0);delta=matdet(M);
  coeffs=vector(K+1,jj,lift(polcoef(delta,jj-1,eps)));
  print("PRIME ",p," constant_rank=",rk," det_coefficients_0_to_",K," = ",coeffs);
  if(p==11 || p==13,if(rk>sz-1,error("predicted collision singularity failed")));
  print("CONSTANT_MATRIX_MOD_",p," = ",lift(M0));
  print("TRUNCATED_SMOOTHING_MATRIX_MOD_",p," = ",lift(M));
);
}
quit;

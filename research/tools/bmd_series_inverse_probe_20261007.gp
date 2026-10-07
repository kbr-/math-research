\\ Probe installed PARI truncated-series inversion on a saved, certified graph pivot.
\\ Exact residual and exact-inverse comparison validate this one matrix, not a new general algorithm.
default(parisizemax,2000000000);
default(nbthreads,1);
assert(c,s)={if(!c,error(s));};
mval(M)={my(v=1000000);for(i=1,matsize(M)[1],for(j=1,matsize(M)[2],if(M[i,j]!=0,v=min(v,valuation(M[i,j],'u)))));v};
{
my(u='u,OO=Mod(1,3),NN=3,PP=3,BB=4,CC=12,AA=[OO,OO*u,OO*(u^2+u+2)],coords=List());
for(S=0,7,for(i=1,NN,if(!bittest(S,i-1),listput(coords,[S,i]))));my(COORD=Vec(coords),ZZ=vector(CC,c,-OO/AA[COORD[c][2]]),rowpow=vector(CC,c,max(0,-2*valuation(ZZ[c],u))));
my(lines=readstr("research/results/bmd-exception-adic-closure-20261007/canonical-pilot.txt"),base=0,record=0);
for(i=1,#lines,my(z=strsplit(lines[i],"BASE_STATE = "));if(#z==2,base=eval(z[2]));z=strsplit(lines[i],"EDGE = ");if(#z==2,my(e=eval(strsplit(z[2]," WALL_MS=")[1]));if(e[1]==1 && e[2]==1,record=e[4][1])));
assert(base!=0 && record!=0 && record[1]==0 && record[2]==0,"saved pivot selector");
my(ch=vector(3,r,my(jp=-floor((1-2*(r-1))/3),dp=BB*NN+BB*floor((1-2*(r-1))/3)-ceil((BB*(NN+1)-(r-1))/3));base[2][jp*CC+dp+1]),sizes=apply(U->matsize(U)[2],ch),s=vecsum(sizes),C=matrix(CC,s,i,j,0*OO),off=0);
for(r=0,2,for(c=1,CC,for(k=1,sizes[r+1],C[c,off+k]=u^rowpow[c]*ZZ[c]^r*ch[r+1][c,k]^3));off+=sizes[r+1]);
my(rows=record[4],cols=record[5],n=#rows,A=matrix(n,n,i,j,C[rows[i],cols[j]]),N=16,P=64);
assert(n==12,"probe sizing");print("INPUT_PIVOT = ",A);gettime();
my(As=matrix(n,n,i,j,A[i,j]+O(u^P)),Bs=matsolve(As,matid(n)),series_ms=gettime(),B=matrix(n,n,i,j,truncate(Bs[i,j])),kept=vecmin(vector(n,i,vecmin(vector(n,j,serprec(Bs[i,j],u))))));
assert(kept>=N,"series inverse lost required precision");my(R=A*B-matid(n),alpha=max(0,-mval(B)),residual=mval(R));assert(residual>0,"inverse residual does not certify invertibility");
gettime();my(exact=A^(-1),exact_ms=gettime(),agreement=mval(B-exact));assert(agreement>=N,"series inverse fails exact comparison");
my(bad=B);bad[1,1]+=OO*u^(N-1);assert(mval(bad-exact)<N,"corrupt inverse escaped comparison");
print("APPROXIMATE_INVERSE = ",B);
print("SERIES_CPU_MS=",series_ms," EXACT_CPU_MS=",exact_ms," RETAINED_ORDER=",kept," INVERSE_LOSS=",alpha," RESIDUAL_ORDER=",residual," EXACT_AGREEMENT_ORDER=",agreement," corruption_detected=1");
print("SERIES_INVERSE_PROBE_COMPLETED: one saved pivot; no complete transition or graph claim")
}
quit;

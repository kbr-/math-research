\\ Exhaust the finite character-to-jet conversion and pure-kernel coefficient rule.
\\ No normality claim: all 8 characters, both branch fibres, all required jet depths.
v;s;
assert(c,m)={if(!c,error(m));};
wt(l,j,n)={my(z=0);for(r=0,l,my(k=l-r,h=(j-n+k-r)/2);if(k>=0 && k<=n && h>=0 && denominator(h)==1 && (n>0 || r==0),z+=binomial(n,k)*(-1)^(n-k)*if(r==0,1,binomial(n+r-1,r))/4^(r+h)));z;};
{
my(exps=[[1,0],[1,0],[0,1],[0,1],[2,2],[2,2],[1,3],[1,3]],chs=[[1,1,1,1],[1,1,-1,-1],[1,-1,1,-1],[1,-1,-1,1]],found=List());
for(mask=0,7,
 my(par=hammingweight(mask),ch=concat([1],vector(3,j,(-1)^(bittest(mask,j-1)+par))),idx=setsearch(Set(chs),ch));
 idx=select(j->chs[j]==ch,[1,2,3,4])[1];
 for(b=1,2,for(k=0,exps[mask+1][b]-1,listput(found,[b,bittest(mask,b-1)+2*k,idx])));
);
my(expected=[[1,0,1],[1,0,2],[1,0,4],[1,1,1],[1,1,2],[1,1,3],[1,2,4],[1,3,3],[2,0,3],[2,0,4],[2,1,1],[2,1,2],[2,1,3],[2,1,4],[2,2,3],[2,2,4],[2,3,1],[2,3,2],[2,5,1],[2,5,2]]);
assert(#found==20 && Set(Vec(found))==Set(expected),"character condition mismatch");
print("PASS: all 8 characters at both fibres yield exactly the 20 stated conditions");
forprime(p=3,7,
 my(o=Mod(1,p),vv=v+O(v^7),yv=(2+vv)/(2-vv),ys=(2+s)/(2-s),kernel=(1/(ys/yv-1)+o)/(1-vv^2/4));
 for(j=1,6,my(E=polcoef(kernel,j-1,v));assert(valuation(E-s^(-j),s)>=0,"pure principal part failed"));
 my(x=(s-vv)/(1-s*vv/4));
 for(n=0,10,my(f=x^n/(1-vv^2/4)*o);for(j=0,5,my(c=polcoef(f,j,v)+O(s^6));for(l=0,5,assert(polcoef(c,l,s)==o*wt(l,j,n),"jet weight mismatch"))));
 print("PASS: p=",p," all six pure principal parts and all 396 local coefficient weights");
);
print("PASS: finite encoding audit complete");
}
quit;

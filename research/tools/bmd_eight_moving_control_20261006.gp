\\ Test the exact n8,d8,p3 moving coefficient via compatible lower-seven paired sources.
\\ N704,q729,alpha365,r384,s320. Preserve G=ell1 ell3^2 ell5^4.
\\ At most three admissible points, stopping at the first nonzero limiting determinant.
\\ If a limiting determinant vanishes, compare the original coefficient at an admissible seven-root point.
default(parisizemax,3000000000);
default(nbthreads,1);
setrand(20261006);
if(default(nbthreads)!=1,error("thread setting"));
assert(c,msg)={if(!c,error(msg));};
sourceV(aa,d,N)={my(o=aa[1]^0,w=vector(#aa,i,sqrt(o+aa[i]*T+O(T^N))),products=vector(2^#aa),cols=List());products[1]=o+O(T^N);for(mask=1,2^#aa-1,my(b=valuation(mask,2));products[mask+1]=products[mask-2^b+1]*w[b+1]);for(mask=0,2^#aa-1,if(hammingweight(mask)<=d,for(j=0,(d-hammingweight(mask))\2,listput(cols,products[mask+1]*T^j))));Vec(cols);};
jetmatrix(cols,N)={matrix(N,#cols,i,j,polcoef(cols[j],i-1,T));};
{
my(d=8,q=729,alpha=365,r=384,s=320,N=704,c=47,exps=[[2,2,0],[2,2,0],[1,3,0],[1,3,0],[1,0,3],[1,0,3],[0,1,3],[0,1,3]]);
my(modulus=ffinit(3,8,'a),a=ffgen(modulus,'a),o=a^0,success=0,negative=0);
print("QUESTION: compatible elliptic limit nonzero for original moving coefficient, not original dimension survey.");
print("STAGES: normalized roots and unit ratio; limiting determinant; lost-shift control; original comparison only if needed.");
print("FIELD=",modulus," seed=20261006 d=",d," q=",q," alpha=",alpha," upper=",r," lower=",s," N=",N);
for(trial=1,3,
 my(aa=vector(7,i,random(a)));while(#Set(aa)!=7 || prod(i=1,7,aa[i])==0,aa=vector(7,i,random(a)));
 print("POINT trial=",trial," slopes=",aa);
 my(ell=vector(3,i,o+aa[i]*T+O(T^N)),w=apply(sqrt,ell));
 for(i=1,3,assert(polcoef(w[i],0,T)==o && valuation(w[i]^2-ell[i],T)>=N,"root equation"));
 my(G=ell[1]*ell[2]^2*ell[3]^4);
 my(normD=w[1]/(w[2]*w[3])*ell[1]^(d-1)*ell[2]^(2*d-2)*ell[3]^(4*d-8));
 my(normPrev=w[1]/(w[2]*w[3])*ell[1]^(d-2)*ell[2]^(2*d-4)*ell[3]^(4*d-12));
 assert(valuation(normD/normPrev-G,T)>=N && polcoef(G,0,T)==o,"degree-dependent common-unit ratio");
 my(up=List(),low=List(),base=vector(8));
 for(mask=0,7,
  base[mask+1]=prod(i=1,3,ell[i]^exps[mask+1][i]*if(bittest(mask,i-1),w[i],o));
  for(j=0,c,listput(up,base[mask+1]*T^j));
  for(j=0,c-8,listput(low,G*base[mask+1]*T^j));
 );
 up=Vec(up);low=Vec(low);
 assert(#up==r && #low==s && r+s==N && alpha<=r && q>=N,"source/support inventory");
 my(M=jetmatrix(concat(up,apply(f->T^alpha*f,low)),N),t0=getwalltime(),det=matdet(M));
 print("LIMIT trial=",trial," determinant=",det," determinant_ms=",getwalltime()-t0);
 if(!negative,
  my(bad=jetmatrix(concat(up,low),N),badRank=matrank(bad));
  assert(badRank==r,"removing the shift must collapse to the upper space");
  negative=1;print("NEGATIVE lost shift: rank=",badRank," expected=",r);
 );
 if(det!=0,success=1;break);
 print("Limit point failed; compare the actual original moving coefficient at seven roots.");
 my(U=sourceV(aa,d,N),V=sourceV(aa,d-1,N));
 assert(#U==r && #V==s,"original inventory");
 my(original=jetmatrix(concat(U,apply(f->T^alpha*f,V)),N),origdet=matdet(original));
 print("ORIGINAL trial=",trial," determinant=",origdet);
);
print("RESULT limiting_nonzero_certificate=",success," negative_control=",negative);
if(!success,print("No generic vanishing conclusion from these failed specializations."));
print("DONE: stop degree and prime-power enlargement; develop or refute the uniform matching implication.");
}
quit;

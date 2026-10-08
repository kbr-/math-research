\\ Exact original dimension-ten low-degree complements after the paired transfer.
\\ Shared roots and subset products; every coefficient and source column retained.
default(parisizemax,2000000000);
default(nbthreads,1);
p=eval(getenv("BMD_PRIME"));extension=eval(getenv("BMD_EXTENSION"));degrees=eval(getenv("BMD_DEGREES"));
assert(c,s)=if(!c,print("FAIL ",s);quit(1));
assert(isprime(p)&&p>2&&extension>=1,"odd finite field");
modulus=ffinit(p,extension,'a);a=ffgen(modulus,'a);o=a^0;q=p^extension;
assert(q>55,"avoid recorded finite-field degree-two obstruction");
field=vector(q,i,sum(j=0,extension-1,o*((((i-1)\p^j)%p))*a^j));codes=Map();for(i=1,q,mapput(codes,Str(field[i]),i-1));
code(z)=mapget(codes,Str(z+0*o));
source_columns(d)={my(cols=List());for(mask=0,1023,if(hammingweight(mask)<=d,for(j=0,(d-hammingweight(mask))\2,listput(cols,[mask,j]))));return(Vec(cols));};
prefixes(roots,N,maxd)={my(products=vector(1024),co=vector(1024));products[1]=o+O(T^N);co[1]=vector(N,j,if(j==1,o,0*o));for(mask=1,1023,if(hammingweight(mask)<=maxd,my(bit=valuation(mask,2),parent=mask-2^bit);products[mask+1]=products[parent+1]*roots[bit+1];co[mask+1]=vector(N,j,polcoef(products[mask+1],j-1,T))));return(co);};
marked(co,cols,N)=matrix(N,N,i,j,if(i<=cols[j][2],0*o,co[cols[j][1]+1][i-cols[j][2]]));
setrand(eval(getenv("BMD_SEED")));
{my(dims=vector(6,j,sum(s=0,j+1,binomial(10,s)*(1+(j+1-s)\2))),cols=vector(6,j,source_columns(j+1)),remaining=degrees,certified=0,negative=0,Nmax=dims[vecmax(degrees)-1]);
assert(#degrees>0&&vecmin(degrees)>=2&&vecmax(degrees)<=7,"exact finite complement");assert(default(nbthreads)==1,"one library thread");
for(j=1,6,assert(#cols[j]==dims[j],"complete original source count"));
print("FIELD_CODES ",p," ",extension," ",vector(extension+1,j,lift(polcoef(modulus,j-1,'a))));
print("TARGET n=10 degrees=",degrees," dimensions=",dims," max_rows=",Nmax," seed=",getenv("BMD_SEED"));
for(trial=1,2,if(#remaining==0,break);my(labels=vector(10,i,random(a)));while(#Set(labels)!=10||prod(i=1,10,labels[i])==0,labels=vector(10,i,random(a)));
my(ell=vector(10,i,o+labels[i]*T+O(T^Nmax)),roots=apply(sqrt,ell));for(i=1,10,assert(polcoef(roots[i],0,T)==o&&valuation(roots[i]^2-ell[i],T)>=Nmax,"normalized root identity"));
my(co=prefixes(roots,Nmax,vecmax(degrees)),pending=List());print("POINT_CODES trial=",trial," labels=",apply(code,labels));
for(j=1,#remaining,my(d=remaining[j],N=dims[d-1],t0=getwalltime());print("DETERMINANT_STARTED d=",d," N=",N);my(v=matdet(marked(co,cols[d-1],N)));print("MATRIX_TIME d=",d," ms=",getwalltime()-t0);
if(v==0,listput(pending,d);print("UNRESOLVED_AT_POINT d=",d),certified++;print("CERTIFIED d=",d," N=",N," determinant_code=",code(v))));
if(!negative,my(d=vecmin(degrees),N=dims[d-1],bad=roots);bad[10]=bad[9];assert(matdet(marked(prefixes(bad,N,d),cols[d-1],N))==0,"repeated-root negative control");negative=1;print("NEGATIVE_CONTROL d=",d," repeated_root_zero=true"));
remaining=Vec(pending));
assert(certified+#remaining==#degrees&&negative,"complete accounting");
print("LOW_FIELD_FINISHED prime=",p," certified=",certified," remaining=",remaining);
}
quit;

\\ Exact sufficient joint-leading filter for the n9/n10 finite complements.
\\ n9 uses proved n<=8 normality; n10 is conditional on the completed n9 result.
\\ A positive valuation leaves a case unresolved by this filter, not an exception.
default(parisizemax,1000000000);
default(nbthreads,1);
p=eval(getenv("BMD_PRIME"));out=getenv("BMD_OUT");
assert(c,s)=if(!c,print("FAIL ",s);quit(1));
assert(isprime(p)&&p>2&&p<=97,"reviewed odd-prime grid");
N(n,d)=sum(k=0,min(n,d),binomial(n,k)*(1+(d-k)\2));
cat(j)=binomial(2*j,j)/(j+1);
vfact(n,pp)={my(v=0,q=pp);while(q<=n,v+=n\q;q*=pp);return(v);};
vH(s,h,pp)=sum(i=1,h-1,vfact(2*s+i+h-1,pp)-vfact(2*s+2*i-1,pp)+vfact(2*i-1,pp)-vfact(i+h-1,pp));
{my(controls=0);for(s=0,4,for(h=0,8,my(H=1);for(i=1,h-1,for(j=i,h-1,H*= (2*s+i+j)/(i+j)));assert(denominator(H)==1,"integral product control");forprime(pp=3,31,assert(vH(s,h,pp)==valuation(H,pp),"factorial valuation equals exact product");controls++)));
assert(vH(2,2,3)==1&&vH(4,4,7)==1,"nonunit negative controls");print("CONTROLS exact_product_valuation=",controls," nonunit_negatives=true");}
{my(needed=vector(2),saved=0);
for(n=9,10,my(top=if(n==9,6,7),degrees=List(),oneunit=prod(j=0,n-2,if(valuation(cat(j),p)==0,1,0)));
for(d=2,top,my(r=N(n-1,d),s=N(n-1,d-1),h=r-s,v=vH(s,h,p),parents=(d>=3||oneunit));assert(v>=0,"nonnegative integral valuation");
my(covered=(v==0&&parents));if(covered,saved++,listput(degrees,d));print("FILTER n=",n," p=",p," d=",d," r=",r," s=",s," h=",h," valuation=",v," lower_degree_one_unit=",oneunit," sufficient=",covered));
needed[n-8]=Vec(degrees));
write(out,"FILTER_PRIME=",p,";DIRECT_DEGREES=",needed,";ASSUMES_N9_COMPLETE=1;");
print("COMPLETE direct_degrees_n9_n10=",needed," skipped_by_existing_identity=",saved," assumes_n9_complete_for_n10=true");}
quit;

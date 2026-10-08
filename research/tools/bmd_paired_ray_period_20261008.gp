\\ Exact finite-field input for a full-cut periodic paired-source test.
default(parisizemax,2500000000);
default(nbthreads,1);
a=ffgen(Mod(1,3)*(x^2+1),'a); o=a^0;
field=vector(9,i,o*((i-1)%3)+a*((i-1)\3));
code(z)={for(i=1,9,if(z==field[i],return(i-1)));error("field code");};
chi(z)=if(z==0,0,if(z^4==o,1,-1));
quotientcount(sl,mask)={my(P=o,degree=hammingweight(mask));for(i=1,4,if(bittest(mask,i-1),P*=o+sl[i]*T));my(n=if(degree%2,1,1+chi(pollead(P))));for(j=1,9,n+=1+chi(subst(P,T,field[j])));return(n);};
best=10^9; hist=Map(); chosen=[]; counts=[]; tested=0;
{for(i=2,6,for(j=i+1,7,for(k=j+1,8,for(l=k+1,9,
 my(sl=[field[i],field[j],field[k],field[l]], ns=vector(5), ex=1, z=0);
 for(mask=0,15,if(hammingweight(mask)>=3,z++;ns[z]=quotientcount(sl,mask);if(ns[z]%4,error("rational two torsion"));ex=lcm(ex,ns[z]/2)));
 tested++;my(bound=8*ex);if(bound<best,best=bound;chosen=sl;counts=ns);
 print("SLOPES ",apply(code,sl)," elliptic_orders ",ns," jacobian_exponent_bound ",bound);
))));}
if(tested!=70 || #chosen!=4,error("incomplete input enumeration"));
print("BEST ",apply(code,chosen)," orders ",counts," exponent_bound ",best);
print("COMPLETE 70 separated four-root inputs; five complete quotient point counts each.");

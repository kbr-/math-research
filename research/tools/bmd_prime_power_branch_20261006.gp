\\ Arithmetic control for the actual joint-leading coefficient.
\\ Prediction: h=64, P the first p-power >126, d=3+P gives H_s^(h)=1 mod p.
\\ The proof, not these controls, treats all odd primes and all progression degrees.
default(parisizemax, 500000000);
default(nbthreads,1);
if(default(nbthreads)!=1,error("thread control"));
Hvalue(h,s)={my(num=1,den=1);for(i=1,h-1,for(j=i,h-1,num*=2*s+i+j;den*=i+j));if(num%den,error("nonintegral Catalan product"));num/den};
profile(h,s,p)={my(r=s+h,N=r+s,q=p,ok=1,levels=0);while(q<=2*r,my(c=vector(q));for(j=0,r-1,c[(2*j)%q+1]++);for(j=0,s-1,c[(2*j+1)%q+1]++);if(vecmax(c)-vecmin(c)>1,ok=0);levels++;q*=p);[ok,levels]};
{
my(h=64, primes=[3,5,7,127,131],positive=0);
print("Stages: exact 2016-factor integer product; independent branch-residue counts; bad-degree control.");
print("No original large Hasse matrices are constructed.");
for(k=1,#primes,
 my(p=primes[k],P=p);while(P<=126,P*=p);
 my(d=3+P,s=64*(d-3),H=Hvalue(h,s),pr=profile(h,s,p));
 if(valuation(H,p)!=0 || lift(Mod(H,p))!=1 || pr[1]!=1,error("positive prediction failed"));
 print("p=",p," P=",P," d=",d," N=",2*s+h," vp(H)=",valuation(H,p)," H_mod_p=",lift(Mod(H,p))," balanced_levels=",pr[2]);
 positive++;
);
my(d=6,s=64*(d-3),H=Hvalue(h,s),pr=profile(h,s,3));
if(valuation(H,3)==0 || pr[1]!=0,error("bad-degree control not detected"));
print("negative p=3 d=6 N=",2*s+h," vp(H)=",valuation(H,3)," balanced=",pr[1]);
print("PASS: ",positive," unit controls and one failed-certificate control; no claim that failure is nonnormality.");
}
quit;

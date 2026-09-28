\\ Symbolic exponent control of a proved general double-Saalschutz identity.
\\ Uses only the existing m=r=3 face; no new dimension or degree series.
\\ Rational function arithmetic in al and polynomial arithmetic in x use PARI.
u='u; x='x; al='al;
poch(a,n)=prod(k=0,n-1,a+k);
m=3; r=3; be=al-m+1;
gam(j)=(-1)^j*poch(al,j)/j!;
hh(j)=sum(a=0,j,gam(a)*gam(j-a)*x^a);
ff(j)=(-1)^j*j!/poch(be,j)*hh(j);
ll=(u-1)^m*(u-x)^m;
zz=sum(k=0,2*m,polcoef(ll,k,u)*ff(r+k));
kk=poch(1-al,m)*poch(al,m)/(poch(-r-al,m)*poch(r+al+1,m));
if(zz-kk*x^m*ff(r)!=0,error("double-Saalschutz identity failed"));
print("Symbolic exponent alpha, m=r=3: finite-difference identity exact.");
print("K(alpha)=",kk);
hr=hh(r);
ode=x*(1-x)*deriv(deriv(hr,x),x)+(1-al-r-(1+al-r)*x)*deriv(hr,x)+r*al*hr;
if(ode!=0,error("hypergeometric ODE failed"));
print("Symbolic exponent alpha: hypergeometric ODE exact.");
hp=subst(hr,al,3/2); hp=hp/pollead(hp,x);
if(hp!=(x+1)*(7*x^2+2*x+7)/7,error("archived face mismatch"));
print("At alpha=3/2 the noncollision factor is ",hp);
print("K(3/2)=",subst(kk,al,3/2));
print("No additional face size or determinant computation was run.");
quit;

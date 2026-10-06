\\ Actual centered last-pair family: full-span controls and characteristic-safe Catalan coefficients.
\\ The four controls test one failed boundary and two other source encodings, not a degree survey.
default(parisizemax,3000000000);
default(nbthreads,1);
setrand(20261006);
w;T;X;
assert(c,s)={if(!c,error(s));};
catcoef(lam,j)=if(j==0,1,binomial(lam+2*j-1,j)-binomial(lam+2*j-1,j-1));
{
my(cases=[[0,2,5],[1,6,3],[1,3,5],[2,5,7]],total=0);
for(ci=1,#cases,
 my(m=cases[ci][1],d=cases[ci][2],pp=cases[ci][3],h=2^m,c=h*(d-m+1)-1,b=2*h-1,C=2*c-b,A=c-b,N=2*h*(C+1),L=N+8,ext=1);
 assert(A>=0,"balanced even core");while(pp^ext<4096,ext++);
 my(modulus=ffinit(pp,ext,'a),aa=ffgen(modulus,'a),o=aa^0,slopes=vector(m,i,random(aa)),center=random(aa),delta=random(aa));
 while(delta==0 || #Set(concat(slopes,[center,center-delta/2,center+delta/2]))!=m+3 || prod(j=1,m,slopes[j])*center*(center-delta/2)*(center+delta/2)==0,
  slopes=vector(m,i,random(aa));center=random(aa);delta=random(aa));
 my(ell=o+center*T+O(T^L),v0=sqrt(ell),vm=sqrt(o+(center-delta/2)*T+O(T^L)),vp=sqrt(o+(center+delta/2)*T+O(T^L)),oldell=vector(m,i,o+slopes[i]*T+O(T^L)),oldroots=apply(sqrt,oldell));
 assert(valuation(vm^2-(o+(center-delta/2)*T),T)>=L && valuation(vp^2-(o+(center+delta/2)*T),T)>=L && valuation(v0^2-ell,T)>=L,"three new square-root equations");
 for(i=1,m,assert(valuation(oldroots[i]^2-oldell[i],T)>=L,"old square-root equations"));
 my(G=prod(i=1,m,oldell[i]^(2^(i-1))),tau=T/ell,z=vm*vp/ell,r=(vm+vp)/(2*v0),theta=tau/r^2,chi=tau^2/r^2,g=(o-center*tau)*prod(i=1,m,(o+(slopes[i]-center)*tau)^(2^i)),orig=List(),lift=List());
 assert(valuation(z^2-(1-delta^2*tau^2/4),T)>=L && valuation(r^2-(1+z)/2,T)>=L,"centered root identities");
 assert(valuation(chi-8*(1-z)/delta^2,T)>=L,"normalized even core coordinate");
 for(mask=0,h-1,
  my(pref=o+O(T^L));for(j=1,m,if(bittest(mask,j-1),pref*=oldroots[j]^(2^j-1),for(i=1,j-1,pref*=oldell[i]^(2^(i-1)))));
  for(j=0,c,listput(orig,pref*v0^C*T^j));
  for(j=0,c-h,listput(orig,pref*v0^C*vm*G*T^j);listput(orig,pref*v0^C*vp*G*T^j));
  for(j=0,c-2*h,listput(orig,pref*v0^C*vm*vp*G^2*T^j));
  for(j=0,b-1,listput(lift,pref*v0^b*ell^C*tau^j));
  for(e=0,2*A,listput(lift,pref*v0^b*ell^C*g*tau^(e%2)*chi^(e\2)));
  for(e=0,C,listput(lift,pref*G*ell^C*r^C*theta^e));
 );
 assert(#orig==N && #lift==N,"all original and saturated columns");
 my(OM=matrix(L,N,i,j,polcoef(orig[j],i-1,T)),LM=matrix(L,N,i,j,polcoef(lift[j],i-1,T)),ro=matrank(OM),rl=matrank(LM),rj=matrank(matconcat([OM,LM])));
 assert(ro==N && rl==N && rj==N,"exact full original/source-frame span equality");
 print("SOURCE m=",m," d=",d," p=",pp," c=",c," b=",b," C=",C," N=",N," rows=",L," ranks=",[ro,rl,rj]);
 print("FIELD=",modulus," old_slopes=",slopes," center=",center," delta=",delta);
 my(zs=sqrt(Mod(1,pp)-w*X^2/4+O(w^(pp+2))),rs=sqrt((1+zs)/2),chis=X^2/rs^2,thetas=X/rs^2);
 for(e=0,2*A,
  my(series=X^(e%2)*chis^(e\2));
  for(j=0,pp+1,my(cc=catcoef(e\2,j));assert(denominator(cc)==2^valuation(denominator(cc),2),"dyadic Catalan coefficient");assert(polcoef(series,j,w)==Mod(cc/16^j,pp)*X^(e+2*j),"even all-order coefficient");total++);
 );
 for(e=0,C,
  my(series=rs^C*thetas^e);
  for(j=0,pp+1,my(cc=catcoef(e-C/2,j));assert(denominator(cc)==2^valuation(denominator(cc),2),"dyadic half-integer Catalan coefficient");assert(polcoef(series,j,w)==Mod(cc/16^j,pp)*X^(e+2*j),"odd all-order coefficient");total++);
 );
 for(j=1,pp-1,assert(Mod(catcoef(pp,j),pp)==0 && Mod(catcoef(pp/2,j),pp)==0,"Frobenius delay beforep"));
 assert(Mod(catcoef(pp,pp),pp)==1 && Mod(catcoef(pp/2,pp),pp)==Mod(1/2,pp),"first Frobenius coefficient");
 print("PASS centered full-frame identities and coefficient checks through q-order",pp+1);
);
print("PASS all4 full source-span controls and",total," exact Catalan coefficient comparisons.");
}
quit;

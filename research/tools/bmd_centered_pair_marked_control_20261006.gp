\\ Independent full marked map at the smallest ternary pure-power boundary.
\\ Uses the centered frame itself; no five-cut formulas or pole-removal calculation.
default(parisizemax,1000000000);
default(nbthreads,1);
setrand(20261006);
T;
assert(c,s)={if(!c,error(s));};
{
my(pp=3,q=81,N=80,C=19,M=42,L=82,modulus=ffinit(pp,8,'a),a=ffgen(modulus,'a),o=a^0,u=a,ac=u^2/(u^2-1)^2,ao=u^2/(u^2+1)^2,zpower=u^q);
assert(u!=0 && u^2!=1 && u^2!=-1 && ac!=ao,"admissible generic-curve control point");
my(ell=o+ac*T+O(T^L),oldell=o+ao*T+O(T^L),v=sqrt(ell),old=sqrt(oldell),tau=T/ell,g=(1-ac*tau)*(1+(ao-ac)*tau)^2,base=List(),first=List());
assert(valuation(v^2-ell,T)>=L && valuation(old^2-oldell,T)>=L,"normalized roots");
for(ch=0,1,
 my(pref=old^ch);
 for(j=0,2,listput(base,pref*v^3*ell^C*tau^j);listput(first,0*o+O(T^L)));
 for(e=0,16,listput(base,pref*v^3*ell^C*g*tau^e);listput(first,pref*v^3*ell^C*g*(o*(e\2)/16)*tau^(e+2)));
 for(e=0,C,listput(base,pref*oldell*ell^C*tau^e);listput(first,pref*oldell*ell^C*(o*(2*e-C)/32)*tau^(e+2)));
);
assert(#base==N && #first==N,"complete centered frame");
my(J0=matrix(N,N,i,j,polcoef(base[j],i-1,T)),J1=matrix(N,N,i,j,polcoef(first[j],i-1,T)),right=matker(J0),left=matker(J0~));
assert(matrank(J0)==79 && matsize(right)[2]==1 && matsize(left)[2]==1,"exact boundary corank1");
my(f=sum(j=1,N,right[j,1]*base[j]),value=(left~*J1*right)[1,1]);
assert(valuation(f,T)==81,"exact extra order of the boundary kernel");assert(value!=0,"nonzero actual centered first coefficient");
my(omega=-(u^2-1)^8*((u^2+1)*(zpower^4+1)+u*zpower*(zpower^2+1))/(u^8*(zpower^2-1)));
assert(omega!=0,"symbolic five-cut scalar also survives this point");
print("FIELD=",modulus," u=",u," old_slope=",ao," center_slope=",ac);
print("FULL_MARKED_RANK=79 OF80;KERNEL_ORDER=81;CENTERED_SCALAR=",value);
print("FIVE_CUT_SCALAR=",omega," (different cokernel normalization)");
print("PASS full original-frame kernel and nonzero first q=delta2 induced coefficient.");
}
quit;

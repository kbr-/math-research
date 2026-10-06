\\ Exact exceptional primes of the joint leading coefficient for n8,d2..5.
\\ Lower n7 degree>=2 is proved at every odd prime; degree1 needs p>=13.
default(parisizemax,1000000000);
default(nbthreads,1);
assert(c,s)={if(!c,error(s));};
N(n,d)=sum(k=0,min(n,d),binomial(n,k)*(1+(d-k)\2));
{
my(inventory=vector(4),total=0,allp=[]);
for(d=2,5,
 my(r=N(7,d),s=N(7,d-1),h=r-s,H=1);
 for(i=1,h-1,for(j=i,h-1,H=H*(2*s+i+j)/(i+j)));
 assert(denominator(H)==1,"integral Hankel product");
 my(fa=factor(H),back=prod(j=1,matsize(fa)[1],fa[j,1]^fa[j,2]));assert(back==H,"complete factor reconstruction");
 my(pp=select(p->p>=7,Vec(fa[,1])));if(d==2,pp=Set(concat(pp,[7,11])));
 inventory[d-1]=pp;total+=#pp;allp=Set(concat(allp,pp));
 print("DEGREE=",d," r=",r," s=",s," h=",h," dimension=",N(8,d));
 print("HANKEL_INTEGER=",H);print("FACTORIZATION=",fa);print("REMAINING_PRIMES=",pp," COUNT=",#pp);
);
write("research/results/bmd-eight-low-complement-20261006/inventory.gp","LOW_PRIMES=",inventory,";EXPECTED_TOTAL=",total,";ALL_PRIMES=",allp,";");
print("TOTAL remaining prime-degree pairs=",total," distinct primes=",#allp," maximum prime=",allp[#allp]);
print("PASS complete integral factorization; p3,p5 already proved; degree-one lower exceptions7,11 explicitly included.");
}
quit;

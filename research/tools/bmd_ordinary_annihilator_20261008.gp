\\ Compute an explicit annihilator for the already fixed ordinary n9/F_(3^8) curve.
\\ Need: 256*lcm of all466 positive-genus quotient Jacobian orders kills A0.
\\ Stages: seven measured quotient sizes; permit full inventory only if estimate<=60s;
\\ all Frobenius functional equations; direct Fq point counts on the seven size controls.
default(parisizemax,1500000000);
default(nbthreads,1);
assert(c,s)={if(!c,error(s));};
{
my(start=getwalltime(),q=6561,modulus=ffinit(3,8,'a),a=ffgen(modulus,'a),one=a^0,lc=[508,5690,5164,3098,2894,6147,276,4463,174],labels=apply(c->sum(j=0,7,(c\3^j)%3*a^j),lc),polys=vector(512),cache=Map(),estimate=0);
for(S=0,511,polys[S+1]=prod(i=1,9,if(bittest(S,i-1),one+labels[i]*T,one)));
for(m=3,9,
 my(S=2^m-1,ts=getwalltime(),cp=hyperellcharpoly(polys[S+1]),ms=max(1,getwalltime()-ts));
 mapput(cache,S,cp);estimate+=binomial(9,m)*ms;
 print("SIZE_CONTROL branches=",m," genus=",(m-1)\2," wall_ms=",ms)
);
print("COUNT_ESTIMATE_MS=",estimate," budget_ms=60000");
assert(estimate<=60000,"measured inventory estimate exceeds budget");
my(E=1,count=0,field=vector(q,j,sum(k=0,7,((j-1)\3^k)%3*a^k)),tracechecks=0);
for(S=1,511,my(m=hammingweight(S),g=(m-1)\2);if(g>0,
 my(cp);if(mapisdefined(cache,S),cp=mapget(cache,S),cp=hyperellcharpoly(polys[S+1]));
 assert(poldegree(cp)==2*g,"Frobenius degree");
 for(j=0,g,assert(polcoef(cp,j)==q^(g-j)*polcoef(cp,2*g-j),"Frobenius functional equation"));
 if(mapisdefined(cache,S),
  my(points=q+if(m%2,1,if(pollead(polys[S+1])^((q-1)/2)==one,2,0)));
  for(j=1,q,my(v=subst(polys[S+1],T,field[j]));if(v!=0,points+=if(v^((q-1)/2)==one,1,-1)));
  assert(points==q+1+polcoef(cp,2*g-1),"independent Fq trace count");tracechecks++
 );
 my(order=subst(cp,variable(cp),1));assert(order>0,"positive order");E=lcm(E,order);count++;
 print("ORDINARY_QUOTIENT subset=",S," genus=",g," order=",order," polynomial=",cp);
 assert(getwalltime()-start<90000,"measured count budget exceeded")
));
my(M=256*E,v=valuation(M,3),m=M/3^v,L=8*9*lcm(vector(4,j,q^j-1)),polebound=256*(4*256+18*sum(j=0,255,j)));
assert(count==466 && tracechecks==7,"complete quotient inventory");
assert(L%8==0 && L>v && L>18,"s4+L exceeds annihilator and pole-bound thresholds");
print("ANNIHILATOR_CONSTANTS M=",M," v3=",v," prime_to_three=",m," Cartier_period=",L," pole_bound=",polebound);
print("ORDINARY_ANNIHILATOR_COMPLETED quotients=",count," trace_controls=",tracechecks," wall_ms=",getwalltime()-start);
}
quit;

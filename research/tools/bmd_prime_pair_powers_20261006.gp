\\ Exhaustive coefficient audit of the all-parameter prime-block identity
\\ at small primes, plus the generic cubic multiplicity-count control.
default(parisizemax, 200000000);
bmd_assert(x,s)=if(!x,error(s));
bmd_verify()={
  my(primes=[3,5,7,11,23],count=0,p,m,beta,lhs,rhs,scale,j,profiles,ids,cond,forms,weights,identity,counts=List());
  for(v=1,#primes,
    p=primes[v];m=(p-3)/2;beta=vector(p,t,Mod(binomial(1/2,t-1),p));
    for(j=0,2*m,
      scale=Mod(-1/8,p)*(-1)^j/Mod(binomial(2*m,j),p);
      lhs=(X-Y)^2*scale*sum(i=max(0,j-m),min(m,j),binomial(m,i)*binomial(m,j-i)*X^i*Y^(j-i));
      rhs=sum(i=0,j+2,beta[i+1]*beta[j+3-i]*X^i*Y^(j+2-i));
      bmd_assert(lhs==rhs,"pair-power identity");
      count++;
    );
    print("prime=",p," all_columns=",2*m+1," PASS");
  );
  forms=[x-a,x-b,x-c];weights=[b-c,c-a,a-b];
  identity=sum(i=1,3,weights[i]^3*forms[i]^3)-3*prod(i=1,3,weights[i])*prod(i=1,3,forms[i]);
  bmd_assert(identity==0,"generic cubic dependence");
  profiles=[[3,0,0],[0,3,0],[0,0,3],[1,1,1]];
  for(mask=1,15,
    ids=select(i->bittest(mask,i-1),vector(4,i,i));
    cond=#ids+sum(col=1,3,vecmin(vector(#ids,j,profiles[ids[j]][col])));
    bmd_assert(cond<=4,"multiplicity-count condition");
    listput(counts,[mask,cond]);
  );
  print("pair_power_columns_checked=",count);
  print("generic_cubic_identity=",identity);
  print("all_nonempty_subset_counts=",Vec(counts));
  print("PASS: full coefficient identities and all15 multiplicity conditions");
};
bmd_verify();
quit;

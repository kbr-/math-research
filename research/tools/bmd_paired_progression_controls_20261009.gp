\\ Exact controls for the all-pair ordinary-merge progression; no original-degree grid.
default(parisizemax,1000000000);
default(nbthreads,1);
assert(c,s)=if(!c,print("FAIL ",s);quit(1));
binompoly(t,k)=prod(j=0,k-1,t-j)/k!;
identityCount=0;unitCount=0;sourceCount=0;
{for(g=1,8,my(A=matrix(g,g,i,j,binompoly(z-j+1,2*i-1)),lhs=matdet(A),coef=(-1)^(g*(g-1)/2)*2^(g*(g-1)/2)*prod(j=1,g-1,j!)/prod(i=0,g-1,(2*i+1)!),rhs=coef*prod(i=0,g-1,prod(j=i,g-1,z-i-j)));assert(lhs==rhs,"general Pascal product identity");assert(subst(lhs,z,-1)==(-1)^g*2^(g*(g-1)/2),"dyadic unit at minus one");identityCount++);}
{for(m=2,6,my(g=2^(m-1)-1);forprime(p=3,17,my(P=p);while(P<=2*g-1,P*=p);for(t=1,2,my(c=t*P-1,q=2*c+1,A=matrix(g,g,i,j,Mod(binomial(q-j+1,2*i-1),p)),B=matrix(g,g,i,j,Mod(binomial(-j,2*i-1),p)));assert(A==B,"every Lucas-periodic entry");assert(matdet(A)==Mod((-1)^g*2^(g*(g-1)/2),p),"ordinary pivot is a unit");unitCount++;
if(m<=4&&p<=7&&t==1,my(exponents=concat(vector(c+1,j,2*(j-1)),vector(c-g+1,j,2*g+1+2*(j-1))),dim=#exponents,J=matrix(dim,dim,i,j,Mod(binomial(exponents[j],i-1),p)));assert(matdet(J)!=0,"actual full monomial source jet determinant");sourceCount++);
)));}
assert(Mod(binomial(39,1),3)==0,"known dimension-five ternary failure excluded by unit hypothesis");
assert(Mod(binomial(23,1),7)!=0,"known septenary normal control retained");
assert(identityCount==8&&unitCount==60&&sourceCount==9,"all planned controls complete");
print("COMPLETE product_identities=",identityCount," all_pair_unit_cases=",unitCount," full_source_jet_controls=",sourceCount," known_failure_hypothesis_checked=true");
quit;

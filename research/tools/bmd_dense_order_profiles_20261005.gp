\\ Test the general dense p-closed profile construction at its smallest target N=80.
\\ All odd primes <=N+23, every order/omission pair, exact binomial arithmetic.
assert(c,s)={if(!c,error(s));};
{
my(N=80,A=N/2+8,cap=N+23,cases=vector(4),count=0);
forprime(p=3,cap,
 my(q=1,a,b,kind,removed,added);
 if(p>N,kind=1;removed=N-1;added=p,
   while(q*p<=N,q*=p);a=N\q;b=N%q;
   if(b==q-1,kind=2;removed=N-1;added=N+1,
     if(a>=2 || q>=A,kind=3;removed=a*q-1;added=N,
       kind=4;removed=N-1;added=2*q
     )
   )
 );
 my(S=if(kind==3,select(x->x!=removed,vector(N+1,i,i-1)),concat(vector(N-1,i,i-1),[added])));
 assert(#S==N && vecmax(S)<=cap && vecmax(S)>=N,"size/pole/nonclassical");
 assert(removed>=A,"prefix lost");
 my(present=vector(cap+1,i,setsearch(Set(S),i-1)!=0));
 for(i=1,#S,for(j=0,S[i],if(!present[j+1],assert(binomial(S[i],j)%p==0,"not p-closed"))));
 cases[kind]++;count++;
 print("p=",p," case=",kind," q=",q," a=",a," b=",b," removed=",removed," added=",added," max=",vecmax(S)," prefix=0..",A-1," PASS");
);
assert(count==26 && vecmin(cases)>0,"branch coverage");
print("PASS: ",count," primes; case counts=",cases,"; every required binomial zero checked");
print("Above-bound negative control: p=107, every 0<=j<=s<=103 has nonzero binomial coefficient");
for(s=0,cap,for(j=0,s,assert(binomial(s,j)%107!=0,"large-prime control")));
print("PASS: at p=107 a p-closed set within the pole cap must be an initial segment");
}
quit;

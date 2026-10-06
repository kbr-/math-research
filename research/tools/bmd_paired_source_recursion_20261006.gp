\\ Structural controls for the all-parameter paired-source induction; no new normality samples.
default(nbthreads,1);
assert(c,s)={if(!c,error(s));};
N(n,d)=sum(k=0,min(n,d),binomial(n,k)*(1+(d-k)\2));
{
my(checked=0,old7=[[2,2,0],[2,2,0],[1,3,0],[1,3,0],[1,0,3],[1,0,3],[0,1,3],[0,1,3]]);
for(m=1,6,
 my(h=2^m,tt=h-m-1,d=2*m-1,c=h*(d-m+1)-1,oddhigh=0,evenhigh=0,chars=List());
 for(mask=0,h-1,
  my(eps=vector(m,i,bittest(mask,i-1)),raw=vector(m,i,0));
  raw[1]+=eps[1];
  for(j=2,m,if(eps[j],raw[j]+=2^j-1,for(i=1,j-1,raw[i]+=2^i)));
  my(gex=vector(m,i,(raw[i]-eps[i])/2),closed=vector(m,i,(2^(i-1)-1)*eps[i]+2^(i-1)*sum(j=i+1,m,1-eps[j])));
  assert(gex==closed && vecsum(gex)==tt,"closed source divisors and common degree");
  assert(vector(m,i,raw[i]%2)==eps,"independent actual characters");listput(chars,eps);
  oddhigh+=(m-hammingweight(mask))\2;evenhigh+=m-hammingweight(mask);
  if(m==3,assert(gex==old7[mask+1],"existing complete dimension-seven table"));
  checked++;
 );
 assert(#Set(Vec(chars))==h,"all character directions retained");
 my(Co=h*tt+oddhigh,Ce=2*h*tt+h*(h-1)+evenhigh,Mo=2*(c+tt)+m);
 assert(Co==4^m-(3*m+5)*2^(m-2) && Ce==3*4^m-3*(m+2)*2^(m-1),"complete finite and high codimensions");
 assert(h*(c+1)==N(2*m+1,d),"odd original endpoint dimension");
 my(de=2*m,ce=h*(de-m+1)-1);assert(h*(2*ce-h+2)==N(2*m+2,de),"even original endpoint dimension");
 assert(2*c-(2*h-1)==2*h*(d-m)-1,"next polynomial bound");
 print("m=",m," characters=",h," divisor_degree=",tt," odd_cut_count=",Co," even_cut_count=",Ce," odd_endpoint_dimension=",N(2*m+1,d)," even_endpoint_dimension=",N(2*m+2,de));
);
assert(checked==126,"complete character controls through six pairs");
print("PASS126 exact character/divisor comparisons, both endpoint counts and cut codimensions, and the full existing dimension-seven table.");
}
quit;

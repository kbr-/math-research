\\ Independent encoding control for lem:cube-six-paired-criterion.
\\ d=4 only: compare direct Z_d + w5 Z_(d-1) Hasse kernel with
\\ ambient 24 conditions and the nonprincipal 20-row elimination.
\\ Exact finite fields, seed fixed; no normality extrapolation.
default(parisizemax, 1000000000);
setrand(20261005);
OUT=getenv("OUT"); if(OUT==0 || OUT=="",error("OUT required"));
emit(s)={print(s);write(OUT,s);};
assert(c,s)={if(!c,error(s));};
{
my(d=4,N=32*d-48,M=8*d-6,m=M-6,exps=[[1,0],[1,0],[0,1],[0,1],[2,2],[2,2],[1,3],[1,3]]);
emit(Str("seed=20261005 d=",d," N=",N," M=",M," field sizes >=100000; one admissible triple per prime"));
forprime(p=3,7,
  my(e=ceil(log(100000)/log(p)),g=ffgen(p^e,'a),o=g^0,aa=vector(3,i,random(g)));
  while(#Set(aa)!=3 || prod(i=1,3,aa[i])==0,aa=vector(3,i,random(g)));
  my(ll=vector(3,i,o+aa[i]*T+O(T^(N+1))),ww=apply(sqrt,ll),raw=List());
  for(block=0,1,
    my(j=d-block,base=ll[1]^(1-j)*ll[2]^(2-2*j)*if(block,ww[3],o));
    my(shapes=[ll[2]^2,ww[2]*ll[1],ww[1]/ll[1]*ll[2]^2,ww[1]*ww[2]]);
    for(s=1,4,for(t=0,4*j-5,listput(raw,base*shapes[s]*T^t)));
  );
  assert(#raw==N,"raw dimension count");
  my(D=matrix(N,N,i,j,polcoef(raw[i],j-1,T)),rawcor=N-matrank(D));
  my(chars=vector(8,s,prod(j=1,3,if(bittest(s-1,j-1),ww[j],o))),cols=List(),top=List(),omit=List());
  for(s=0,7,
    my(w=hammingweight(s),bound=(M-w)\2);
    for(j=0,bound,
      listput(cols,[s,j]);
      if(w+2*j>m,listput(top,#cols));
      if(j==bound && (s==0 || s==4 || s==5 || s==6),listput(omit,#cols));
    );
  );
  my(Amb=matrix(N,#cols,i,j,polcoef(chars[cols[j][1]+1]*T^cols[j][2],i-1,T)),K=matker(Amb));
  assert(#cols==104 && #K==24 && #top==24 && #omit==4,"ambient/kernel count");
  my(Phi=matrix(24,#cols,i,j,0*o),r=4);
  for(i=1,4,Phi[i,omit[i]]=o);
  for(s=0,7,for(node=1,2,for(k=0,exps[s+1][node]-1,
    r++;my(x=-1/aa[node]);
    for(j=1,#cols,if(cols[j][1]==s && cols[j][2]>=k,Phi[r,j]=binomial(cols[j][2],k)*x^(cols[j][2]-k)));
  )));
  assert(r==24 && matrank(Phi)==24,"24 independent conditions");
  my(cor24=24-matrank(Phi*K));assert(cor24==rawcor,"raw vs 24 corank mismatch");
  my(Top=matrix(24,24,i,j,K[top[i],j]));assert(matrank(Top)==24,"sample is principal: 20 reduction unavailable");
  my(C=K*Top^-1,free=select(i -> !setsearch(Set(Vec(omit)),top[i]),vector(24,i,i)));
  assert(#free==20,"free count");
  my(PC=Phi*C,small=matrix(20,20,i,j,PC[i+4,free[j]]),cor20=20-matrank(small));
  assert(cor20==rawcor,"raw vs 20 corank mismatch");
  \\ Independent table-to-ambient kernel check and unit-normalized direct rows.
  my(Y=List(),norm=ww[1]/ww[2]*ll[1]^(d-1)*ll[2]^(2*d-2));
  for(s=0,7,
    my(poly=(o+aa[1]*T)^exps[s+1][1]*(o+aa[2]*T)^exps[s+1][2]);
    for(j=0,4*d-5-if(s>=4,4,0),
      listput(Y,vector(#cols,k,if(cols[k][1]==s,polcoef(poly*T^j,cols[k][2],T),0*o))~);
    );
  );
  my(YM=Mat(Vec(Y)));assert(matrank(YM)==N && Phi*YM==matrix(24,N),"table kernel mismatch");
  my(NormRaw=matrix(N,N,i,j,polcoef(raw[i]*norm,j-1,T)),Table=Amb*YM);
  assert(matrank(matconcat([NormRaw~ ,Table]))==matrank(Table),"direct normalized span mismatch");
  emit(Str("p=",p," e=",e," slopes=",aa," raw_rank=",N-rawcor," phi_rank=24 marked_rank=",24-cor24," top_rank=24 reduced_rank=",20-cor20," table/direct span PASS"));
);
emit("PASS: all three independent encoding controls; no all-degree nonvanishing inferred.");
}
quit;

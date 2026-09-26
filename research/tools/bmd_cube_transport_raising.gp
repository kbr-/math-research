\\ Check the proposed order-raising encoding, not a finite threshold sweep.
\\ For every row of n=1..5,d=0..4 and coefficients c=0..12, verify
\\ D f_c = (sum r_i a_i/2) f_c - (c+1) f_(c+1) + q (T^(q-1)w^r)_c
\\ over Z[1/2][a,b,c,e,g], with D=sum a_i^2 partial_ai.
\\ Shared series through order 13 give every truncation m<=12.
\\ Also test a nonzero marked kernel vector and the p=3 excluded step.
T='T; AV=['a,'b,'c,'e,'g]; M=12;
WW=vector(5,i,sqrt(1+AV[i]*T+O(T^(M+2))));
DD(f,n)=sum(i=1,n,AV[i]^2*deriv(f,AV[i]));
{
  my(rows=0,checks=0,lowercontrols=0,shiftcontrols=0);
  for(n=1,5,for(d=0,4,
    my(nrows=0);
    for(mask=0,2^n-1,
      my(w=hammingweight(mask),f=1,L=0);
      if(w>d,next);
      for(i=1,n,if(bittest(mask,i-1),f*=WW[i];L+=AV[i]/2));
      for(q=0,(d-w)\2,
        my(g=f*T^q); rows++; nrows++;
        for(c=0,M,
          my(fc=polcoef(g,c,T),fn=polcoef(g,c+1,T),
             low=if(q,q*polcoef(f*T^(q-1),c,T),0),lhs=DD(fc,n));
          if(lhs!=L*fc-(c+1)*fn+low,error("transport recurrence failed"));
          checks++;
          if(low && lhs!=L*fc-(c+1)*fn,lowercontrols++);
          if(fn && lhs!=L*fc-c*fn+low,shiftcontrols++);
        );
      );
    );
    print("n=",n," d=",d,": ",nrows," rows; coefficients 0..",M," passed");
  ));
  my(W=[0,'a/4,1],Wp=vector(4,i,if(i<=3,DD(W[i],1),0)-if(i>1,(i-1)*W[i-1],0)));
  if(sum(i=1,3,W[i]*polcoef(WW[1],i-1,T))!=0,error("input witness invalid"));
  if(sum(i=1,4,Wp[i]*polcoef(WW[1],i-1,T))!=0,error("raised witness invalid"));
  if(Wp[4]!=-3,error("top coefficient multiplier incorrect"));
  if(Mod(Wp[4],3)!=0,error("excluded-characteristic control failed"));
  print("Nonzero n=1,d=1,m=2 witness: ",W,"; raised witness: ",Wp);
  print("At p=3 this operator loses the marked coefficient, as asserted; no general monotonicity conclusion there.");
  if(!lowercontrols || !shiftcontrols,error("negative controls were vacuous"));
  print("PASS: ",rows," complete rows; ",checks," dyadic polynomial identities; ",lowercontrols," missing-lower-row and ",shiftcontrols," wrong-shift failures detected.");
}
quit;

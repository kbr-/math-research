\\ Exact validation of the finite-fibre residue formula on every ambient basis row
\\ and every omitted coefficient. No normality or parameter-range test.
default(parisizemax,1000000000);
wt(mask,r)=sum(j=0,r-1,bittest(mask,j));
{
forprime(p=3,5,
  my(g=ffgen(p^2,'a),o=g^0);
  for(r=3,4,
    my(d=r-1,labels=vector(r,j,(j%p)+(j\p)*g));
    if(#Set(labels)!=r || setsearch(Set(labels),0*o),error("invalid labels"));
    for(which=0,1,
      my(M=2*d+which*(r-2),w=vector(r,j,sqrt(o+labels[j]*T+O(T^(M+2)))),basis=List(),cuts=List());
      for(mask=0,2^r-1,
        my(s=wt(mask,r),top=(M-s)\2);
        if(top>=0,for(j=0,top,listput(basis,[mask,j])));
        for(q=max(0,d-s+1),top,listput(cuts,[mask,q])));
      my(checked=0);
      for(b=1,#basis,for(c=1,#cuts,
        my(total=0*o);
        for(signs=0,2^r-1,
          my(f=T^basis[b][2]*o,den=o);
          for(i=0,r-1,
            my(v=(-1)^bittest(signs,i)*w[i+1]);
            if(bittest(basis[b][1],i),f*=v);
            if(bittest(cuts[c][1],i),den*=v));
          total+=polcoeff(f/den,cuts[c][2],T));
        total/=2^r;
        my(expected=o*(basis[b][1]==cuts[c][1] && basis[b][2]==cuts[c][2]));
        if(total!=expected,error("residue functional mismatch"));
        checked++));
      print("p=",p," r=",r," d=",d," M=",M," ambient=",#basis," cuts=",#cuts," fibre points=",2^r," checked entries=",checked," PASS");
    )
  )
);
print("PASS: all ambient basis/cut entries checked at both ambient bounds in characteristics three and five.");
}
quit;

\\ Exact Hasse controls for the aligned polynomial prefix lemma.
\\ Every subset of the p possible tail degrees at p=3,5,7; three necessary-scope controls.
default(nbthreads,1);
w='w;
check(c,s)=if(!c,error(s));
run_checks()={
  my(cases=0,negative=0);
  forprime(p=3,7,
    my(o=Mod(1,p),N=p*(p-1));
    for(mask=1,2^p-1,
      my(E=select(e->bittest(mask,e),vector(p,i,i-1)),q=#E,M=matrix(q,q,i,j,o*binomial(N+E[i],N+j-1)),D=matdet(M));
      check(D!=0,"every distinct aligned tail pivot set");cases++
    );
    check(o*binomial(p+1,p)!=0 && subst(o*(w-1),w,1)==0,"generic normality need not hold at prescribed point");
    check(o*binomial(p,p-1)==0,"unaligned low prefix fails");
    check(o*binomial(p^2,N)==0,"tail width p can fail");negative+=3;
    print("CONTROL p=",p," subsets=",2^p-1," scope_controls=3")
  );
  print("COMPLETE nonzero_tail_minors=",cases," scope_controls=",negative)
};
iferr(run_checks(),E,print(E);quit(1));
quit;

\\ Check the dimension-recursion encoding over Z[1/2][a,b,c,e].
\\ For n=2..4, d=0..3 and all truncations m=0..12, compare every
\\ coefficient of the direct character matrix with [A_d; A_(d-1) C].
\\ The largest case is a 20 by 13 matrix.  Polynomial identities over
\\ Z[1/2] also hold in every odd characteristic, including collisions.
\\ This is an encoding check, not a new finite threshold certificate.
\\ All truncations share the same series and maximal matrices.
T='T; AV=['a,'b,'c,'e]; M=12;
WW=vector(4,i,sqrt(1+AV[i]*T+O(T^(M+1))));
rowset(n,d)={
  my(out=List());
  for(mask=0,2^n-1,
    my(w=hammingweight(mask),f=1);
    if(w>d,next);
    for(i=1,n,if(bittest(mask,i-1),f*=WW[i]));
    for(q=0,(d-w)\2,listput(out,[q,f*T^q]));
  );
  Vec(out)
};
coefficient_matrix(rows)={
  matrix(#rows,M+1,i,j,polcoef(rows[i][2],j-1,T))
};
{
  my(cases=0,entries=0,bad=0);
  for(n=2,4,
    my(C=matrix(M+1,M+1,i,j,if(j>=i,polcoef(WW[n],j-i,T),0)),
       J=matrix(M+1,M+1,i,j,j==i+1),
       CI=matrix(M+1,M+1,i,j,if(j>=i,polcoef(1/WW[n],j-i,T),0)));
    if(C*C != matid(M+1)+AV[n]*J,error("square-root operator identity failed"));
    if(C*CI != matid(M+1),error("inverse identity failed"));
    if(C[M+1,] != matid(M+1)[M+1,],error("marked coordinate changed"));
    for(d=0,3,
      my(rows=rowset(n,d), lower=rowset(n-1,d), odd=rowset(n-1,d-1),
         A=coefficient_matrix(rows), B=coefficient_matrix(lower),
         D=coefficient_matrix(odd), AC=matconcat([B;D*C]));
      if(A!=AC,error("direct versus recursive matrix mismatch"));
      for(i=1,#rows,for(j=1,M+1,
        my(E=sum(v=1,n,AV[v]*deriv(A[i,j],AV[v])));
        if(E!=(j-1-rows[i][1])*A[i,j],error("row grading mismatch"));
      ));
      for(m=0,M,
        my(Cm=matrix(m+1,m+1,i,j,C[i,j]),
           Bm=matrix(#lower,m+1,i,j,B[i,j]),
           Dm=matrix(#odd,m+1,i,j,D[i,j]),
           Am=matrix(#rows,m+1,i,j,A[i,j]));
        if(Am!=matconcat([Bm;Dm*Cm]),error("truncation mismatch"));
        cases++; entries+=#rows*(m+1);
      );
      if(d>=1,
        my(wrong=C); wrong[1,3]=0;
        if(A!=matconcat([B;D*wrong]),bad++,error("negative control not detected"));
      );
      print("n=",n," d=",d,": ",#rows," rows; every m=0..",M," passed");
    );
  );
  print("PASS: ",cases," complete matrix cases; ",entries," coefficient entries; ",bad," wrong-convolution controls detected.");
  print("PASS: C^2=I+a_n J, inverse, marked coordinate and homogeneous row grading.");
}
quit;

\\ Copyright (c) 2026 Kamil Braun. SPDX-License-Identifier: MIT
\\ Exact polynomial row saturation over Q(b)[epsilon] or F_p(b)[epsilon].
\\ sat_rows(R, epsilon, p=0) requires nonempty full row rank over the fraction field.
\\ Returns [constant_rows, pole_bounds, operations, minor_columns, minor,
\\          excluded_prime_multiple, cancellation_steps].
\\ Operations [i,-v] divide row i by epsilon^v; [i,c] replace it by sum(c_j row_j).
\\ c_i=1, so every replacement is invertible. Coefficients c_j are epsilon-constant.
\\ Pole bounds concern the full left transformation, not just the final row valuations.
\\ A caller omitting columns of initial order >=H must separately check max(poles)<H.
\\ In characteristic zero the prime multiple audits every operation denominator and
\\ the final unit minor, coefficientwise in b; it does not audit an external encoding.
\\ Finite-characteristic calls reduce R modulo p and return prime multiple 1.
\\ No file writes, stack changes, or process exit: callers must catch errors and fail closed.

sat_contents(v)={
  my(a=Vec(numerator(v)), d=Vec(denominator(v)), scale=1);
  for(i=1,#a, if(type(a[i])!="t_INT" && type(a[i])!="t_FRAC",error("sat_rows: coefficients must be univariate rational functions")); scale=lcm(scale,denominator(a[i])));
  for(i=1,#d, if(type(d[i])!="t_INT" && type(d[i])!="t_FRAC",error("sat_rows: coefficients must be univariate rational functions")); scale=lcm(scale,denominator(d[i])));
  [abs(content(a*scale)),abs(content(d*scale))];
};

sat_denominator(bad,v,eps)={
  my(co=if(type(v)=="t_POL" && variable(v)==eps,Vec(v),[v]));
  for(i=1,#co,bad=lcm(bad,sat_contents(co[i])[2]));
  bad;
};

sat_rows(input,eps,fieldPrime=0)={
  if(type(input)!="t_MAT",error("sat_rows: expected a matrix"));
  my(shape=matsize(input),nrow=shape[1],ncol=shape[2]);
  if(nrow<1 || nrow>ncol,error("sat_rows: impossible full row rank"));
  if(fieldPrime!=0 && !isprime(fieldPrime),error("sat_rows: characteristic must be prime"));
  my(R=if(fieldPrime,Mod(1,fieldPrime)*input,input),bad=1,maxDegree=0);
  for(i=1,nrow,for(j=1,ncol,
    if(poldegree(denominator(R[i,j]),eps)>0,error("sat_rows: epsilon denominators are not polynomial input"));
    maxDegree=max(maxDegree,poldegree(R[i,j],eps));
    if(!fieldPrime,bad=sat_denominator(bad,R[i,j],eps))
  ));
  my(depth=vector(nrow),ops=List(),steps=0,LC);
  while(1,
    for(i=1,nrow,
      my(v=vecmin(vector(ncol,j,valuation(R[i,j],eps))));
      if(v>maxDegree,error("sat_rows: dependent rows or insufficient column window"));
      if(v<0,error("sat_rows: negative polynomial valuation"));
      if(v>0,listput(ops,[i,-v]);R[i,]/=eps^v;depth[i]+=v)
    );
    LC=matrix(nrow,ncol,i,j,polcoef(R[i,j],0,eps));
    my(K=matker(LC~));
    if(matsize(K)[2]==0,break);
    my(c=K[,1],chosen=0,newDepth=0);
    for(i=1,nrow,if(c[i]!=0,chosen=i;newDepth=max(newDepth,depth[i])));
    c/=c[chosen];
    if(!fieldPrime,for(i=1,nrow,bad=sat_denominator(bad,c[i],eps)));
    listput(ops,[chosen,c]);
    R[chosen,]=sum(i=1,nrow,c[i]*R[i,]);depth[chosen]=newDepth;
    steps++;
    if(steps>nrow*maxDegree,error("sat_rows: exceeded polynomial-minor degree bound"))
  );
  my(indices=matindexrank(LC)[2],unit=matdet(matrix(nrow,nrow,i,j,LC[i,indices[j]])));
  if(unit==0,error("sat_rows: missing unit maximal minor"));
  if(!fieldPrime,my(contents=sat_contents(unit));bad=lcm(bad,contents[1]*contents[2]));
  [LC,depth,Vec(ops),indices,unit,bad,steps];
};

\\ Replay works over both coefficient fields and checks every retained operation.
sat_replay(input,eps,S)={
  my(R=input,shape=matsize(R),nrow=shape[1],ncol=shape[2],depth=vector(nrow),nu=0);
  for(k=1,#S[3],
    my(op=S[3][k],i=op[1]);
    if(type(op[2])=="t_INT",
      if(op[2]>=0,error("sat_replay: invalid division"));
      R[i,]*=eps^op[2];depth[i]-=op[2];nu-=op[2],
      my(c=op[2],d=0);
      if(#c!=nrow || c[i]!=1,error("sat_replay: replacement determinant is not one"));
      for(j=1,nrow,
        if(poldegree(numerator(c[j]),eps)>0 || poldegree(denominator(c[j]),eps)>0,error("sat_replay: replacement is not epsilon-constant"));
        if(c[j]!=0,d=max(d,depth[j]))
      );
      R[i,]=sum(j=1,nrow,c[j]*R[j,]);depth[i]=d
    )
  );
  for(i=1,nrow,for(j=1,ncol,if(valuation(R[i,j],eps)<0,error("sat_replay: replay is not integral"))));
  my(C=matrix(nrow,ncol,i,j,polcoef(R[i,j],0,eps)),P=S[4],block=matrix(nrow,nrow,i,j,C[i,P[j]]));
  if(C!=S[1] || depth!=S[2] || matdet(block)!=S[5],error("sat_replay: certificate mismatch"));
  [C,depth,nu,block];
};

\\ Sharper characteristic audit over Q(b). Replays the certificate and uses the
\\ original chosen maximal minor: det(R_P)=eps^nu*det((U R)_P).
\\ Cramer's rule spreads the canonical primitive rows without specializing U.
\\ Returns [prime_multiple, canonical_constant_rows, nu, max_inverse_pole_bound].
\\ Input coefficient denominators and the chosen leading minor must survive.
\\ This is an open-stratum certificate, not commutation of arbitrary saturation
\\ and specialization. A vanishing chosen minor is unresolved, not a rank verdict.
sat_specialization(input,eps,S)={
  my(R=input,shape=matsize(R),nrow=shape[1],ncol=shape[2],bad=1);
  for(i=1,nrow,for(j=1,ncol,
    if(poldegree(denominator(R[i,j]),eps)>0,error("sat_specialization: input must be polynomial in epsilon"));
    bad=sat_denominator(bad,R[i,j],eps)
  ));
  my(replay=sat_replay(R,eps,S),C=replay[1],depth=replay[2],nu=replay[3],block=replay[4]);
  my(unitContents=sat_contents(S[5]));bad=lcm(bad,unitContents[1]*unitContents[2]);
  my(canonical=block^-1*C);
  for(i=1,nrow,for(j=1,ncol,
    my(d=sat_contents(canonical[i,j])[2],g=gcd(d,bad));
    while(g>1,d/=g;g=gcd(d,bad));
    if(d!=1,error("sat_specialization: unexplained canonical denominator"))
  ));
  [bad,canonical,nu,vecmax(depth)];
};

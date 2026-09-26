\\ A mechanism test, not another threshold table: n=4,d=2,N=12 over F_31.
\\ Search the 3654 triples 2<=a2<a3<a4<=30 with a1=1 for corank one
\\ persisting after the next jet column, but nonzero branch-parameter pairing.
\\ Stop at the first such point; do not enlarge the bound automatically.
\\ At success, check all four derivative pairings, the transport identity,
\\ a nonzero cofactor, and an independent exact determinant polynomial in a4.
T='T; P=31; N=12; LAST=16;
mkrows(a)={
  my(W=vector(4,i,sqrt(1+a[i]*T+O(T^(LAST+1)))),out=List());
  for(mask=0,15,
    if(hammingweight(mask)>2,next);
    my(f=prod(i=1,4,if(bittest(mask,i-1),W[i],1)));
    for(q=0,(2-hammingweight(mask))\2,listput(out,[q,mask,f*T^q]));
  ); Vec(out)
};
cmat(rows,m)=matrix(#rows,m+1,i,j,polcoef(rows[i][3],j-1,T));
pairing_control()={
  my(a=vector(4,i,Mod(i,P)),rows=mkrows(a),A=cmat(rows,N-1),
     lam=matker(A~),mu=matker(A));
  if(matrank(A)!=N-1 || matrank(cmat(rows,N-2))!=N-1 || matrank(cmat(rows,N))!=N,
     error("ordinary boundary control does not meet its hypotheses"));
  if(A~*lam!=matrix(N,1) || A*mu!=matrix(N,1),error("control kernel identity failed"));
  my(beta=vector(4,j,
       my(J=matrix(N,N,i,c,if(bittest(rows[i][2],j-1),
            polcoef(rows[i][3]*T/(2*(1+a[j]*T)),c-1,T),0)));
       (lam~*J*mu)[1,1]),
     fN=sum(i=1,N,lam[i,1]*polcoef(rows[i][3],N,T)),
     flow=sum(j=1,4,a[j]^2*beta[j]),pred=-N*fN*mu[N,1]);
  if(flow!=pred || !flow,error("control transport identity failed or vacuous"));
  my(i=1,j=1,k=1);
  while(!lam[i,1],i++);while(!mu[j,1],j++);while(!beta[k],k++);
  my(cof=(-1)^(i+j)*matdet(matrix(N-1,N-1,r,c,A[if(r<i,r,r+1),if(c<j,c,c+1)])),
     gamma=cof/(lam[i,1]*mu[j,1]),ae=a);
  if(!cof,error("control rank minor is zero"));
  ae[k]+='ee;
  my(detpoly=matdet(cmat(mkrows(ae),N-1)),der=polcoef(detpoly,1,'ee));
  if(polcoef(detpoly,0,'ee)!=0 || der!=gamma*beta[k] || !der,error("control determinant derivative failed"));
  if(der==-gamma*beta[k],error("wrong-sign negative control not detected"));
  print("Pairing encoding control: a=",liftall(a),"; beta=",liftall(beta));
  print("Left/right null vectors: ",liftall(lam),"; ",liftall(mu));
  print("Next coefficient=",fN,"; right last coefficient=",mu[N,1],"; flow=",flow,"; predicted=",pred);
  print("Nonzero cofactor ",[i,j]," = ",cof,"; gamma=",gamma);
  print("Independent determinant derivative in parameter ",k," = ",der);
  print("Exact control determinant polynomial: ",liftall(detpoly));
  print("PASS: corank-one deformation and flow encodings; wrong-sign control detected.");
};
{
  if(type(ONLY_CONTROL)=="t_INT" && ONLY_CONTROL,pairing_control();quit);
  my(bound=binomial(P-2,3),tried=0,found=0,a,rows,A,lam,mu,beta,fullcontrol=0,
     ranks=vector(N+1),higher=0,anytransverse=0);
  print("Bounded search: ",bound," tuples; each uses a 12x13 jet matrix at most.");
  if(bound>4000,error("search cap exceeded"));
  for(a2=2,P-3,
    for(a3=a2+1,P-2,
      for(a4=a3+1,P-1,
        a=vector(4,i,Mod([1,a2,a3,a4][i],P));tried++;
        rows=mkrows(a);A=cmat(rows,N-1);my(rk=matrank(A));ranks[rk+1]++;
        if(rk==N,
          if(!fullcontrol,print("Full-rank negative control: ",liftall(a));fullcontrol=1);
          next;
        );
        if(rk!=N-1 || matrank(cmat(rows,N))!=N-1,next);
        higher++;
        lam=matker(A~);mu=matker(A);
        beta=vector(4,j,
          my(J=matrix(N,N,i,c,if(bittest(rows[i][2],j-1),
               polcoef(rows[i][3]*T/(2*(1+a[j]*T)),c-1,T),0)));
          (lam~*J*mu)[1,1]);
        if(beta!=vector(4),anytransverse++);
        print("Higher-contact candidate ",liftall(a),"; beta=",liftall(beta));
        if(!beta[4],next);
        found=1;break;
      );if(found,break);
    );if(found,break);
  );
  print("Tuples examined: ",tried);
  print("Rank histogram (index k+1 counts rank k): ",ranks);
  print("Corank-one higher-contact points: ",higher,"; any nonzero gradient pairing: ",anytransverse);
  if(!found,print("NO HIT in the fixed search: no point with the requested nonzero fourth-parameter pairing; no range enlargement.");quit);
  if(!fullcontrol,error("negative control not yet available; schedule it separately"));
  if(A~*lam!=matrix(N,1) || A*mu!=matrix(N,1),error("kernel verification failed"));
  my(jets=vector(LAST+1,c,sum(i=1,N,lam[i,1]*polcoef(rows[i][3],c-1,T))),ord=0);
  while(ord<=LAST && !jets[ord+1],ord++);
  if(ord<N+1 || ord>LAST,error("unexpected exceptional order"));
  my(flow=sum(j=1,4,a[j]^2*beta[j]),pred=-N*jets[N+1]*mu[N,1]);
  if(flow!=pred,error("transport pairing identity failed"));
  if(flow!=0 || beta[4]==0,error("test does not distinguish the directions"));
  my(i=1,j=1);
  while(!lam[i,1],i++);while(!mu[j,1],j++);
  my(cof=(-1)^(i+j)*matdet(matrix(N-1,N-1,r,c,A[if(r<i,r,r+1),if(c<j,c,c+1)])),
     gamma=cof/(lam[i,1]*mu[j,1]));
  if(!cof,error("nonzero rank minor missing"));
  my(ae=a);ae[4]+='ee;
  my(detpoly=matdet(cmat(mkrows(ae),N-1)),der=polcoef(detpoly,1,'ee));
  if(polcoef(detpoly,0,'ee)!=0 || der!=gamma*beta[4] || !der,error("independent determinant derivative failed"));
  print("Chosen a: ",liftall(a));
  print("Ranks at lengths 12,13: ",[matrank(A),matrank(cmat(rows,N))],"; exceptional order: ",ord);
  print("Left section coefficients: ",liftall(lam));
  print("Right jet functional: ",liftall(mu));
  print("Section coefficients T^12..T^16: ",liftall(vector(5,j,jets[N+j])));
  print("Pairings beta_1..beta_4: ",liftall(beta));
  print("Transport pairing: ",flow,"; formula: ",pred);
  print("Cofactor at (row,column)=",[i,j],": ",cof,"; adjugate multiplier: ",gamma);
  print("Independent partial_a4 determinant derivative: ",der);
  print("Exact determinant under a4 -> a4+ee: ",liftall(detpoly));
  print("PASS: marked-point transport is tangent, while a4 variation is transverse at this point.");
}
quit;

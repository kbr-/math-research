/* Exact cellular transfer for the five elliptic quotients of the complex C4.
   Fixed problem: 16 vertices, 40 edges, 16 faces; five 8/16/8 quotients.
   Stages: boundary incidence and orientation; integral H1; transfer; binary kernel.
   No parameter sweep. Topological markings are chosen, not globally canonical. */
default(parisizemax, 1000000000);
S = [1,2,4,8,15];
must(b,msg) = if(!b,error(msg));
rep(v,k) = if(k==0,v,min(v,bitxor(v,S[k])));
pos(V,x) = {for(i=1,#V,if(V[i]==x,return(i)));error("missing vertex")};
edgepos(E,v,w,j) = {
  my(a=min(v,w),b=max(v,w));
  for(i=1,#E,if(E[i]==[a,b,j],return(if(v==a,i,-i))));
  error("missing oriented edge");
};
cell(k) = {
  my(V=List(),E=List(),J=select(j->j!=k,[1,2,3,4,5]),d1,d2);
  for(v=0,15,if(rep(v,k)==v,listput(V,v))); V=Vec(V);
  for(jj=1,#J,my(j=J[jj]);for(a=1,#V,
    my(v=V[a],w=rep(bitxor(v,S[j]),k));
    if(v<w,listput(E,[v,w,j])))); E=Vec(E);
  d1=matrix(#V,#E);d2=matrix(#E,#V);
  for(e=1,#E,d1[pos(V,E[e][1]),e]=-1;d1[pos(V,E[e][2]),e]=1);
  for(a=1,#V,my(v=V[a]);
    for(jj=1,#J,my(j=J[jj],w=rep(bitxor(v,S[j]),k),e=edgepos(E,v,w,j));
      d2[abs(e),a]+=sign(e);v=w);
    must(v==V[a],"face does not close"));
  must(d1*d2==matrix(#V,#V),"boundary squared is not zero");
  for(e=1,#E,
    must(sum(a=1,#V,abs(d2[e,a]))==2,"edge has wrong face incidence");
    must(sum(a=1,#V,d2[e,a])==0,"orientations do not cancel"));
  must(matrank(d1)==#V-1,"graph disconnected");
  [V,E,d1,d2];
};
hom(C) = {
  my(Z=matkerint(C[3]),r=matsize(Z)[2],R=matrix(r,#C[1]),SN,U,D,F=List(),B);
  for(j=1,#C[1],my(v=matinverseimage(Z,C[4][,j]));
    must(#v==r,"face not in cycle lattice");R[,j]=v);
  must(denominator(R)==1,"nonintegral cycle coordinates");
  SN=matsnf(R,1);U=SN[1];D=SN[3];
  must(U*R*SN[2]==D,"Smith certificate failed");
  for(i=1,r,
    if(D[i,]==vector(#C[1]),listput(F,i),
      must(sum(j=1,#C[1],abs(D[i,j]))==1,"homology has torsion")));
  F=Vec(F);B=Z*vecextract(U^-1,F);
  must(denominator(B)==1,"nonintegral homology representatives");
  must(C[3]*B==matrix(#C[1],#F),"representative not a cycle");
  [B,Z,R,U,F];
};
coords(H,B) = {
  my(Q=matrix(#H[5],matsize(B)[2]));
  for(j=1,matsize(B)[2],my(v=matinverseimage(H[2],B[,j]));
    must(#v==matsize(H[2])[2],"transferred cycle not in lattice");
    must(denominator(v)==1,"transfer has fractional cycle coordinates");
    Q[,j]=vecextract(H[4]*v,H[5]));Q;
};
transfer(C,Q,k) = {
  my(T=matrix(#C[2],#Q[2]),V=matrix(#C[1],#Q[1]),F=matrix(#C[1],#Q[1]));
  for(a=1,#Q[1],my(v=Q[1][a]);
    V[pos(C[1],v),a]=1;V[pos(C[1],bitxor(v,S[k])),a]=1;
    F[pos(C[1],v),a]=1;F[pos(C[1],bitxor(v,S[k])),a]=1);
  for(e=1,#Q[2],my(v=Q[2][e][1],j=Q[2][e][3]);
    for(b=0,1,my(w=if(b,bitxor(v,S[k]),v),f=edgepos(C[2],w,bitxor(w,S[j]),j));
      T[abs(f),e]+=sign(f)));
  must(C[3]*T==V*Q[3],"transfer does not commute with d1");
  must(T*Q[4]==C[4]*F,"transfer does not commute with d2");
  [T,V,F];
};
{
  my(C=cell(0),H=hom(C),Ms=List(),M,SN,K,J,weights=vector(6),codes=List());
  print("STAGES boundaries; integral homology; five chain transfers; binary gluing");
  print("SIZE C4: vertices=",#C[1]," edges=",#C[2]," faces=",#C[1]);
  must(matsize(H[1])[2]==10,"wrong genus-five homology rank");
  print("GENUS5_EDGES=",C[2]);print("GENUS5_D1=",C[3]);print("GENUS5_D2=",C[4]);
  print("GENUS5_CYCLE_LATTICE=",H[2]);print("GENUS5_FACE_COORDINATES=",H[3]);
  print("GENUS5_SMITH_LEFT=",H[4]);print("GENUS5_FREE_ROWS=",H[5]);
  print("GENUS5_H1_REPRESENTATIVES=",H[1]);
  for(k=1,5,my(Q=cell(k),HQ=hom(Q),T=transfer(C,Q,k),B,m);
    must(#Q[1]==8 && #Q[2]==16 && matsize(HQ[1])[2]==2,"wrong elliptic quotient sizes");
    B=T[1]*HQ[1];m=coords(H,B);listput(Ms,m);
    print("QUOTIENT ",k," inertia=",S[k]);
    print("VERTICES=",Q[1]);print("EDGES=",Q[2]);print("D1=",Q[3]);print("D2=",Q[4]);
    print("CYCLE_LATTICE=",HQ[2]);print("FACE_COORDINATES=",HQ[3]);
    print("SMITH_LEFT=",HQ[4]);print("FREE_ROWS=",HQ[5]);print("H1_REPRESENTATIVES=",HQ[1]);
    print("TRANSFER_C1=",T[1]);print("TRANSFER_H1=",m);
  );
  M=matconcat(Vec(Ms));SN=matsnf(M);
  must(abs(matdet(M))==32,"wrong transfer index");
  must(vecsort(SN)==[1,1,1,1,1,2,2,2,2,2],"wrong lattice quotient structure");
  K=lift(matker(Mod(M,2)));must(matsize(K)[2]==5,"wrong binary kernel rank");
  J=matrix(10,10,i,j,if((i%2 && j==i+1)||(!(i%2) && j==i-1),1,0));
  must(Mod(K~*J*K,2)==matrix(5,5),"kernel not isotropic in elliptic pair coordinates");
  for(mask=0,31,my(v=lift(Mod(K*vector(5,j,bittest(mask,j-1))~,2)),w=0);
    for(k=1,5,if(v[2*k-1]||v[2*k],w++));weights[w+1]++;listput(codes,Vec(v)));
  print("TRANSFER_MATRIX=",M);print("SMITH_INVARIANTS=",SN);
  print("BINARY_KERNEL_COLUMNS=",K);print("SYMPLECTIC_GRAM=",lift(Mod(K~*J*K,2)));
  print("ALL_BINARY_KERNEL_ELEMENTS=",Vec(codes));print("BLOCK_WEIGHT_DISTRIBUTION_0_TO_5=",weights);
  my(bad=K);bad[1,1]=1-bad[1,1];
  must(Mod(M*bad,2)!=matrix(10,5),"single-bit negative control was not detected");
  print("CONTROL changed first bit: rejected by transfer-kernel equation");
  print("PASS fixed cellular model; all five chain maps; integral bases; index32; kernel dimension5; isotropy");
}

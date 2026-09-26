/* Exact actual-lift constants from archived elliptic homology markings.
   Fixed test: fifteen nonzero midpoint squares, all sixteen sign elements,
   all 256 cocycle pairs, and a wrong-half negative control.
   The earlier homology and kernel computations are read, not rerun. */
S=[1,2,4,8,15];
must(b,msg)=if(!b,error(msg));
Q=vector(5,j,Map());K=0;
{
  my(lines=readstr("research/results/cube-theta-gluing-20260926/cellular-transfer.txt"),current=0);
  for(n=1,#lines,my(words=strsplit(lines[n]," "),parts=strsplit(lines[n],"="));
    if(#words>=2 && words[1]=="QUOTIENT",current=eval(words[2]));
    if(#parts==2,
      if(parts[1]=="BINARY_KERNEL_COLUMNS",K=eval(parts[2]));
      if(current>0 && setsearch(Set(["VERTICES","EDGES","D1","CYCLE_LATTICE","SMITH_LEFT","FREE_ROWS"]),parts[1]),
        mapput(Q[current],parts[1],eval(parts[2]))));
  );
  must(type(K)=="t_MAT" && matsize(K)==[10,5],"missing archived kernel");
}
rep(v,i)=min(v,bitxor(v,S[i]));
edgevec(i,v,j)={
  my(E=mapget(Q[i],"EDGES"),w=rep(bitxor(v,S[j]),i),out=vector(#E));
  for(k=1,#E,if(E[k]==[min(v,w),max(v,w),j],out[k]=if(v<w,1,-1);return(out~)));
  error("missing archived edge");
};
hcoords(i,v)={
  my(Z=mapget(Q[i],"CYCLE_LATTICE"),u=matinverseimage(Z,v));
  must(#u==matsize(Z)[2] && denominator(u)==1,"square not in integral cycle lattice");
  vecextract(mapget(Q[i],"SMITH_LEFT")*u,mapget(Q[i],"FREE_ROWS"));
};
chi(i,g)=(-1)^(sum(j=0,3,bittest(g,j))-if(i<=4,bittest(g,i-1),0));
twokernel(v)={
  my(w=lift(Mod(v,4)));
  if(sum(i=1,10,w[i]%2),return(0));
  #matinverseimage(Mod(K,2),Mod(w/2,2))==5;
};
{
  my(C=matrix(10,5),count=0,All=matrix(10,16),pattern=matrix(5,6),bad);
  print("SCOPE fifteen midpoint squares, sixteen group elements, 256 cocycle pairs");
  for(i=1,5,my(r=if(i==1,2,1),D1=mapget(Q[i],"D1"));
    for(j=1,5,if(j!=i && j!=r,
      my(a=edgevec(i,0,j)+edgevec(i,rep(S[j],i),r)-edgevec(i,rep(S[r],i),j)-edgevec(i,0,r));
      must(D1*a==vector(#mapget(Q[i],"VERTICES"))~,"midpoint square is not closed");
      my(v=hcoords(i,a));must(#v==2,"wrong elliptic homology rank");
      C[2*i-1,j]=lift(Mod(v[1],4));C[2*i,j]=lift(Mod(v[2],4));count++;
      print("SQUARE factor=",i," reference=",r," branch=",j," chain=",Vec(a)," homology=",Vec(v));
    ));
    my(reflections=Set(vector(5,j,if(j==i,[0,0],lift(Mod([C[2*i-1,j],C[2*i,j]],2))))));
    must(#reflections==4,"reflection centers do not give all elliptic two-torsion");
  );
  must(count==15,"wrong number of midpoint squares");
  for(g=1,15,my(j=1);while(!bittest(g,j-1),j++);
    my(previous=bitxor(g,S[j]));
    All[,g+1]=lift(Mod(All[,previous+1]+vector(10,k,chi(ceil(k/2),previous)*C[k,j])~,4));
  );
  must(twokernel(All[,16]-C[,5]),"fifth inertia does not match its composition");
  for(g=0,15,for(h=0,15,
    my(v=All[,bitxor(g,h)+1]-All[,g+1]-vector(10,k,chi(ceil(k/2),g)*All[k,h+1])~);
    must(twokernel(v),"sign cocycle fails modulo actual kernel");
  ));
  for(i=1,5,for(j=1,6,my(g=if(j<=5,S[j],3));pattern[i,j]=(1-chi(i,g))/2));
  print("QUARTER_CONSTANTS_COLUMNS_s1_TO_s5=",C);
  print("TWICE_CONSTANTS_BINARY=",lift(Mod(C,2)));
  print("ALL_QUARTER_CONSTANTS_COLUMNS_g0_TO_g15=",All);
  print("INCREMENT_PATTERN_s1_s2_s3_s4_s5_s1pluss2=",pattern);
  print("FIFTH_COMPOSITION_DIFFERENCE_MOD4=",lift(Mod(All[,16]-C[,5],4)));
  bad=C[,5];bad[1]+=2;
  must(!twokernel(All[,16]-bad),"wrong-half control was not rejected");
  print("CONTROL add half-period in first coordinate of fifth constant: rejected despite unchanged doubled point");
  print("PASS fifteen squares; complete sign cocycle; actual fifth inertia; exponent patterns; wrong-half control");
}

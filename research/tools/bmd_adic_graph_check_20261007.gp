\\ Independent direct-jet check of the canonical pilot's stored frames, not graph closure.
default(parisizemax,2000000000);
default(nbthreads,1);
read("research/tools/bmd_branch_state_core_20261007.gp");
mval(M)={my(v=1000000);for(i=1,matsize(M)[1],for(j=1,matsize(M)[2],if(M[i,j]!=0,v=min(v,valuation(M[i,j],XPAR)))));v};
submat(M,rr,cc)=matrix(#rr,#cc,i,j,M[rr[i],cc[j]]);
chop(M,N)=matrix(matsize(M)[1],matsize(M)[2],i,j,truncate(M[i,j]+O(XPAR^N)));
canonical_rows(Z)={
 my(M=chop(Z,1),k=matsize(Z)[2],rows=List());
 for(i=1,matsize(Z)[1],my(rr=concat(Vec(rows),[i]));if(matrank(submat(M,rr,[1..k]))>#rows,listput(rows,i));if(#rows==k,return(Vec(rows))));
 error("reduction not full column rank")
};
{
T='x;XPAR='u;NN=3;PP=3;OO=Mod(1,3);BB=4;CC=12;PREC=16;
AA=[OO,OO*XPAR,OO*(XPAR^2+XPAR+2)];my(coords=List());for(S=0,7,for(i=1,NN,if(!bittest(S,i-1),listput(coords,[S,i]))));COORD=Vec(coords);ZZ=vector(CC,c,-OO/AA[COORD[c][2]]);
my(ell=vector(NN,i,OO+AA[i]*T+O(T^17)),roots=apply(sqrt,ell));for(i=1,NN,assert(valuation(roots[i]^2-ell[i],T)>=17,"root equations"));CH=vector(8,S,prod(i=1,NN,if(bittest(S-1,i-1),roots[i],OO)));
my(lines=readstr("research/results/bmd-exception-adic-closure-20261007/canonical-pilot.txt"),states=List(),xs=List(),cache=Map(),count=0,negative=0);gettime();
for(i=1,#lines,
 my(z=strsplit(lines[i],"BASE_STATE = "));
 if(#z==2,listput(states,eval(z[2]));listput(xs,0),
  z=strsplit(lines[i]," DATA = ");if(#z==2,listput(states,eval(z[2]));listput(xs,eval(strsplit(z[1]," representative_x=")[2])))
 );
);
assert(#states==2,"expected canonical pilot has two saved states");
for(t=1,#states,my(st=states[t],xx=xs[t]);assert(st[1]==min(xx,2),"state flag");assert(xx<=1,"direct control sizing");
 for(j=0,2,for(delta=0,CC-1,
  my(d=NN+xx-j,L=BB*d-delta,key=[d,L],V);
  if(mapisdefined(cache,key),V=mapget(cache,key),V=source_eval(d)*matker(source_jet(d,L));mapput(cache,key,V));
  my(U=st[2][j*CC+delta+1],k=matsize(U)[2]);assert(matsize(V)[2]==k,"direct kernel dimension");
  if(k,
   my(rr=canonical_rows(U));assert(submat(U,rr,[1..k])==matid(k),"stored chart not canonical");assert(#rr==k,"stored frame not saturated");my(Uc=U*submat(U,rr,[1..k])^(-1),Vc=V*submat(V,rr,[1..k])^(-1));assert(mval(Uc-Vc)>=PREC,"stored frame differs from direct kernel");
   if(!negative,my(free=select(i->!setsearch(Set(rr),i),[1..CC]),bad=Uc);bad[free[1],1]+=OO*XPAR^(PREC-1);assert(mval(bad-Vc)<PREC,"perturbed frame escaped check");negative=1)
  );count++
 ));
);
print("DIRECT_FRAME_CHECKS=",count," distinct_jet_kernels=",#cache," corruption_detected=",negative," CPU_MS=",gettime());assert(negative,"missing negative control");print("ADIC_GRAPH_DIRECT_CHECK_COMPLETED")
}
quit;

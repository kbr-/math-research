\\ Independent original-source checks for the small reached parity states.
default(parisizemax,2000000000);
default(nbthreads,1);
read("research/tools/bmd_branch_state_core_20261007.gp");
read("research/tools/bmd_series_graph_core_20261007.gp");
{
T='x;XPAR='u;NN=3;PP=3;OO=Mod(1,3);BB=4;CC=12;PREC=16;
AA=[OO,OO*XPAR,OO*(XPAR^2+XPAR+2)];my(coords=List());for(S=0,7,for(i=1,NN,if(!bittest(S,i-1),listput(coords,[S,i]))));COORD=Vec(coords);ZZ=vector(CC,c,-OO/AA[COORD[c][2]]);
my(ell=vector(NN,i,OO+AA[i]*T+O(T^25)),roots=apply(sqrt,ell));for(i=1,NN,assert(polcoef(roots[i],0,T)==OO && valuation(roots[i]^2-ell[i],T)>=25,"root equations"));CH=vector(8,S,prod(i=1,NN,if(bittest(S-1,i-1),roots[i],OO)));
my(lines=readstr("research/results/bmd-exception-reversed-graph-20261007/graph.txt"),states=List(),xs=List(),cache=Map(),count=0,negative=0);gettime();
for(i=1,#lines,my(z=strsplit(lines[i],"BASE_STATE = "));if(#z==2,listput(states,eval(z[2]));listput(xs,0),z=strsplit(lines[i]," DATA = ");if(#z==2,my(xx=eval(strsplit(z[1]," representative_x=")[2]));if(xx<=3,listput(states,eval(z[2]));listput(xs,xx)))));
assert(#states>=1,"missing saved states");
for(t=1,#states,my(st=states[t],xx=xs[t]);assert(st[1]==min(xx,2) && st[2]==xx%2,"state flag/parity");
 for(j=0,2,for(delta=0,CC-1,
  my(d=NN+xx-j,L=max(0,BB*d-delta),key=[d,L],V);
  if(mapisdefined(cache,key),V=mapget(cache,key),my(raw=source_eval(d)*matker(source_jet(d,L)));V=matrix(CC,matsize(raw)[2],c,k,AA[COORD[c][2]]^floor((d-hammingweight(COORD[c][1]))/2)*raw[c,k]);mapput(cache,key,V));
  my(U=st[3][j*CC+delta+1],k=matsize(U)[2]);assert(matsize(V)[2]==k,"direct weighted kernel dimension");
  if(k,my(rr=canonical_rows(U));assert(submat(U,rr,[1..k])==matid(k),"stored chart not canonical");my(Vc=V*submat(V,rr,[1..k])^(-1));assert(mval(U-Vc)>=PREC,"weighted frame differs from direct source");
   if(!negative,my(free=select(i->!setsearch(Set(rr),i),[1..CC]),bad=U);bad[free[1],1]+=OO*XPAR^(PREC-1);assert(mval(bad-Vc)<PREC,"corrupted weighted frame escaped check");negative=1)
  );count++
 ))
);
print("DIRECT_WEIGHTED_STATES=",Vec(xs)," FRAME_CHECKS=",count," SOURCE_KERNELS=",#cache," corruption_detected=",negative," CPU_MS=",gettime());assert(negative,"missing negative control");print("REVERSED_GRAPH_DIRECT_CHECK_COMPLETED")
}
quit;

\\ Check saved total digit coverage, certificate bounds, and agreement with direct-checked prefix frames.
default(parisizemax,1000000000);
default(nbthreads,1);
read("research/tools/bmd_series_graph_core_20261007.gp");
coverage(states,edges)={
 my(seen=Map(),n=#states);
 for(t=1,#edges,my(e=edges[t],key=[e[1],e[2]]);if(e[1]<1||e[1]>n||e[2]<0||e[2]>2||e[3]<1||e[3]>n||mapisdefined(seen,key),return(0));mapput(seen,key,1));
 #seen==3*n
};
{
a=ffgen(Mod(1,3)*('a^2+'a+2),'a);OO=a^0;XPAR='u;CC=12;PREC=2;WP=6;
my(path="research/results/bmd-exception-reversed-graph-20261007/",lines=readstr(concat(path,"smooth-closed-graph.txt")),states=List(),edges=List(),xs=List(),closed=0,components=0,prefix=Map(),checks=0,amin=1000000,amax=0,bmax=0,keep=1000000);
for(i=1,#lines,
 my(z=strsplit(lines[i],"BASE_STATE = "));
 if(#z==2,listput(states,eval(z[2]));listput(xs,0));
 z=strsplit(lines[i]," DATA = ");if(#z==2,listput(states,eval(z[2]));listput(xs,eval(strsplit(z[1]," representative_x=")[2])));
 z=strsplit(lines[i],"EDGE = ");if(#z==2,listput(edges,eval(strsplit(z[2]," WALL_MS=")[1])));
 if(#strsplit(lines[i],"closed=1 ")==2,closed=1)
);
assert(closed && #states==242 && #edges==726 && coverage(states,edges),"incomplete or malformed graph");
assert(!coverage(states,Vec(edges)[1..#edges-1]),"missing-edge corruption accepted");
for(t=1,#states,my(st=states[t]);assert(st[1]==min(xs[t],2) && #st[2]==36,"state flag/component count");
 for(c=1,36,my(U=st[2][c],k=matsize(U)[2]);assert((!k || matsize(U)[1]==CC) && mval(U)>=0,"state integrality");if(k,my(rr=canonical_rows(U));assert(submat(U,rr,[1..k])==matid(k),"state canonical chart")))
);
for(t=1,#edges,my(e=edges[t],src=states[e[1]],dst=states[e[3]],records=e[4]);assert(dst[1]==min(2,3*src[1]+e[2]) && #records==36,"edge flag or coverage");
 for(c=1,36,my(z=records[c],j=(c-1)\12,delta=(c-1)%12,k=matsize(dst[2][c])[2]);assert(z[1]==j && z[2]==delta && z[3]==#z[4] && z[3]==#z[5],"local indices/pivot sizes");assert(z[6]<WP && z[7]>0,"pivot precision");amax=max(amax,z[6]);
  if(k,my(ret=min(min(WP,z[9]+z[8])-z[6]-z[11],z[12]));assert(ret>=PREC && ret==z[13],"image precision");bmax=max(bmax,z[11]);keep=min(keep,ret));components++
 )
);
lines=readstr(concat(path,"smooth-graph.txt"));for(i=1,#lines,my(z=strsplit(lines[i],"BASE_STATE = "));if(#z==2,mapput(prefix,0,eval(z[2])));z=strsplit(lines[i]," DATA = ");if(#z==2,my(x=eval(strsplit(z[1]," representative_x=")[2]));if(x<=3,mapput(prefix,x,eval(z[2])))));
for(t=1,#states,if(xs[t]<=3,assert(states[t]==mapget(prefix,xs[t]),"direct-checked prefix changed");checks+=36));assert(checks==144,"missing independently checked prefix");
print("TOTAL_COVERAGE states=",#states," edges=",#edges," local_certificates=",components," max_pivot_loss=",amax," max_image_loss=",bmax," min_retained=",keep," direct_checked_prefix_components=",checks," missing_edge_corruption_detected=1");
print("SMOOTH_GRAPH_COVERAGE_COMPLETED; residual products checked by producer, not independently recomputed here")
}
quit;

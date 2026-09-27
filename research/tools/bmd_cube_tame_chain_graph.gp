\\ Actual tame-chain coset graph: structural controls n3,n4; one rank test n5,d3.
\\ Named question: does the specified interior point give rank -1 for dH-NP?
\\ n5 has 32 component vertices and 48 edges; subdivision3 gives 128/144,
\\ genus17. d3 gives deg(dH)=48, N32, residual degree16.
\\ Exact Dhar burning uses integer divisor updates and a directly checked
\\ Laplacian potential. No enumeration of effective divisors or degree sweep.
rep2(g,a,b)=vecmin([g,bitxor(g,a),bitxor(g,b),bitxor(g,bitxor(a,b))]);
chain(nn,sub)={
 my(ng=2^nn,ids=matrix(nn-1,ng),vl=List(),el=List(),a,b,c,rr,id,ngv,edges,nv,L,H,labels,mark=0,x,y,last);
 for(j=1,nn-1,
  if(j==1,a=1;b=2,if(j==nn-1,a=2^(nn-1);b=ng-1,a=2^j-1;b=2^j));
  for(g=0,ng-1,if(rep2(g,a,b)==g,
   listput(vl,[j,g]);id=#vl;
   ids[j,g+1]=id;ids[j,bitxor(g,a)+1]=id;ids[j,bitxor(g,b)+1]=id;ids[j,bitxor(g,bitxor(a,b))+1]=id;
  ));
 );
 for(j=1,nn-2,c=2^(j+1)-1;for(g=0,ng-1,if(g<bitxor(g,c),
  x=ids[j,g+1];y=ids[j+1,g+1];
  if(x!=ids[j,bitxor(g,c)+1]||y!=ids[j+1,bitxor(g,c)+1],error("edge-coset incidence"));
  listput(el,[x,y,j,g]);
 )));
 ngv=#vl;edges=Vec(el);nv=ngv+#el*(sub-1);L=matrix(nv,nv);H=vector(nv)~;
 labels=vector(nv,i,if(i<=ngv,vl[i],[0,0]));
 for(i=1,ngv,if(vl[i][1]==nn-1,H[i]=2));
 for(e=1,#edges,
  last=edges[e][1];
  for(k=1,sub,
   y=if(k==sub,edges[e][2],ngv+(e-1)*(sub-1)+k);
   if(k<sub,labels[y]=[edges[e][3],edges[e][4],k]);
   L[last,last]++;L[y,y]++;L[last,y]--;L[y,last]--;
   if(nn==5&&edges[e][3]==2&&edges[e][4]==0&&k==1,mark=y);
   last=y;
  );
 );
 if(ngv!=(nn-1)*2^(nn-2)||#el!=(nn-2)*2^(nn-1),error("coset counts"));
 if(#el*sub-nv+1!=1+(nn-3)*2^(nn-2),error("genus count"));
 if(vecsum(H)!=2^(nn-1),error("infinity degree"));
 if(L*vector(nv,i,1)~!=vector(nv)~,error("Laplacian row sums"));
 return([L,H,labels,edges,mark,ngv]);
};
reduce_at(L,D,q)={
 my(nv=#D,burn,order,change,U,f=vector(nv)~,cur=D,steps=0,v);
 if(sum(i=1,nv,if(i==q,0,cur[i]<0)),error("not q-effective"));
 while(1,
  burn=vector(nv)~;burn[q]=1;order=List([q]);change=1;
  while(change,
   change=0;
   for(i=1,nv,if(!burn[i]&&cur[i]<sum(j=1,nv,if(j!=i,-L[i,j]*burn[j],0)),
    burn[i]=1;listput(order,i);change=1;
   ));
  );
  if(vecsum(burn)==nv,
   if(cur!=D-L*f,error("potential verification"));
   return([cur,f,Vec(order),steps]);
  );
  U=vector(nv,i,1-burn[i])~;cur-=L*U;f+=U;steps++;
  if(sum(i=1,nv,if(i==q,0,cur[i]<0)),error("q-effectivity lost"));
  if(steps>100000,error("burning cap"));
 );
};
{
my(C,L,H,nv,K,ff,expect,adj,ids,verts);
for(nn=3,4,
 C=chain(nn,1);L=C[1];H=C[2];nv=#H;
 if(matrank(L)!=nv-1,error("connected rank control"));
 K=vector(nv,i,L[i,i]-2)~;
 ff=vector(nv,i,-(C[3][i][1]-1)*(C[3][i][1]-2)/2)~;
 if(L*ff!=K-(nn-3)*H,error("canonical relation control"));
 print("STRUCTURAL_CONTROL n=",nn," vertices=",nv," edges=",#C[4]," genus=",#C[4]-nv+1," H_degree=",vecsum(H));
);
C=chain(5,3);L=C[1];H=C[2];nv=#H;
my(P=C[5],D=3*H);D[P]-=32;
if(P==0||vecsum(D)!=16,error("marked target"));
print("TARGET n=5 d=3 subdivision=3 vertices=",nv," edges=",#C[4]*3," genus=17 P=",P," label=",C[3][P]);
print("UNSUBDIVIDED_EDGES = ",C[4]);
print("VERTEX_LABELS = ",C[3]);
print("H_DIVISOR = ",H);
my(R=reduce_at(L,D,P),cur=R[1],pot=R[2],ord=R[3],burn=vector(nv)~);
if(#ord!=nv||ord[1]!=P,error("burn ordering"));
burn[P]=1;
for(k=2,nv,my(v=ord[k]);if(burn[v]||cur[v]>=sum(j=1,nv,if(j!=v,-L[v,j]*burn[j],0)),error("burn certificate"));burn[v]=1);
if(cur!=D-L*pot,error("direct final identity"));
print("REDUCED_DIVISOR = ",cur);
print("FIRING_POTENTIAL = ",pot);
print("BURN_ORDER = ",ord);
print("FIRING_STEPS = ",R[4]," MARKED_COEFFICIENT = ",cur[P]," RANK_MINUS_ONE = ",cur[P]<0);
print("CHAIN_GRAPH_CONTROL_COMPLETED");
}
quit;

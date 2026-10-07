\\ Exact conjugation and precision test for degree-reversed branch coordinates.
default(parisizemax,2000000000);
default(nbthreads,1);
read("research/tools/bmd_branch_state_core_20261007.gp");
read("research/tools/bmd_series_graph_core_20261007.gp");
gauge(d)=vector(CC,c,AA[COORD[c][2]]^floor((d-hammingweight(COORD[c][1]))/2));
row_scale(M,v)=matrix(matsize(M)[1],matsize(M)[2],i,j,v[i]*M[i,j]);
{
my(count=0,planned=260884);print("PLANNED_INTEGER_CHECKS=",planned,"; child matrices at most21 by32, parent12 by21");assert(planned<300000,"control budget");
for(n=3,10,forprime(p=3,11,my(b=(p-1)/2);for(d=n-2,n-2+4*p,for(s=0,n-1,my(D=floor((d-s)/2),m=n-s,M=D+b*m);
 for(r=0,p-1,my(dr=floor((d+(p-1)*n-2*r)/p),Dr=floor((dr-s)/2),h=(M-r)%p);
  assert(Dr==floor((M-r)/p),"child polynomial degree");
  for(j=0,b-1,assert(M+j-r-p*Dr==h+j,"C exponent");count++);
  assert(b*(m-2)+D+b-r-p*Dr==h-b,"H exponent");
  assert((floor((d+2*p-s)/2)+b*m-r)%p==h,"coefficient period");count+=2
 )
))));assert(count==planned,"integer check count");print("INTEGER_CONJUGATION_CHECKS=",count);
T='x;XPAR='u;NN=3;PP=3;OO=Mod(1,3);BB=4;CC=12;HH=1;GG=1;PREC=17;WP=51;
AA=[OO,OO*XPAR,OO*(XPAR^2+XPAR+2)];my(coords=List());for(S=0,7,for(i=1,NN,if(!bittest(S,i-1),listput(coords,[S,i]))));COORD=Vec(coords);
ZZ=vector(CC,c,-OO/AA[COORD[c][2]]);RR=vector(CC,c,my(S=COORD[c][1],i=COORD[c][2]);AA[i]*prod(h=1,NN,if(h==i||bittest(S,h-1),OO,OO+AA[h]*ZZ[c])));
my(ell=vector(NN,i,OO+AA[i]*T+O(T^22)),roots=apply(sqrt,ell));for(i=1,NN,assert(polcoef(roots[i],0,T)==OO && valuation(roots[i]^2-ell[i],T)>=22,"normalized roots"));CH=vector(8,S,prod(i=1,NN,if(bittest(S-1,i-1),roots[i],OO)));
my(d=18,L=63,ds=vector(3,r,floor((d+6-2*(r-1))/3)),ls=vector(3,r,ceil((L-(r-1))/3)),raw=vector(3),weighted=vector(3));gettime();
for(r=1,3,my(V=source_eval(ds[r])*matker(source_jet(ds[r],ls[r])));raw[r]=exact_frame(V);weighted[r]=exact_frame(row_scale(V,gauge(ds[r]))));
print("CHILD_EXACT_CPU_MS=",gettime()," degrees=",ds," lengths=",ls," dimensions=",apply(U->matsize(U)[2],raw));
my(Cw=matrix(CC,3,c,r,my(S=COORD[c][1],i=COORD[c][2],m=NN-hammingweight(S),D=floor((d-hammingweight(S))/2),h=(D+m-(r-1))%3);(-1)^(r-1)*AA[i]^h),Hw=matrix(CC,3,c,r,my(S=COORD[c][1],i=COORD[c][2],m=NN-hammingweight(S),D=floor((d-hammingweight(S))/2),h=(D+m-(r-1))%3,Delta=prod(t=1,NN,if(t==i||bittest(S,t-1),OO,AA[i]-AA[t])));if(r==1,0*OO,(r-1)*(-1)^(r-2)*AA[i]^(h-1)/Delta)));
for(c=1,CC,for(r=0,2,my(s=hammingweight(COORD[c][1]),i=COORD[c][2],D=floor((d-s)/2),M=D+NN-s,Dr=floor((ds[r+1]-s)/2));assert(Cw[c,r+1]==AA[i]^M*ZZ[c]^r*AA[i]^(-3*Dr),"C field conjugation");assert(Hw[c,r+1]==AA[i]^D*RR[c]^(-1)*r*ZZ[c]^(r-1)*AA[i]^(-3*Dr),"H field conjugation")));
my(kdims=apply(U->matsize(U)[2],raw),s=vecsum(kdims),Cr=matrix(CC,s,i,j,0*OO),Hr=Cr,Cn=Cr,Hn=Cr,off=0);
for(r=0,2,for(c=1,CC,for(j=1,kdims[r+1],Cr[c,off+j]=ZZ[c]^r*raw[r+1][c,j]^3;Hr[c,off+j]=RR[c]^(-1)*r*ZZ[c]^(r-1)*raw[r+1][c,j]^3;Cn[c,off+j]=Cw[c,r+1]*weighted[r+1][c,j]^3;Hn[c,off+j]=Hw[c,r+1]*weighted[r+1][c,j]^3));off+=kdims[r+1]);
my(Ur=Hr*matker(Cr),Un=Hn*matker(Cn));assert(matsize(Ur)[2]==9 && matsize(Un)[2]==9,"exact parent kernel");assert(matrank(matconcat([row_scale(Ur,gauge(d)),Un]))==9,"weighted parent image changed");print("EXACT_RECONSTRUCTION_CPU_MS=",gettime());
my(ac=max(0,-mval(Cw)),ah=max(0,-mval(Hw)));CCOEF=chop(XPAR^ac*Cw,WP);HCOEF=chop(XPAR^ah*Hw,WP);
INVCACHE=Map();LOCALCACHE=Map();INVS=0;INVHITS=0;PICK_FALLBACKS=0;LOCALS=0;LOCALHITS=0;INVMS=0;RESMS=0;EXCHANGES=0;NEGATIVE=0;STARTMS=getwalltime();
my(result=local_step(apply(U->chop(U,PREC),weighted),9));assert(result[1],"weighted local certificate refused");my(U=result[2],rr=canonical_rows(U),direct=Un*submat(Un,rr,[1..9])^(-1));assert(mval(U-direct)>=PREC,"weighted precision output disagrees with exact reconstruction");
print("WEIGHTED_CERTIFICATE = ",result[3]," clearing=",[ac,ah]," wall_ms=",getwalltime()-STARTMS);
print("WEIGHTED_OUTPUT_FRAME = ",U);
print("REVERSED_BRANCH_CONTROL_COMPLETED: exact conjugation and one parent control, not graph closure")
}
quit;

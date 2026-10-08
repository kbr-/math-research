\\ Geometric local jets for every full paired-source cut; no original rows dropped.
default(parisizemax,2500000000);
default(nbthreads,1);
modulus=ffinit(3,4);b=ffgen(modulus,'b);o=b^0;
field=vector(81,i,sum(j=0,3,o*((((i-1)\3^j)%3))*b^j));
codes=Map();for(i=1,81,mapput(codes,Str(field[i]),i-1));
code(z)=mapget(codes,Str(z+0*o));
assert(ok,msg)=if(!ok,error(msg));
Strjoin(v,sep)={my(s="");for(i=1,#v,s=Str(s,if(i==1,"",sep),v[i]));return(s);};
a=0*o;for(i=2,81,if(field[i]^2==-o,a=field[i];break));assert(a!=0,"F9 embedding");
read("research/results/bmd-exception-outside-coverage-20261008/paired-data.gp");
sl=apply(z->z+0*o,sl);
bases=[base3,base4,base5]; lens=[7,11,15,15,4];offset=vector(5);dim=0;for(i=1,5,offset[i]=dim;dim+=8*lens[i]);assert(dim==416,"complete geometric jet dimension");
rootsat=vector(5);phiJets=vector(dim,i,0*o);baseJets=vector(3,z,matrix(dim,188,i,j,0*o));
localvalue(co,point,T0,rr,L,M=0)={my(v=0*o+O(u^L));if(point<=4,for(mask=0,15,v+=subst(co[mask+1],T,T0)*prod(j=1,4,if(bittest(mask,j-1),rr[j],o))),for(mask=0,15,for(j=max(0,(M-hammingweight(mask)-L+2)\2),if(co[mask+1]==0,-1,poldegree(co[mask+1],T)),my(e=M-2*j-hammingweight(mask));assert(e>=0,"infinity pole bound");if(e<L,my(cc=polcoef(co[mask+1],j,T));if(cc!=0,v+=cc*u^e*prod(t=1,4,if(bittest(mask,t-1),rr[t],o)))))));return(v);};
completed=0;
{for(point=1,5,my(L=lens[point],T0=if(point<=4,-o/sl[point]+u^2/sl[point]+O(u^(L+2)),0),rr=vector(4),others=if(point<=4,select(j->j!=point,[1,2,3,4]),[2,3,4]));
for(j=1,4,if(point<=4,if(j==point,rr[j]=u+O(u^(L+2)),my(c=o-sl[j]/sl[point]);rr[j]=sqrt(c)*sqrt(o+(sl[j]/sl[point]/c)*u^2+O(u^(L+2)))),rr[j]=sqrt(sl[j])*sqrt(o+u^2/sl[j]+O(u^(L+2)))));
rootsat[point]=rr;
for(signs=0,7,my(r=rr);for(t=1,3,if(bittest(signs,t-1),r[others[t]]=-r[others[t]]));my(pj=localvalue(phi,point,T0,r,L,96));assert(polcoef(pj,0,u)!=0,"torsion function unit at every cut point");assert(valuation(pj^2160-o,u)>=L,"full local period");for(k=0,L-1,phiJets[offset[point]+signs*L+k+1]=polcoef(pj,k,u));
for(z=1,3,for(col=1,188,my(fj=localvalue(bases[z][col],point,T0,r,L,32*(z+2)-72));for(k=0,L-1,baseJets[z][offset[point]+signs*L+k+1,col]=polcoef(fj,k,u))));
);completed++;print("LOCAL point=",point," length=",L," all 8 sign points and 564 frame columns verified");)}
if(completed!=5,quit(1));
rows=List();
{for(point=1,4,for(mask=0,15,my(e=bittest(mask,point-1),bi=(2^(point-1)-1)*e+2^(point-1)*sum(j=point+1,4,1-bittest(mask,j-1)));for(j=0,bi-1,listput(rows,[point,mask,2*j+e]))));
for(mask=0,15,my(s=hammingweight(mask));for(k=0,3-s,if(k%2==s%2,listput(rows,[5,mask,k]))));}
assert(#rows==188,"all finite and infinity cuts");
W=matrix(188,dim,i,j,0*o);
{for(row=1,188,my(point=rows[row][1],mask=rows[row][2],target=rows[row][3],L=lens[point],others=if(point<=4,select(j->j!=point,[1,2,3,4]),[2,3,4]),inv=1/prod(j=1,4,if(bittest(mask,j-1)&&j!=point,rootsat[point][j],o)));if(point==5,inv=1/prod(j=1,4,if(bittest(mask,j-1),rootsat[point][j],o)));
for(signs=0,7,my(sgn=(-1)^sum(t=1,3,bittest(signs,t-1)*bittest(mask,others[t]-1)));for(k=0,target,W[row,offset[point]+signs*L+k+1]=sgn*o/8*polcoef(inv,target-k,u)));)}
out="research/results/bmd-exception-outside-coverage-20261008/local-data.txt";
write(out,"4 ",Strjoin(apply(x->Str(lift(x)),Vecrev(modulus))," "));write(out,code(a));write(out,Strjoin(apply(x->Str(code(x)),phiJets)," "));
for(z=1,3,for(i=1,dim,write(out,Strjoin(vector(188,j,Str(code(baseJets[z][i,j])))," "))));
for(i=1,188,write(out,Strjoin(vector(dim,j,Str(code(W[i,j])))," ")));
for(z=1,3,my(A=W*baseJets[z]);print("BASE degree=",z+2," rank=",matrank(A));for(i=1,188,write(out,Strjoin(vector(188,j,Str(code(A[i,j])))," "))));
print("FIELD ",modulus," F9_root_code=",code(a));
print("COMPLETE 416 geometric jets, all 188 cuts, all three frames, and local period2160.");

\\ Geometric local jets for every full paired-source cut; no original rows dropped.
default(parisizemax,2500000000);
default(nbthreads,1);
modulus=ffinit(29,2);b=ffgen(modulus,'b);o=b^0;
field=vector(841,i,o*((i-1)%29)+b*((i-1)\29));
codes=Map();for(i=1,841,mapput(codes,Str(field[i]),i-1));
code(z)=mapget(codes,Str(z+0*o));
assert(ok,msg)=if(!ok,error(msg));
Strjoin(v,sep)={my(s="");for(i=1,#v,s=Str(s,if(i==1,"",sep),v[i]));return(s);};
a=0*o;
read("research/results/bmd-twenty-nine-paired-20261009/paired-data-second.gp");
sl=apply(z->z+0*o,sl);
bases=[base3,base4,base5]; lens=[15,15,15,15,4];offset=vector(5);dim=0;for(i=1,5,offset[i]=dim;dim+=8*lens[i]);assert(dim==512,"complete geometric jet dimension");
rootsat=vector(5);phiJets=vector(dim,i,0*o);baseJets=vector(3,z,matrix(dim,188,i,j,0*o));
localvalue(co,point,T0,rr,L,M=0)={my(v=0*o+O(u^L));if(point<=4,for(mask=0,15,if(co[mask+1]!=0,v+=subst(co[mask+1],T,T0)*prod(j=1,4,if(bittest(mask,j-1),rr[j],o)))),for(mask=0,15,for(j=max(0,(M-hammingweight(mask)-L+2)\2),if(co[mask+1]==0,-1,poldegree(co[mask+1],T)),my(e=M-2*j-hammingweight(mask));assert(e>=0,"infinity pole bound");if(e<L,my(cc=polcoef(co[mask+1],j,T));if(cc!=0,v+=cc*u^e*prod(t=1,4,if(bittest(mask,t-1),rr[t],o)))))));return(v);};
completed=0;
{for(point=1,5,my(L=lens[point],T0=if(point<=4,-o/sl[point]+u^2/sl[point]+O(u^(L+2)),0),rr=vector(4),others=if(point<=4,select(j->j!=point,[1,2,3,4]),[2,3,4]));
for(j=1,4,if(point<=4,if(j==point,rr[j]=u+O(u^(L+2)),my(c=o-sl[j]/sl[point]);rr[j]=sqrt(c)*sqrt(o+(sl[j]/sl[point]/c)*u^2+O(u^(L+2)))),rr[j]=sqrt(sl[j])*sqrt(o+u^2/sl[j]+O(u^(L+2)))));
rootsat[point]=rr;
for(signs=0,7,my(r=rr);for(t=1,3,if(bittest(signs,t-1),r[others[t]]=-r[others[t]]));my(pj=localvalue(phi,point,T0,r,L,96));assert(polcoef(pj,0,u)!=0,"torsion function unit at every cut point");assert(valuation(pj^24360-o,u)>=L,"full local period");for(k=0,L-1,phiJets[offset[point]+signs*L+k+1]=polcoef(pj,k,u));
for(z=1,3,for(col=1,188,my(fj=localvalue(bases[z][col],point,T0,r,L,32*(z+2)-72));for(k=0,L-1,baseJets[z][offset[point]+signs*L+k+1,col]=polcoef(fj,k,u))));
);completed++;print("LOCAL point=",point," length=",L," all 8 sign points and 564 frame columns verified");)}
if(completed!=5,quit(1));
rows=List();
{for(point=1,4,for(mask=0,15,for(j=0,6,listput(rows,[point,mask,2*j+bittest(mask,point-1)]))));
for(mask=0,15,my(s=hammingweight(mask));for(k=0,3-s,if(k%2==s%2,listput(rows,[5,mask,k]))));}
assert(#rows==460,"complete shared cut row pool");
perms=vector(24,i,numtoperm(4,i-1)); selections=vector(24);
{for(pi=1,24,my(sel=List(),order=perms[pi]);for(pos=1,4,my(point=order[pos]);for(mask=0,15,my(e=bittest(mask,point-1),bi=(2^(pos-1)-1)*e+2^(pos-1)*sum(j=pos+1,4,1-bittest(mask,order[j]-1)));for(j=0,bi-1,listput(sel,(point-1)*112+mask*7+j+1))));for(j=449,460,listput(sel,j));selections[pi]=Vec(sel);assert(#sel==188,"all reordered full cuts"));}
W=matrix(460,dim,i,j,0*o);
{for(row=1,460,my(point=rows[row][1],mask=rows[row][2],target=rows[row][3],L=lens[point],others=if(point<=4,select(j->j!=point,[1,2,3,4]),[2,3,4]),inv=1/prod(j=1,4,if(bittest(mask,j-1)&&j!=point,rootsat[point][j],o)));if(point==5,inv=1/prod(j=1,4,if(bittest(mask,j-1),rootsat[point][j],o)));
for(signs=0,7,my(sgn=(-1)^sum(t=1,3,bittest(signs,t-1)*bittest(mask,others[t]-1)));for(k=0,target,W[row,offset[point]+signs*L+k+1]=sgn*o/8*polcoef(inv,target-k,u)));)}
out="research/results/bmd-twenty-nine-paired-20261009/local-data-second.txt";
write(out,"2 ",Strjoin(apply(x->Str(lift(x)),Vecrev(modulus))," "));write(out,code(a));for(pi=1,24,write(out,Strjoin(apply(j->Str(j-1),selections[pi])," ")));write(out,Strjoin(apply(x->Str(code(x)),phiJets)," "));
for(z=1,3,for(i=1,dim,write(out,Strjoin(vector(188,j,Str(code(baseJets[z][i,j])))," "))));
for(i=1,460,write(out,Strjoin(vector(dim,j,Str(code(W[i,j])))," ")));
{for(z=1,3,my(pool=W*baseJets[z],A=matrix(188,188,i,j,pool[selections[1][i],j]));
for(row=1,460,my(point=rows[row][1],mask=rows[row][2],target=rows[row][3],j=if(point<=4,(target-bittest(mask,point-1))/2,(32*(z+2)-72-hammingweight(mask)-target)/2));for(col=1,188,my(P=bases[z][col][mask+1],expected=if(point<=4,polcoef(subst(P,T,-o/sl[point]+u),j,u)/sl[point]^j,polcoef(P,j,T)));assert(pool[row,col]==expected,"direct polynomial full-cut equality")));
print("BASE degree=",z+2," rank=",matrank(A));for(i=1,188,write(out,Strjoin(vector(188,j,Str(code(A[i,j])))," "))));}
print("FIELD ",modulus," unused_embedding_code=",code(a));
print("COMPLETE 512 geometric jets, all 460 pool cuts, all 24 orders, direct polynomial equality, period24360.");

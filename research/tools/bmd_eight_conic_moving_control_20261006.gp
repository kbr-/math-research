\\ Same d8,q729 moving-coefficient test, now at the exact fourth-merge conic.
\\ Profiles are saturated via their complete missing-coefficient constraints.
\\ Correct lower multiplier is tau^alpha v*w^4 modulo tau^N.
default(parisizemax,3000000000);
default(nbthreads,1);
setrand(20261006);
if(default(nbthreads)!=1,error("threads"));
assert(c,msg)={if(!c,error(msg));};
profile(c,m)={my(top=2*c+if(m==3,1,3),rows=if(m==3,[1,3,5],[1,3,5,2*c+2]),piv=List(),B=matrix(#rows,0),rank=0);forstep(j=top,0,-1,my(col=vector(#rows,i,Mod(binomial(j,rows[i]),3))~);my(C=matconcat([B,Mat(col)]));if(matrank(C)>rank,listput(piv,j);B=C;rank++);if(rank==#rows,break));assert(rank==#rows,"full profile constraint rank");select(j->!setsearch(Set(Vec(piv)),j),[0..top]);};
rowsW(d,v,w,N)={my(c=8*d-17,EA=profile(c,3),EB=profile(c,2),A=concat([1,T,T^2],apply(e->v^2*w^4*T^e,EA)),B=concat([1,T],apply(e->w^4*T^e,EB)));assert(#A==2*c+2 && #B==2*c+2,"full cut dimensions");print("d=",d," c=",c," EA_tail=",EA[max(1,#EA-9)..#EA]," EB_tail=",EB[max(1,#EB-9)..#EB]);concat(concat(apply(f->v*f,A),apply(f->w^3*f,A)),concat(apply(f->v^2*f,B),apply(f->v*w^3*f,B)));};
{
my(d=8,q=729,alpha=365,N=704,modulus=ffinit(3,8,'a),a=ffgen(modulus,'a),o=a^0);
my(aa=vector(7,i,random(a)));while(#Set(aa)!=7 || prod(i=1,7,aa[i])==0,aa=vector(7,i,random(a)));
my(v=sqrt(o-aa[1]*T+O(T^N)),w=sqrt(o+(aa[2]-aa[1])*T+O(T^N)));
assert(valuation(v^(1-q)-v,T)>=N,"Frobenius removes the mark-unit exponent");
my(U=rowsW(8,v,w,N),V=rowsW(7,v,w,N),R=concat(U,apply(f->T^alpha*v*w^4*f,V)));
assert(#U==384 && #V==320 && #R==N,"moving source dimensions");
print("FIELD=",modulus," seed=20261006 slopes=",aa[1..2]);
my(M=matrix(N,N,i,j,polcoef(R[j],i-1,T)),det=matdet(M));
print("CONIC n8 d8 q729 alpha365 N704 determinant=",det);
if(det==0,print("rank=",matrank(M)," no generic failure inferred from one point."));
print("DONE same-degree conic mechanism test.");
}
quit;

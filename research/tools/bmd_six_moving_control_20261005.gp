\\ Smallest supported moving coefficient: n=6,d=4,p=3,q=81,alpha=41,N=80.
\\ Compare original shifted lower blocks with their characteristic-safe conic degeneration.
setrand(20261005);default(parisizemax,1000000000);
rowsV(aa,j,N)={my(w=vector(#aa,k,sqrt(1+aa[k]*T+O(T^N))),R=List());for(mask=0,2^#aa-1,for(k=0,(j-hammingweight(mask))\2,if(2*k+hammingweight(mask)<=j,listput(R,T^k*prod(l=1,#aa,if(bittest(mask,l-1),w[l],1))))));Vec(R);};
rowsZ(a1,a3,j,N)={my(l1=1+a1*T+O(T^N),l3=1+a3*T+O(T^N),w1=sqrt(l1),w3=sqrt(l3),base=l1^(1-j)*l3^(2-2*j),sh=[l3^2,w3*l1,w1/l1*l3^2,w1*w3],R=List());for(s=1,4,for(k=0,4*j-5,listput(R,base*sh[s]*T^k)));Vec(R);};
{
my(p=3,g=ffgen(3^6,'a),o=g^0,N=80,alpha=41);
for(trial=1,3,
 my(aa=vector(5,k,random(g)));while(#Set(aa)!=5 || prod(k=1,5,aa[k])==0,aa=vector(5,k,random(g)));
 my(U=rowsV(aa,4,N),V=rowsV(aa,3,N),R=concat(U,apply(f->f*T^alpha,V)));
 if(#R!=N,error("original row count"));
 my(rr=matrank(matrix(N,N,i,j,polcoef(R[i],j-1,T))));
 my(z1=aa[1],z3=aa[2],Z=concat(rowsZ(z1,z3,4,N),apply(f->f*T^alpha,rowsZ(z1,z3,3,N))));
 my(zr=matrank(matrix(N,N,i,j,polcoef(Z[i],j-1,T))));
 print("trial=",trial," slopes=",aa," original_moving_rank=",rr," conic_moving_rank=",zr);
);
}
quit;

\\ Shared exact character bases and marked jets for the separated root-curve computations.
\\ Coefficient positions are absolute: Vec(series) would discard leading zeros at mark zero.
rootbasis(n,d)={my(v=List());for(S=0,2^n-1,if(hammingweight(S)<=d,for(j=0,(d-hammingweight(S))\2,listput(v,[S,j]))));Vec(v);};
rootjets(labels,mark,wval,I,N)={
 my(n=#labels,one=labels[1]^0,maxd=vecmax(apply(v->2*v[2]+hammingweight(v[1]),I)));
 if(#Set(labels)!=n || prod(i=1,n,labels[i])==0,error("distinct nonzero root labels required"));
 if(#wval!=n || N<1,error("invalid marked jet dimensions"));
 my(roots=vector(n,i,wval[i]*sqrt(one+labels[i]/(one+labels[i]*mark)*T+O(T^N))),products=vector(2^n),co=vector(#I));
 for(i=1,n,if(valuation(roots[i]^2-(one+labels[i]*mark+labels[i]*T),T)<N,error("marked root-square identity")));
 products[1]=one+O(T^N);
 for(S=1,2^n-1,if(hammingweight(S)<=maxd,my(b=valuation(S,2));products[S+1]=products[S-2^b+1]*roots[b+1]));
 for(j=1,#I,my(v=(mark+T)^I[j][2]*products[I[j][1]+1]);co[j]=vector(N,r,polcoef(v,r-1,T)));
 matrix(N,#I,r,j,co[j][r])
};

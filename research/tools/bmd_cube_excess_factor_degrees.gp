p=2^61-1;
f=factor(Mod(1,p)*G);
print(vector(#f~,k,[poldegree(f[k,1]),f[k,2]]));

\\ Rank screen of the retained failed axis input; exact old source only.
z='z;T='T;
read("research/results/bmd-axis-parity-20261010/rank-data.gp");
{
my(n=DATA[1],p=DATA[2],e=DATA[3],g=ffgen(Mod(1,p)*Polrev(DATA[4],z),'g),o=g^0,m=n*(n+1)/2+2,r=n*(n-1)/2+2,
aa=concat([0*o],vector(n-1,i,sum(j=0,e-1,DATA[5][i][j+1]*g^j))),rows=List([vector(m+1,j,if(j==1,o,0*o)),vector(m+1,j,if(j==2,o,0*o))]));
for(i=1,n,for(j=i+1,n,
my(F=sqrt((o+aa[i]*T)*(o+aa[j]*T)+O(T^(m+1))));
listput(rows,vector(m+1,c,polcoef(F,c-1,T)))
));
my(M=matrix(r,m+1,i,j,rows[i][j]));
print("OLD_PREFIX_RANK=",matrank(matrix(r,r,i,j,M[i,j])),"/",r);
print("OLD_EXTENDED_RANK=",matrank(M),"/",r);
print("AXIS_RANK_DIAGNOSTIC_COMPLETED");
}
quit;

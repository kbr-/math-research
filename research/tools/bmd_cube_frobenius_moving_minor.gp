\\ Test the actual moving coefficient for n4,d2,p13: r8,s4,N12,alpha7.
\\ After homogeneous scaling set a1=1; retain symbolic a2=u,a3=v.
\\ Its vanishing as a polynomial decides whether this proposed coefficient
\\ can certify this first known-normal member of the p=5 mod8 family.
\\ One exact 12x12 determinant over F13[u,v]; no parameter sweep.
\\ Stages: construct truncated roots; build E and shifted F; determinant;
\\ retain the complete matrix and determinant for independent inspection.
T='T; u='u; v='v;
basis(nn,dd,roots)=if(dd<0,[],if(nn==0,vector(dd\2+1,j,T^(j-1)),concat(basis(nn-1,dd,roots),roots[nn]*basis(nn-1,dd-1,roots))));
{
my(pp=13,nn=4,dd=2,sz=12,al=7,aa=[1,u,v]);
my(roots=vector(3,i,(1+Mod(1,pp)*aa[i]*T)^al+O(T^sz)));
my(ev=basis(3,dd,roots),fv=basis(3,dd-1,roots));
my(rows=concat(ev,T^al*fv));
my(M=matrix(sz,sz,i,j,polcoef(rows[i],j-1,T)));
if(#ev!=8||#fv!=4,error("row counts"));
print("PARAMETERS n=4 d=2 p=13 r=8 s=4 N=12 alpha=7 a=[1,u,v]");
print("MOVING_MATRIX = ",lift(M));
my(res=matdet(M));
print("MOVING_DETERMINANT = ",lift(res));
print("MOVING_COEFFICIENT_ZERO = ",res==0);
print("MOVING_MINOR_TEST_COMPLETED");
}
quit;

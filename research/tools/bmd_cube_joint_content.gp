\\ Exact identity/normalization checks for the all-dimensional leading coefficient.
\\ No high-dimensional normality instances are enumerated.
\\ Checks: condensation rational identity, Catalan Toeplitz scaling,
\\ and one original integral five-row (n=2,d=2) parameter determinant.
\\ Full stdout is retained by tools/save-run-output.py.

s='s; h='h;
ratio1=(s-1)*(2*s-1)/((s+h)*(2*s+2*h-1));
ratio2=(2*h+1)*(2*s+h-1)/((s+h)*(2*s+2*h-1));
if(ratio1+ratio2!=1,error("condensation ratios"));
print("CONDENSATION_RATIO_SUM = ",ratio1+ratio2);
print("RATIO_A = ",ratio1);print("RATIO_B = ",ratio2);
cat(k)=binomial(2*k,k)/(k+1);
hankel(sz,shift)=matdet(matrix(sz,sz,i,j,cat(shift+i+j-2)));
productform(sz,shift)=prod(j=1,shift-1,prod(i=1,j,(2*sz+i+j)/(i+j)));
{
my(cases=[[3,0],[3,1],[2,2],[4,4]],sz,shift,r,H,B,expected);
for(k=1,#cases,
  sz=cases[k][1];shift=cases[k][2];r=sz+shift;
  H=hankel(sz,shift);
  if(H!=productform(sz,shift),error("Hankel product control"));
  B=matdet(matrix(sz,sz,i,j,binomial(1/2,r+j-i)));
  expected=(-1)^(sz*shift+sz*(sz-1)/2)*H/2^(2*r*sz-sz);
  if(B!=expected,error("Toeplitz scaling control"));
  print("CONTROL s=",sz," h=",shift," Hankel=",H," Toeplitz=",B);
);
if(hankel(2,2)!=3,error("odd-factor negative control"));
}

T='T; y1='y1; y2='y2;
zbasis(nn,dd,roots)=if(dd<0,[],if(nn==0,vector(dd\2+1,j,T^(j-1)),concat(zbasis(nn-1,dd,roots),roots[nn]*zbasis(nn-1,dd-1,roots))));
coeffdet(nn,dd,roots)={my(v=zbasis(nn,dd,roots),sz=#v);matdet(matrix(sz,sz,i,j,polcoef(v[i],j-1,T)))};
{
my(roots=[(1-sqrt(1+4*y1*T+O(T^5)))/2,(1-sqrt(1+4*y2*T+O(T^5)))/2]);
my(full=coeffdet(2,2,roots),left=coeffdet(1,2,roots),right=coeffdet(1,1,roots));
my(r=3,sz=2,shift=1,sgn=(-1)^(sz*shift+sz*(sz-1)/2+sz));
my(top=polcoef(full,r*sz,y2),expected=sgn*hankel(sz,shift)*left*right);
if(poldegree(full,y2)!=r*sz,error("degree control"));
if(top!=expected,error("integral normalization control"));
print("INTEGRAL_DELTA_n2_d2 = ",full);
print("CHILD_DELTA_d2 = ",left," CHILD_DELTA_d1 = ",right);
print("TOP_COEFFICIENT_y2^6 = ",top," EXPECTED = ",expected);
print("ALL_IDENTITY_AND_NORMALIZATION_CONTROLS_PASSED");
}
quit;

\\ Characteristic-three Schur-frame encoding control, four labels 0,a,b,c.
\\ This is the already solved rank-six pair model, not a dimension survey.
\\ Verify all polynomial coefficient columns 0..8 by independent monic
\\ alternant reduction, the compound determinant and a wrong-column control.
\\ All divisions are monic reductions or by powers of two, never factorials.
X='X; Y='Y; a='a; b='b; c='c;
{
my(aa=[0,a,b,c],pairs=[[0,1],[0,2],[0,3],[1,2],[1,3],[2,3]]);
my(one=Mod(1,3),rr=6,ss=(X+Y)*one,dd=(X-Y)^2*one);
my(q=vector(9));q[1]=one;
for(l=1,8,q[l+1]=ss*q[l]+dd*sum(j=0,l-2,q[j+1]*q[l-1-j]));
my(pp=X*(X-a)*(X-b)*(X-c)*one);
my(rems=vector(10,j,lift(Mod(X^(j-1)*one,pp))));
my(frame=matrix(rr,rr),coords=matrix(rr,9),raw=matrix(rr,9));
for(t=1,rr,
  my(x=aa[pairs[t][1]+1],y=aa[pairs[t][2]+1]);
  for(k=1,rr,my(u=pairs[k][1],v=pairs[k][2]);
    frame[t,k]=one*x^u*y^u*sum(j=0,v-u-1,x^j*y^(v-u-1-j)));
  for(l=0,8,raw[t,l+1]=subst(subst(q[l+1],X,x),Y,y)));
for(l=0,8,
  my(anti=(Y-X)*q[l+1],red=0);
  for(u=0,l+1,for(v=0,l+1-u,
    my(co=polcoef(polcoef(anti,u,X),v,Y));
    if(co!=0,red+=co*rems[u+1]*subst(rems[v+1],X,Y))));
  for(k=1,rr,coords[k,l+1]=polcoef(polcoef(red,pairs[k][1],X),pairs[k][2],Y));
  my(rebuilt=sum(k=1,rr,coords[k,l+1]*(X^pairs[k][1]*Y^pairs[k][2]-X^pairs[k][2]*Y^pairs[k][1])));
  if(red!=rebuilt,error("alternant reduction failed at ",l)));
if(frame*coords!=raw,error("pair coefficient encoding failed"));
my(vand=prod(t=1,rr,aa[pairs[t][2]+1]-aa[pairs[t][1]+1])*one);
if(matdet(frame)!=vand^2,error("Schur compound determinant failed"));
my(root=vector(11));root[1]=one;
for(j=1,10,root[j+1]=(if(j==1,ss,if(j==2,X*Y*one,0))-sum(i=1,j-1,root[i+1]*root[j-i+1]))/2);
for(l=0,8,if(root[l+3]!=dd*q[l+1],error("original root coefficient mismatch ",l)));
my(wrong=coords);wrong[1,1]+=one;
if(frame*wrong==raw,error("wrong column was not detected"));
print("FIELD = F3(a,b,c); LABELS = [0,a,b,c]; PAIR_RANK = 6");
print("ALL_COEFFICIENT_ENTRIES_CHECKED = ",rr*9);
print("ORIGINAL_ROOT_COEFFICIENTS_CHECKED = 9");
print("COORDINATE_MATRIX = ",coords);
print("FRAME_DETERMINANT = ",matdet(frame));
print("NORMALIZED_PREFIX_DETERMINANT = ",matdet(matrix(rr,rr,i,j,coords[i,j])));
print("WRONG_COLUMN_DETECTED = 1");
print("ODD_SCHUR_FRAME_CONTROL_COMPLETED");
}
quit;

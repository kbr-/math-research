\\ Reuse the completed five-root symbolic Schur matrix; compute only its
\\ next column. Test whether its squarefree normalized boundary factors
\\ persist in the augmented prefix in characteristic three.
\\ This is an original boundary-threshold control, not a longer order table.
X='X; Y='Y; e1='e1; e2='e2; e3='e3; e4='e4; e5='e5;
{
my(lines=readstr("research/results/cube-coefficient-sensitive-route-review-20260928/cms-control.txt"));
my(C=0,phi=0);
for(i=1,#lines,my(parts=strsplit(lines[i],"="));
  if(#parts==2,
    if(parts[1]=="SCHUR_COORDINATES ",C=eval(parts[2]));
    if(parts[1]=="PHI ",phi=eval(parts[2]))));
if(type(C)!="t_MAT"||matsize(C)!=[10,10],error("saved Schur matrix absent"));
my(one=Mod(1,3),pairs=List());
for(i=0,4,for(j=i+1,4,listput(pairs,[i,j])));pairs=Vec(pairs);
my(pp=(X^5-e1*X^4+e2*X^3-e3*X^2+e4*X-e5)*one);
my(rems=vector(12,j,lift(Mod(X^(j-1)*one,pp))));
\\ q_10=s^10 by the recorded q=9 digit-block formula.
my(anti=(Y-X)*(X+Y)^10*one,red=0);
for(i=0,11,for(j=0,11-i,
  my(co=polcoef(polcoef(anti,i,X),j,Y));
  if(co!=0,red+=co*rems[i+1]*subst(rems[j+1],X,Y))));
my(next=vector(10,k,polcoef(polcoef(red,pairs[k][1],X),pairs[k][2],Y))~);
my(aug=matconcat([C,next]),center=matrix(10,11,i,j,subst(aug[i,j],e1,0)));
\\ Pivot the seven already computed constant columns; no new determinants
\\ of size ten are needed.
my(pivots=[1,2,3,4,7,9,10],rest=[5,6,8],unit=matrix(7,7,i,j,center[pivots[i],j]));
if(matdet(unit)!=one,error("constant pivot block changed"));
my(tail=matrix(3,4,i,j,center[rest[i],j+7])
  -matrix(3,7,i,j,center[rest[i],j])*unit^-1
     *matrix(7,4,i,j,center[pivots[i],j+7]));
my(corephi=matdet(matrix(3,3,i,j,tail[i,j])));
if(corephi!=subst(phi,e1,0),error("pivot sign or normalized boundary mismatch"));
my(minors=vector(4));
for(j=1,4,
  my(cols=select(k->k!=j,[1,2,3,4]));
  minors[j]=(-1)^(j-1)*matdet(matrix(3,3,r,s,tail[r,cols[s]])));
if(tail*minors~!=vector(3)~,error("signed cofactor kernel failed"));
my(g=0);for(i=1,4,g=gcd(g,minors[i]));
print("FIELD = F3[e2,e3,e4,e5]; SOURCE = saved unanchored Schur prefix");
print("NEW_q10_COORDINATES = ",next);
print("CENTERED_RESIDUAL_3_BY_4 = ",tail);
print("SIGNED_CORE_MINORS = ",minors);
print("COMMON_GCD = ",g);
print("NORMALIZED_BOUNDARY = ",corephi);
print("TOP_PRIMITIVE_COEFFICIENT = ",minors[4]/g);
my(points=[[0,0,1,1],[1,0,0,0],[1,1,0,2]]);
my(columns=[[2,3,4],[1,2,4],[1,2,4]],expected=[1,2,1]);
for(i=1,3,
  my(mm=matrix(3,3,r,s,substvec(tail[r,columns[i][s]],[e2,e3,e4,e5],points[i])));
  my(det=matdet(mm));
  if(det!=expected[i]*one,error("component witness failed ",i));
  print("COMPONENT_WITNESS ",i," POINT = ",points[i],
        " COLUMNS = ",columns[i]," DETERMINANT = ",det));
print("SIGNED_COFACTOR_IDENTITY_CHECKED = 1");
print("TERNARY_BOUNDARY_NEXT_COLUMN_COMPLETED");
}
quit;

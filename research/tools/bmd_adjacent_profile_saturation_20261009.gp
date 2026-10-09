\\ Exact bounded constant-root saturation test for the r=1 elliptic source.
\\ A=F_s+g(1+ep*T)^4*T^s, g=(1+T)(1+b*T)^2, p>19, p|s.
\\ Twelve complete high coefficient constraints, not selected source rows.
default(parisizemax,1000000000);
default(nbthreads,1);
ep='ep;b='b;
assert(c,msg)=if(!c,print("FAIL ",msg);quit(1));
H=32;P=64;
gc=[1,1+2*b,2*b+b^2,b^2];
G(j)=sum(l=0,3,if(j>=l&&j-l<=4,gc[l+1]*binomial(4,j-l)*ep^(j-l),0));
coef(e,v)=if(e<v,0,(-1)^(e-v)*binomial(e,e-v));
rows(s)={my(A=matrix(3,3,i,j,(-1)^(2*s+12+j-(2*i-1))*binomial(2*s+12+j,2*i-1)),R=matrix(12,H));for(h=0,H-1,my(e=2*s+12-h,al=-A^-1*vector(3,i,(-1)^(e-(2*i-1))*binomial(e,2*i-1))~,fc=vector(22,k,coef(e,2*s+k-1)+sum(j=1,3,al[j]*coef(2*s+12+j,2*s+k-1))),E=vector(8,j,sum(u=j-1,7,fc[2*u+1]*binomial(s+u,u-j+1))),O=vector(11,j,my(v=j-4);sum(u=v,4,fc[7+2*u+1]*binomial(s+u,u-v))),fac=2^(12-h)*ep^h);for(j=2,7,R[j-1,h+1]=fac*(G(1)*ep^j*E[j+1]-G(j)*ep*E[2]);R[6+j-1,h+1]=fac*(G(1)*sum(l=0,3,gc[l+1]*ep^(j+3-l)*O[j-l+4])-G(j)*sum(l=0,3,gc[l+1]*ep^(4-l)*O[5-l]))));R;};
R=rows(0);
Rc=rows(23);
assert(Mod(1,23)*R==Mod(1,23)*Rc,"every full constraint entry agrees at the positive s=23 control");
OUT="research/results/bmd-elliptic-adjacent-profile-20261009/constraints.gp";
write(OUT,"\\\\ Complete bounded constraints, column h represents normalized core order 2s+12-h.");
write(OUT,"R=",R,";");
bad=1;
contents(v)={my(a=Vec(numerator(v)),d=Vec(denominator(v)),den=1);for(i=1,#a,assert(type(a[i])=="t_INT"||type(a[i])=="t_FRAC","one-variable rational numerator");den=lcm(den,denominator(a[i])));for(i=1,#d,assert(type(d[i])=="t_INT"||type(d[i])=="t_FRAC","one-variable rational denominator");den=lcm(den,denominator(d[i])));[content(a*den),content(d*den)];};
checkden(v)={if(type(v)=="t_POL"&&variable(v)==ep,my(c=Vec(v));for(j=1,#c,bad=lcm(bad,abs(contents(c[j])[2]))),bad=lcm(bad,abs(contents(v)[2])));};
checknum(v)=bad=lcm(bad,abs(contents(v)[1]));
for(i=1,matsize(R)[1],for(j=1,H,checkden(R[i,j])));
write(OUT,"operations=List();");
depth=vector(12);divisionTotal=0;iterations=0;
{while(1,for(i=1,12,my(v=vecmin(vector(H,j,valuation(R[i,j],ep))));assert(v<P,"nonzero polynomial row");if(v>0,write(OUT,"listput(operations,[",i,",-",v,"]); ");R[i,]=R[i,]/ep^v;depth[i]+=v;divisionTotal+=v));my(LC=matrix(12,H,i,j,polcoef(R[i,j],0,ep)),K=matker(LC~));if(matsize(K)[2]==0,break);my(v=K[,1],ri=0,newDepth=0);for(i=1,12,if(v[i]!=0,ri=i;newDepth=max(newDepth,depth[i])));v=v/v[ri];for(i=1,12,checkden(v[i]));write(OUT,"listput(operations,[",ri,",",v,"]); ");R[ri,]=sum(i=1,12,v[i]*R[i,]);depth[ri]=newDepth;iterations++;assert(iterations<=12*(H+9),"polynomial minor degree bounds saturation steps");print("SATURATION iteration=",iterations," constant_rank=",12-matsize(K)[2]," max_depth=",vecmax(depth)));}
LC=matrix(12,H,i,j,polcoef(R[i,j],0,ep));
assert(matrank(LC)==12,"all primitive rows independent");
assert(vecmax(depth)<H,"omitted columns still vanish after all row operations");
primeAudit=0;
my(ij=matindexrank(LC));my(det=matdet(matrix(12,12,i,j,LC[i,ij[2][j]])));checkden(det);checknum(det);print("EXCLUDED_PRIMES ",factor(bad)[,1]~);write(OUT,"rankColumns=",ij[2],"; rankMinor=",det,"; excludedPrimes=",factor(bad)[,1]~,";");primeAudit=1;
print("POLE_DEPTHS ",depth," division_total=",divisionTotal);
print("ORDINARY_TOP12_RANK ",matrank(LC[,1..12]));
write(OUT,"primitive=",LC,";");
write(OUT,"poleDepths=",depth,";");
assert(primeAudit==1,"prime audit completed");
print("COMPLETE twelve source constraints; one positive-parameter encoding control; symbolic primitive rows retained.");
quit;

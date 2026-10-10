\\ Independent exact coefficient proof of the N4 formal secant identities.
default(parisize,128000000);
z1='z1;z2='z2;z3='z3;t1='t1;t2='t2;t3='t3;B='B;C='C;E='E;
alt(t,z)=matdet(matrix(3,3,i,j,if(j==1,z[i+1],if(j==2,z[i+1]^2,t[i+1]))));
{
my(z=[0,z1,z2,z3],t=[0,t1,t2,t3],rows=List());
for(i=1,4,for(j=i+1,4,listput(rows,[1,z[i]+z[j],-z[i]^2-z[j]^2,t[i]+t[j],-t[j]*z[i]-t[i]*z[j],t[j]*z[i]^2+t[i]*z[j]^2])));
my(D=matdet(matrix(6,6,i,j,Mod(1,3)*rows[i][j])),A=alt(t,z),A2=alt(vector(4,i,t[i]^2),z),claim=Mod(1,3)*A*(2*A2-(t1+t2+t3)*A));
if(D!=claim,error("Factor identity"));
my(V=z1*z2*z3*(z2-z1)*(z3-z1)*(z3-z2),e1=z1+z2+z3,e2=z1*z2+z1*z3+z2*z3,e3=z1*z2*z3,
 actual=subst(subst(subst(D,t1,z1^3),t2,z2^3),t3,z3^3));
if(actual!=Mod(1,3)*V^2*(e1^3-e1*e2-e3),error("Original control"));
my(graph=subst(subst(subst(D,t1,B*z1+C*z1^2+E*z1^3),t2,B*z2+C*z2^2+E*z2^3),t3,B*z3+C*z3^2+E*z3^3),
 expect=Mod(1,3)*E*V^2*(C*(B-C*e1)+C*E*e2+E^2*(e1^3-e1*e2-e3)));
if(graph!=expect,error("Graph identity"));
my(normal=0);
for(i=0,6,for(j=0,6,for(k=0,6,
 my(cc=polcoef(polcoef(polcoef(D,i,z1),j,z2),k,z3));
 if(cc!=0,normal+=cc*z1^(i%3)*z2^(j%3)*z3^(k%3)*t1^(i\3)*t2^(j\3)*t3^(k\3));
)));
my(P0=polcoef(polcoef(polcoef(normal,0,z1),0,z2),0,z3),P12=polcoef(polcoef(polcoef(normal,1,z1),2,z2),0,z3));
if(P0!=Mod(1,3)*t1*t2*t3*(t1^2+t2^2+t3^2+t1*t2+t1*t3+t2*t3),error("Constant residue"));
if(P12!=Mod(1,3)*t1*t3^2*(t3-t1),error("Mixed residue"));
print("PARI_FACTOR_GRAPH_AND_RESIDUES_PASS");
print("P000=",P0);print("P120=",P12);
print("NORMAL_RESIDUES=",normal);
print("SECANT_SYMBOLIC_INDEPENDENT_COMPLETED");
}
quit;

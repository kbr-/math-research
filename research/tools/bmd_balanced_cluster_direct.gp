\\ Independent check of the SAME simultaneous 3+3 test against the original
\\ square-root Hasse matrix, without Laurent saturation.
\\ Prediction from the retained saturation trace: exact epsilon valuation49.
\\ One 15x15 polynomial determinant after eliminating original rows1,T.
default(parisizemax,256000000);
default(parisize,64000000);
eps='t;
bet(j)={my(v=if(j%3==1,-1,1));j=j\3;while(j>0,if(j%3==2,return(0));j=j\3);v};
{
my(ff=ffinit(3,3,'a),g=ffgen(ff,'a),one=g^0);
my(roots=[0,eps,eps*g,1,1+eps*g^2,1+eps*(1+g)],pairs=List());
for(i=1,6,for(j=i+1,6,listput(pairs,[i,j])));pairs=Vec(pairs);
my(A=matrix(15,15,i,j,sum(u=0,j+1,one*bet(u)*bet(j+1-u)*roots[pairs[i][1]]^u*roots[pairs[i][2]]^(j+1-u))));
print("FIELD_MODULUS = ",ff);
print("ORIGINAL_BRANCH_ROOTS = ",roots);
print("ORIGINAL_17x17_HASSE_DETERMINANT = det(pair coefficients T2..T16)");
my(dd=matdet(A));
print("DETERMINANT = ",dd);
if(dd==0,error("direct determinant zero"));
my(vv=valuation(dd,eps));
print("EPSILON_VALUATION = ",vv);
print("LEADING_COEFFICIENT = ",polcoef(dd,vv,eps));
if(vv!=49,error("valuation contradicts retained saturation trace"));
print("DIRECT_ORIGINAL_DETERMINANT_CHECK_COMPLETED");
}
quit;

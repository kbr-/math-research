\\ Independent PARI coefficient, determinant and Hasse-support checks.
assert(c,s)=if(!c,error(s));
main()={
 my(one=Mod(1,3), sq=sqrt(one+one*z+O(z^15)), coeff=vector(15,k,lift(polcoef(sq,k-1))));
 assert(coeff==[1,2,1,1,2,1,0,0,0,1,2,1,1,2,1],"Hasse coefficient support");
 my(c=vector(10,k,one*polcoef((x*r-1)^9+r*(x*r-1)^8+r^4*(x*r-1)^5+r^8*(x*r-1)-t*r^9,k-1,r)));
 my(U=matrix(3,3,i,j,c[4-i+j]), V=matrix(3,3,i,j,c[6-i+j]));
 assert(matdet(U)==one,"unramified minor");assert(matdet(V)==one*x^3*(x^3-1),"branch minor");
 my(b=varhigher("branch"), f=one*(b^9+b^8+b^5+b-t), J=matrix(3,3,i,j,polcoef((one*b^(8+i))%f,5+j,b)));
 assert(matdet(J)!=0,"infinity minor");
 print("HASSE_COEFFICIENTS_0_TO_14=",coeff);
 print("UNRAMIFIED_DETERMINANT=",lift(matdet(U)));
 print("BRANCH_DETERMINANT=",lift(matdet(V)));
 print("INFINITY_PROJECTED_MATRIX=",lift(J));
 print("INFINITY_DETERMINANT=",lift(matdet(J)));
 print("PARI_EIGHTH_ROOT_JET_IDENTITIES_COMPLETED");
};
iferr(main(),E,print(E);quit(1));
quit;

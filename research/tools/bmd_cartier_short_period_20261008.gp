\\ Verify the smaller semilinear period on both fixed curves; no jet or order recount.
\\ Frobenius norm matrices have characteristic coefficients in F3.
\\ Small exponent9*lcm(3^j-1,j1..4)=9360 gives the same stable projector as the old Fq bound.
default(nbthreads,1);
assert(c,s)={if(!c,error(s));};
{
my(Esmall=9*lcm(vector(4,j,3^j-1)),start=getwalltime());
for(ci=1,2,
 my(f=if(ci==1,3,8),modulus=if(f==3,Mod(1,3)*(a^3+2*a+2),ffinit(3,8,'a)),a=ffgen(modulus,'a),one=a^0,labels);
 if(f==3,labels=vector(9,i,a^(i-1)),my(lc=[508,5690,5164,3098,2894,6147,276,4463,174]);labels=apply(c->sum(j=0,7,(c\3^j)%3*a^j),lc));
 my(Elarge=9*lcm(vector(4,j,(3^f)^j-1)),count=0,total=0);
 for(S=1,511,my(g=(hammingweight(S)-1)\2);if(g>0,
  my(R=prod(i=1,9,if(bittest(S,i-1),one+labels[i]*T,one)),B=matrix(g,g,i,j,polcoef(R,3*(i-1)+2-(j-1),T)),D=matid(g)*one);
  forstep(j=f-1,0,-1,D=D*matrix(g,g,r,c,B[r,c]^(3^j)));
  my(cp=charpoly(D));for(j=0,g,assert(polcoef(cp,j)^3==polcoef(cp,j),"norm characteristic polynomial not overF3"));
  my(P=D^Esmall);assert(P==D^Elarge && P*P==P && D^4*(matid(g)*one-P)==matrix(g,g),"small/large stable projector mismatch");
  total+=matrank(P);count++
 ));
 assert(count==466 && total==if(f==3,744,769),"full stable dimensions");
 print("SHORT_PERIOD field_degree=",f," stable_rank=",total," blocks=",count," matrix_exponent=",Esmall," coefficient_period=",f*Esmall," old_period=",f*Elarge," all_projectors_equal=true")
);
print("SHORT_CARTIER_PERIOD_COMPLETED wall_ms=",getwalltime()-start);
}
quit;

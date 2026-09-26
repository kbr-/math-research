/* Exact falsifying control for reading global initial degree from a plane
   section alone. C=[s^5:s^4*t:s*t^4:t^5+s^2*t^3] over Q.
   Complete degree-one/two/three coefficient maps, and plane x0+x3=0.
   The notebook supplies the embedding and general-plane arguments. */
must(ok,msg)=if(!ok,error(msg));
{
  my(f=[1,u,u^4,u^5+u^3],quad=List(),cub=List(),M1,M2,M3,F,plane=[1,u,u^4],pq=List(),MP);
  print("SCOPE rational quintic control; all 4 linear, 10 quadratic, 20 cubic monomials; plane x0+x3=0");
  for(i=1,4,for(j=i,4,listput(quad,f[i]*f[j]);for(k=j,4,listput(cub,f[i]*f[j]*f[k]))));
  M1=matrix(6,4,i,j,polcoef(f[j],i-1));
  M2=matrix(11,#quad,i,j,polcoef(quad[j],i-1));
  M3=matrix(16,#cub,i,j,polcoef(cub[j],i-1));
  must(#quad==10 && #cub==20,"monomial inventory failed");
  must(matrank(M1)==4 && matrank(M2)==10 && matrank(M3)==16,"global coefficient ranks unexpected");
  F=1+u^3+u^5;
  must(gcd(F,deriv(F))==1,"plane section not reduced");
  for(i=1,3,for(j=i,3,listput(pq,(plane[i]*plane[j])%F)));
  MP=matrix(5,6,i,j,polcoef(pq[j],i-1));
  must(matrank(MP)==5,"plane quadratic coefficient rank unexpected");
  print("GLOBAL_LINEAR_MATRIX=",M1);
  print("GLOBAL_QUADRATIC_MATRIX=",M2);
  print("GLOBAL_RANKS degrees1,2,3 = ",[matrank(M1),matrank(M2),matrank(M3)]);
  print("GLOBAL_KERNEL_DIMENSIONS degrees1,2,3 = ",[4-matrank(M1),10-matrank(M2),20-matrank(M3)]);
  print("PLANE_POLYNOMIAL=",F," gcd_with_derivative=",gcd(F,deriv(F)));
  print("PLANE_QUADRATIC_MATRIX=",MP);
  print("PLANE_CONIC_KERNEL=",matker(MP));
  print("COHOMOLOGY h1(I_C(1)),h1(I_C(2)),h1(I_C(3)) = ",[6-matrank(M1),11-matrank(M2),16-matrank(M3)]);
  print("PASS alpha(C)=3, alpha(plane section)=2; plane conic has no global quadric lift");
}

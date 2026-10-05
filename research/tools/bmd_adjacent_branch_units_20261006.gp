\\ Decide compatibility of actual leading-coefficient unit conditions in char3.
\\ All degrees >=7 reduce to at most729 classes; no original Hasse matrix is built.
default(parisizemax,500000000);
default(nbthreads,1);
if(default(nbthreads)!=1,error("threads"));
tables(h)={my(L=List(),q=3);while(q<=2*h-2,my(c=vector(q));for(i=1,h-1,for(j=i,h-1,c[(i+j)%q+1]++));listput(L,[q,c]);q*=3);my(c=vector(q));for(i=1,h-1,for(j=i,h-1,c[(i+j)%q+1]++));listput(L,[q,c]);Vec(L)};
units(n)={my(h=2^(n-2),L=tables(h),P=L[#L][1],U=vector(P));for(k=1,#L,my(q=L[k][1],c=L[k][2],z=select(r->c[r+1]==c[1],[0..q-1]));if(vecmin(c)!=c[1],error("zero not minimum"));print("n=",n," q=",q," C0=",c[1]," minimizing_x=",z));for(d=0,P-1,my(x=-h*(2*d-n+2),v=0,high=0);for(k=1,#L,my(q=L[k][1],c=L[k][2]);v+=c[x%q+1]-c[1];if(k==#L,high=c[x%q+1]));if(v==0 && high,error("unresolved higher valuation"));U[d+1]=(v==0));print("n=",n," period=",P," unit_degree_residues=",select(d->U[d+1],[0..P-1]));[P,U]};
{
print("Stages: fixed pair-sum tables; all residue classes; adjacent-input intersection.");
print("Inventory: h64 has2016 pairs, h128 has8128 pairs; periods243 and729.");
my(A=units(8),B=units(9),P=B[1],adj=List(),full=List());
for(d=0,P-1,if(A[2][d%A[1]+1] && A[2][(d-1)%A[1]+1],listput(adj,d);if(B[2][d+1],listput(full,d))));
print("adjacent_dimension8_mod729=",Vec(adj));
print("full_dimension9_recursive_mod729=",Vec(full));
print("PASS: exact exhaustive arithmetic inventory complete.");
}

Hvalue(h,s)={my(a=1,b=1);for(i=1,h-1,for(j=i,h-1,a*=2*s+i+j;b*=i+j));if(a%b,error("integrality"));a/b};
residue_counts(h,s)={my(c=vector(27));for(j=0,s+h-1,c[(2*j)%27+1]++);for(j=0,s-1,c[(2*j+1)%27+1]++);c};
{
my(A=[0,1,19,20,21,22,23,24,25,26],B=[0..13],total=0);
print("Modulo27 proof control: all27 residues at h10 and20.");
for(k=1,2,my(h=if(k==1,10,20),allowed=if(k==1,A,B),found=List());
 for(x=0,26,my(s=(-14*x)%27,c=residue_counts(h,s),balanced=vecmax(c)-vecmin(c)<=1,H=Hvalue(h,s));
  if(balanced,listput(found,x),if(valuation(H,3)==0,error("failed necessary valuation")));
  print("h=",h," x=",x," s=",s," residue_counts=",c," balanced=",balanced);
 );
 if(Vec(found)!=allowed,error("wrong allowed table"));
);
print("Lift control: h10,37,64 and every x modulo27; actual integer factors.");
for(k=1,3,my(h=[10,37,64][k]);
 for(x=0,26,my(s=(-14*x)%27+27*ceil(h/27),c=residue_counts(h,s),c0=residue_counts(10,(-14*x)%27));
  if(vecmax(c)-vecmin(c)!=vecmax(c0)-vecmin(c0),error("periodic profile failed"));
  my(v=[valuation(Hvalue(h,s),3),valuation(Hvalue(h,s-h),3),valuation(Hvalue(2*h,2*s-h),3)]);
  if(vecmax(v)==0,error("recursive obstruction failed"));
  total++;
 );
);
my(s=27,v=[valuation(Hvalue(10,s),3),valuation(Hvalue(10,s-10),3),valuation(Hvalue(20,2*s-10),3)]);
if(v[1]!=0 || v[2]!=0 || v[3]==0,error("coupled negative control failed"));
print("Both lower factors can be units: h10 s27 valuations=",v);
print("PASS:54 complete residue profiles,81 lifted exact triple products, and coupled control.");
}
quit;

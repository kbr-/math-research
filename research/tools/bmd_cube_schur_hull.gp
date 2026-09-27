\\ Exact degree-two Schur hull encoding control, n=3 over Q[a,b,c].
\\ This is the smallest existing nonreflexive cyclic-image control: rank 8.
\\ Check every frame/connection entry, all coefficient columns 0..9,
\\ determinant, and a wrong half-density negative control. No parameter sweep.
X='X; a='a; b='b; c='c;
dv(f)=-a^2*deriv(f,a)-b^2*deriv(f,b)-c^2*deriv(f,c);
{
my(nn=3,aa=[0,a,b,c],pairs=List());
for(i=0,nn,for(j=i+1,nn,listput(pairs,[i,j])));
pairs=Vec(pairs);
my(ss=#pairs,rr=ss+2,pp=X*(X-a)*(X-b)*(X-c));
my(H=matrix(rr,rr),C=matrix(rr,rr),W=matrix(ss,ss));
H[1,1]=1;H[2,2]=1;C[2,1]=1;
for(t=1,ss,
  my(i=pairs[t][1]+1,j=pairs[t][2]+1,x=aa[i],y=aa[j]);
  H[t+2,1]=1;H[t+2,2]=(x+y)/2;C[t+2,t+2]=(x+y)/2;
  for(k=1,ss,my(u=pairs[k][1],v=pairs[k][2]);
    H[t+2,k+2]=(y-x)*(x^u*y^v-x^v*y^u)));
my(D=matrix(nn+1,nn+1));
for(u=0,nn,my(rem=lift(Mod(-(u+1/2)*X^(u+1),pp)));
  for(v=0,nn,D[v+1,u+1]=polcoef(rem,v,X)));
for(k=1,ss,my(u=pairs[k][1],v=pairs[k][2]);
  for(t=1,ss,my(i=pairs[t][1],j=pairs[t][2]);
    W[t,k]=D[i+1,u+1]*(j==v)-D[j+1,u+1]*(i==v)
      +(i==u)*D[j+1,v+1]-(j==u)*D[i+1,v+1]));
my(K=matrix(rr,rr));K[2,1]=1;K[3,2]=-1/4;
for(i=1,ss,for(j=1,ss,K[i+2,j+2]=W[i,j]));
my(dH=matrix(rr,rr,i,j,dv(H[i,j])),defect=dH+C*H-H*K);
if(defect!=matrix(rr,rr),error("connection intertwining failed"));
my(vand=prod(t=1,ss,aa[pairs[t][2]+1]-aa[pairs[t][1]+1]));
if(matdet(H)!=vand^(nn+1),error("compound determinant failed"));
my(z=vector(rr,i,i==1)~,checks=0);
for(k=0,9,
  my(raw=vector(rr,i,if(i==1,k==0,if(i==2,k==1,0)))~);
  for(t=1,ss,my(x=aa[pairs[t][1]+1],y=aa[pairs[t][2]+1]);
    raw[t+2]=sum(j=0,k,binomial(1/2,j)*binomial(1/2,k-j)*x^j*y^(k-j)));
  if(H*z!=raw,error("coefficient encoding failed at order ",k));
  checks+=rr;
  z=(vector(rr,i,dv(z[i]))~+K*z)/(k+1));
my(wrong=K);wrong[4,3]+=1/2;
if(dH+C*H-H*wrong==matrix(rr,rr),error("negative control missed"));
print("PARAMETERS n=3 d=2 field=Q[a,b,c] rank=8 pair_rank=6");
print("SCHUR_FRAME = ",H);
print("HULL_CONNECTION = ",K);
print("FRAME_DETERMINANT = ",matdet(H));
print("CONNECTION_ENTRIES_CHECKED = ",rr^2);
print("COEFFICIENT_ENTRIES_CHECKED_ORDERS_0_TO_9 = ",checks);
print("WRONG_HALF_DENSITY_DETECTED = 1");
print("SCHUR_HULL_CONTROL_COMPLETED");
}
quit;

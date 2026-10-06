"""Reference GP verification of joint transfer support and actual tied coefficients.
No original threshold is inferred: finite nonzero evaluations prove coefficients
nonzero, whereas zero evaluations alone do not prove polynomial vanishing.
"""
import argparse,json,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--data',required=True);p.add_argument('--control',required=True);p.add_argument('--out',required=True);a=p.parse_args()
data=json.loads(Path(a.data).read_text());controls=json.loads(Path(a.control).read_text())
code=r'''
default(parisizemax,1000000000);
bb(m) = vector(m+1,k,Mod(binomial(1/2,k-1),3));
tr(b,J,K) = matrix(#J,#K,i,j,if(K[j]<J[i],Mod(0,3),b[K[j]-J[i]+1]));
sel(A,cols) = matrix(matsize(A)[1],#cols,i,j,A[i,cols[j]+1]);
'''
code+=r'''
{
my(shapes=[[3,3,0,2],[5,5,1,3],[3,9,2,4],[3,9,3,4]],passed=0,nonzero=0);
setrand(20261006);
for(case=1,#shapes,
 my(p=shapes[case][1],q=shapes[case][2],t=shapes[case][3],s=shapes[case][4],alpha=(q+1)/2,a=t+1,m=q+t,r=m-s,D=s*alpha+a*(q-alpha),E,F,C,M,H);
 E=matrix(r,m+1,i,j,Mod(random(p),p));F=matrix(s,m+1,i,j,Mod(random(p),p));
 C=matrix(m+1,m+1,i,j,if(j<i,Mod(0,p),Mod(binomial(1/2,j-i),p)*X^(j-i)));
 M=matconcat([E;F*C]);
 H=matrix(m,m+1,i,j,if(i<=r,if(j<=q,E[i,j],0),if(j<=q,if(j>alpha,F[i-r,j-alpha],0),F[i-r,j-q])));
 for(omit=0,q-1,
  my(cols=select(k->k!=omit,vector(m+1,k,k-1)),actual=matdet(sel(M,cols)),pred=Mod(-1/2,p)^a*matdet(sel(H,cols)));
  if(poldegree(actual)>D||polcoef(actual,D)!=pred,error("rollover coefficient mismatch"));
  passed++;if(pred!=0,nonzero++)
 )
);
if(!nonzero,error("vacuous rollover controls"));
print("PASS rollover coefficient controls=",passed," nonzero=",nonzero);
}
'''
for c in controls:
 n=c['n'];m=c['m'];expected=[x['bound'] for x in c['cofactors']]
 code+=f'n={n};m={m};b=bb(m);expected={expected};\n'
 code+=r'''
{
my(supp=select(k->b[k+1]!=0,vector(m,k,k)),best=vector(m-1,k,-100000));
forsubset([#supp,n-1],ii,
 my(J=concat([0],vector(n-1,k,supp[ii[k]])));
 for(omit=2,m,
  my(outputs=select(k->k!=omit,vector(m-1,k,k+1)));
  forsubset([#outputs,n],kk,
   my(K=vector(n,k,outputs[kk[k]]));
   if(matdet(tr(b,J,K))!=0,best[omit-1]=max(best[omit-1],vecsum(K)-vecsum(J)))
  )
 )
);
if(best!=expected,error("GP exhaustive support disagreement"));
print("PASS GP exhaustive support n=",n," bounds=",best);
}
'''
n=data['n'];m=data['m'];code+=f'n={n};m={m};b=bb(m);\n'
code+=r'''
modulus=ffinit(3,8);z=ffgen(modulus,'z);
aa=[z,z^2+1,z^3+z,z^4+2*z^2,z^5+z+1,z^6+z^3+2];
if(#Set(aa)!=n-1||prod(i=1,n-1,aa[i])==0,error("invalid distinct old slopes"));
F=matrix(n,m+1,i,k,if(i==1,if(k==1,1,0),b[k]*aa[i-1]^(k-1)));
r=n*(n-1)/2+2;
E=matrix(r,m+1);E[1,1]=1;E[2,2]=1;
for(i=1,n-1,for(k=0,m,E[i+2,k+1]=F[i+1,k+1]));
idx=n+1;
for(i=1,n-1,for(j=i+1,n-1,idx++;for(k=0,m,E[idx,k+1]=sum(t=0,k,F[i+1,t+1]*F[j+1,k-t+1]))));
if(idx!=r,error("wrong E dimension"));
initial=matdet(sel(E,vector(r,k,k-1)));
if(initial==0,error("lower initial minor vanishes at control"));
print("lower initial minor=",initial);
print("field modulus=",modulus," old slopes=",aa);
'''
for c in data['cofactors']:
 omit=c['omit'];code+=f'omit={omit};bound={c["bound"]};total=0;terms=0;nonzero=0;\n'
 for q in c['maximizers']:
  code+=f'J={q["J"]};K={q["K"]};\n'
  code+=r'''
{
my(transfer=matdet(tr(b,J,K)),I=select(k->k!=omit,vector(m+1,k,k-1)),L,sign,ev,fv);
if(transfer==0,error("zero claimed transfer"));
L=select(k->!setsearch(Set(K),k),I);
sign=(-1)^sum(i=1,#K,sum(j=1,#L,K[i]<L[j]));
ev=matdet(sel(E,L));fv=matdet(sel(F,J));
terms++;if(ev*fv!=0,nonzero++);
total+=sign*ev*fv*transfer;
}
'''
 code+='print("omit=",omit," bound=",bound," terms=",terms," nonzero_terms=",nonzero," coefficient=",total);\n'
code+='print("PASS all target transfer determinants verified; actual coefficients are finite evaluations only");\nquit;\n'
r=subprocess.run(['gp','-q'],input=code,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
Path(a.out).write_text(r.stdout)
if r.returncode or any('***' in line and 'Warning:' not in line for line in r.stdout.splitlines()) or 'PASS all target' not in r.stdout: raise SystemExit('GP verification failed; inspect '+a.out)
print('PASS: GP exhaustive controls, every saved target transfer minor, actual cofactor coefficient evaluation')

"""Independent GP validation of actual overflow cofactor norm-line evidence."""
import argparse,json,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--data',required=True);p.add_argument('--out',required=True);p.add_argument('--full',action='store_true');a=p.parse_args();d=json.loads(Path(a.data).read_text())
code=r'''
default(parisizemax,1000000000);
x;z;t=varhigher("t");
need(c,s)={if(!c,error(s));};
normpoly(P,p,e)={if(P==0,return(0));my(v=1);for(j=0,e-1,v*=sum(k=0,poldegree(P,x),polcoef(P,k,x)^(p^j)*x^k));v;};
monic(P)={if(P==0,return(0));P/pollead(P);};
mkH(n,q,aa)={
 my(m=n*(n+1)/2+2,r=n*(n-1)/2+2,alpha=(q+1)/2,o=aa[2]^0,E=List([vector(q,j,if(j==1,o,0*o)),vector(q,j,if(j==2,o,0*o))]),F=matrix(n,q));
 for(i=1,n,
  my(w=sqrt(o+aa[i]*t+O(t^q)));for(k=0,q-1,F[i,k+1]=polcoef(w,k,t));
  for(j=i+1,n,my(wij=sqrt(o+(aa[i]+aa[j])*t+aa[i]*aa[j]*t^2+O(t^q)));listput(E,vector(q,k,polcoef(wij,k-1,t))));
 );
 need(#E==r,"complete old pair source");
 matrix(m,m+1,i,j,if(i<=r,if(j<=q,E[i][j],0*o),if(j<=q,if(j>alpha,F[i-r,j-alpha],0*o),F[i-r,j-q])));
};
minor(H,j)={my(m=matsize(H)[1],cols=select(k->k!=j,vector(m+1,k,k-1)));matdet(matrix(m,m,i,k,H[i,cols[k]+1]));};
'''
for k in ['n','q','p','e']:code+=f'{k}={d[k]};\n'
code+=f'field=Mod(1,p)*Polrev({d["modulus"]},z);aldata={d["intercept"]};bedata={d["direction"]};\n'
code+=r'''
a=ffgen(field,'a);o=a^0;al=concat([0*o],vector(n-1,i,sum(j=0,e-1,aldata[i][j+1]*a^j)));be=concat([0*o],vector(n-1,i,sum(j=0,e-1,bedata[i][j+1]*a^j)));aa=vector(n,i,al[i]+x*be[i]);
need(polisirreducible(field),"irreducible field");
V=prod(i=1,n,prod(j=i+1,n,aa[j]-aa[i]));
Hlead=mkH(n,q,be);H0=mkH(n,q,al);H1=mkH(n,q,vector(n,i,al[i]+be[i]));
G=0;checked=0;skipped=0;
'''
code+=f'NV=Mod(1,p)*Polrev({d["norm_vandermonde"]},x);GG=Mod(1,p)*Polrev({d["gcd"]},x);FRAME=Mod(1,p)*Polrev({d["frame"]},x);\n'
code+='need(o*NV==normpoly(V,p,e),"norm Vandermonde");need(FRAME==monic(NV^(n+1)),"frame");\n'
if a.full:code+='H=mkH(n,q,aa);rawg=0;\n'
for item in d['minors']:
 code+=f'j={item["omit"]};D=Mod(1,p)*Polrev({item["norm"]},x);G=gcd(G,D);\n'
 code+=r'''
{
my(lc=minor(Hlead,j)^((p^e-1)/(p-1)));
if(lc!=0,
 need(o*subst(D,x,0)==minor(H0,j)^((p^e-1)/(p-1))/lc,"point zero");
 need(o*subst(D,x,1)==minor(H1,j)^((p^e-1)/(p-1))/lc,"point one");checked++
,skipped++);
}
'''
 if a.full:code+='raw=minor(H,j);need(o*D==monic(normpoly(raw,p,e)),"full norm polynomial");rawg=gcd(rawg,raw);\n'
code+='need(monic(G)==GG,"full gcd");print("PASS exact norm gcd and frame; independently checked minors=",checked," skipped vanishing directions=",skipped);\n'
if a.full:code+='print("original field gcd degree=",poldegree(rawg,x)," expected frame degree=",(n+1)*n*(n-1)/2);print("PASS full original polynomial determinants and norms");\n'
code+='print("PASS verification complete");quit;\n'
r=subprocess.run(['gp','-q'],input=code,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);Path(a.out).write_text(r.stdout)
if r.returncode or any('***' in l and 'Warning:' not in l for l in r.stdout.splitlines()) or 'PASS verification complete' not in r.stdout:raise SystemExit('GP failed; inspect '+a.out)
print('PASS independent GP verification')

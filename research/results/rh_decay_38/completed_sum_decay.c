/* Tested statement (imported preprint of 5 October 2026, its completed mean square at one row, H = 1, f = 1,
 * trivial ray class character, S = primes above 2 and 3): the completed sum
 *   T(X) = X^{-1/2} sum_{n,b} conj(alpha(n)) gamma_2(n) conj(alpha(b))^3 N(b)^{1/2} W(N(n) N(b)^3 / X)
 * over primary n, b in Z[w] prime to 6, n squarefree, satisfies |T(X)|^2 << X^eps (1 + 1/X).
 * gamma_2(n) = N(n)^{-1/2} sum_{x mod n} (x/n)_3 e(x/n), e(z) = exp(4 pi i Im z / sqrt 3), alpha(n) = n/|n|.
 * gamma_2 is computed at primes from the definition and at composite squarefree n by
 *   gamma_2(v m) = gamma_2(v) gamma_2(m) conj((v/m)_3)   (checked numerically in the previous entry),
 * and dumped for N(n) <= DUMP for comparison with a direct PARI computation.
 * Controls: alpha in place of conj(alpha); no angular factor; and the sums with b = 1 only.
 * DECAY RUN.  Weight W(y) = exp(-(log y)^2 / 2), cut at |log y| = 3.5 (relative size 2e-3 at the cut).
 * The source's transformation formula (its proposition on the transformed sums, appendix read) gives at this
 * row T(X) = sum over finitely many groups of C sum_l d(l) alpha(l) N(l)^(-1/2) psi V#(N(l) X / N(c0)^2), with
 * |C| <= 1/81, l in lambda^(-4) O (least norm 1/81) and c0 a divisor of 6 for the period 18 of the fixed
 * factor, so N(l)/N(c0)^2 >= 1/104976.  V# for this weight is tabulated in dual_weight.out: of order 1 below
 * x = 0.1, then 4e-2 at x = 1, 1e-3 at 5, 2e-4 at 30, 5e-6 at 100.
 * EXPECTED, WRITTEN BEFORE THE RUN:
 *  - import twist: the dual sum has about 1e5/X effective terms, so |T| should fall as X grows, roughly like
 *    X^(-1/2) between X = 1e3 and 4.5e4 (a factor near 7, with fluctuation), and its imaginary part should be
 *    at rounding level (the sum is real by n -> conj n).  |T| staying at the random-walk scale across that
 *    range would contradict the transformation formula, or show a kernel error.
 *  - no twist: growth, as in the previous run (a polar term), by a factor near 45^(1/3) = 3.6 over that range.
 *  - conjugate twist: no prediction of mine; a reviewer expects the same fall as for the import twist.
 *  - random-walk scale: constant.
 * usage: completed_sum_decay M dumpfile outfile     (M = bound for N(n); X runs over powers of 2 up to M/e^3.5)
 */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <complex.h>
#include <omp.h>
typedef long long ll;
static ll pw(ll b, ll e, ll m){ ll r=1; b%=m; if(b<0)b+=m; while(e){ if(e&1) r=(__int128)r*b%m; b=(__int128)b*b%m; e>>=1;} return r; }
static const double PI=3.14159265358979323846;
static double complex W3[3];
/* split prime p = 1 mod 3: roots r of r^2+r+1 mod p; prime element with w = r mod pi */
static int M; static int *spf;
static double complex *g_split[2]; /* gamma_2 for (p, root index) */
static int *root0, *root1, *pa[2], *pb[2]; /* primary generator a + b w for each root */
/* F_{q^2} = F_q[w] arithmetic */
static void mul2(ll *s, ll *t, ll u, ll v, ll q){ ll a=((*s)*u - (*t)*v)%q, b=((*s)*v + (*t)*u - (*t)*v)%q; if(a<0)a+=q; if(b<0)b+=q; *s=a; *t=b; }
static int sym_inert(ll a, ll b, ll q){ /* (a+bw / q)_3 as exponent k of w, -1 if zero */
  a%=q; if(a<0)a+=q; b%=q; if(b<0)b+=q; if(a==0&&b==0) return -1;
  ll rs=1, rt=0, bs=a, bt=b, e=(q*q-1)/3;
  while(e){ if(e&1) mul2(&rs,&rt,bs,bt,q); ll cs=bs, ct=bt; mul2(&bs,&bt,cs,ct,q); e>>=1; }
  if(rs==1&&rt==0) return 0; if(rs==0&&rt==1) return 1; if(rs==q-1&&rt==q-1) return 2;
  fprintf(stderr,"bad inert symbol\n"); exit(1);
}
static int sym_split(ll a, ll b, ll p, ll r){ /* (a+bw / pi)_3, pi the prime above p with w = r */
  ll v=((a + b%p*r)%p+p)%p; if(v==0) return -1;
  ll c=pw(v,(p-1)/3,p); if(c==1) return 0; if(c==r) return 1; if(c==(r*r)%p) return 2;
  fprintf(stderr,"bad split symbol\n"); exit(1);
}
static double complex gamma_inert(ll q){ /* generator -q; e(x/(-q)) = exp(-2 pi i t/q) for x = s + t w */
  double complex s=0;
  for(ll u=0;u<q;u++) for(ll t=0;t<q;t++){ int k=sym_inert(u,t,q); if(k>=0) s+=W3[k]*cexp(-2*PI*I*(double)t/(double)q); }
  return s/(double)q;
}
static double complex gamma_split(ll p, ll r, ll b){ /* pi = a + b w, w = r mod pi; classes t in Z; e(t/pi) = exp(-2 pi i t b/p) */
  ll g=2; for(;;g++){ ll m=p-1, ok=1; for(ll f=2;f*f<=m;f++) if(m%f==0){ if(pw(g,(p-1)/f,p)==1){ok=0;break;} while(m%f==0)m/=f; } if(ok&&m>1&&pw(g,(p-1)/m,p)==1) ok=0; if(ok) break; }
  ll c=pw(g,(p-1)/3,p); int st=(c==r)?1:2;
  /* cubic character by index table; then sum over the phase index j = t b mod p, i.e. t = j b^{-1}, with the
     root of unity advanced by multiplication and reseeded exactly every 2048 steps */
  unsigned char *ix=malloc(p); ll t=1; for(ll k=0;k<p-1;k++){ ix[t]=(unsigned char)((k*st)%3); t=t*g%p; }
  ll bb=((b%p)+p)%p, binv=pw(bb,p-2,p); double complex s=0, z=1, zeta=cexp(-2*PI*I/(double)p); t=0;
  for(ll j=1;j<p;j++){ t+=binv; if(t>=p) t-=p; if((j&2047)==0) z=cexp(-2*PI*I*(double)j/(double)p); else z*=zeta; s+=W3[ix[t]]*z; }
  free(ix);
  return s/sqrt((double)p);
}
#define WCUT 3.5
static double Wf(double y){ double u=log(y); if(u<=-WCUT||u>=WCUT) return 0; return exp(-u*u/2); }
int main(int argc,char**argv){
  if(argc<4){ fprintf(stderr,"usage\n"); return 2; }
  M=atoi(argv[1]); W3[0]=1; W3[1]=cexp(2*PI*I/3); W3[2]=cexp(4*PI*I/3);
  spf=calloc(M+1,sizeof(int)); for(int i=2;i<=M;i++) if(!spf[i]) for(int j=i;j<=M;j+=i) if(!spf[j]) spf[j]=i;
  root0=calloc(M+1,sizeof(int)); root1=calloc(M+1,sizeof(int));
  for(int j=0;j<2;j++){ g_split[j]=calloc(M+1,sizeof(double complex)); pa[j]=calloc(M+1,sizeof(int)); pb[j]=calloc(M+1,sizeof(int)); }
  int R=(int)(2*sqrt((double)M))+3;
  /* primary elements of prime norm p: a = 1 mod 3, b = 0 mod 3 */
  for(int a=-R;a<=R;a++) if(((a%3)+3)%3==1) for(int b=-R;b<=R;b++) if(b%3==0){
    ll N=(ll)a*a-(ll)a*b+(ll)b*b; if(N<2||N>M||spf[N]!=N||N%3!=1) continue;
    ll p=N, r=((-(ll)a%p+p)%p)*pw(((b%p)+p)%p,p-2,p)%p; /* w = -a/b mod pi */
    int j; if(root0[p]==0){ root0[p]=(int)r; j=0; } else { root1[p]=(int)r; j=1; }
    pa[j][p]=a; pb[j][p]=b;
  }
  #pragma omp parallel for schedule(dynamic,16)
  for(int p=7;p<=M;p++) if(spf[p]==p&&p%3==1){ g_split[0][p]=gamma_split(p,root0[p],pb[0][p]); g_split[1][p]=gamma_split(p,root1[p],pb[1][p]); }
  /* check added for the report, expectation written before its run: at every split prime |gamma_2| = 1 and the
     two conjugate prime elements have conjugate gamma_2 (computed independently, with different index tables),
     both to 1e-10 or better; this exercises the reseeded branch of gamma_split, which the dump (norms up to 700)
     does not */
  double dev_mod=0, dev_conj=0; int nsplit=0;
  for(int p=7;p<=M;p++) if(spf[p]==p&&p%3==1){ nsplit++;
    double a=fabs(cabs(g_split[0][p])-1), b2=fabs(cabs(g_split[1][p])-1), c2=cabs(g_split[1][p]-conj(g_split[0][p]));
    if(a>dev_mod) dev_mod=a; if(b2>dev_mod) dev_mod=b2; if(c2>dev_conj) dev_conj=c2; }
  int Q=(int)sqrt((double)M)+1; double complex *g_in=calloc(Q+1,sizeof(double complex));
  for(int q=5;q<=Q;q++) if(spf[q]==q&&q%3==2&&(ll)q*q<=M) g_in[q]=gamma_inert(q);
  /* all primary n with N(n) <= M, prime to 2, squarefree: gamma_2(n) */
  int cap=(int)(0.45*M)+1000, cnt=0; int *na=malloc(cap*sizeof(int)), *nb=malloc(cap*sizeof(int)); double complex *ng=malloc(cap*sizeof(double complex));
  for(int a=-R;a<=R;a++) if(((a%3)+3)%3==1) for(int b=-R;b<=R;b++) if(b%3==0){
    ll N=(ll)a*a-(ll)a*b+(ll)b*b; if(N<1||N>M||N%2==0) continue;
    /* factor: list prime elements as (type, p, root, a, b) */
    int tp[40]; ll pp[40], rr[40]; int ea[40], eb[40]; int k=0, ok=1; ll m=N;
    while(m>1&&ok){ ll p=spf[m]; int v=0; while(m%p==0){m/=p;v++;}
      if(p%3==2){ if(v!=2){ok=0;break;} tp[k]=1; pp[k]=p; rr[k]=0; ea[k]=-(int)p; eb[k]=0; k++; }
      else { int both=(a%p==0&&b%p==0);
        if(both){ if(v!=2){ok=0;break;} for(int j=0;j<2;j++){ tp[k]=0; pp[k]=p; rr[k]=j?root1[p]:root0[p]; ea[k]=pa[j][p]; eb[k]=pb[j][p]; k++; } }
        else { if(v!=1){ok=0;break;} ll r0=root0[p]; int j=((( (ll)a + (ll)b%p*r0)%p+p)%p==0)?0:1; tp[k]=0; pp[k]=p; rr[k]=j?root1[p]:root0[p]; ea[k]=pa[j][p]; eb[k]=pb[j][p]; k++; } } }
    if(!ok) continue;
    double complex g=1; int e=0;
    for(int i=0;i<k;i++){ if(tp[i]) g*=g_in[pp[i]]; else g*=g_split[rr[i]==root0[pp[i]]?0:1][pp[i]]; }
    for(int i=0;i<k;i++) for(int j=i+1;j<k;j++){ int s= tp[j]? sym_inert(ea[i],eb[i],pp[j]) : sym_split(ea[i],eb[i],pp[j],rr[j]); if(s<0){fprintf(stderr,"zero symbol\n");return 1;} e+=3-s; }
    g*=W3[e%3];
    if(cnt>=cap){fprintf(stderr,"cap\n");return 1;} na[cnt]=a; nb[cnt]=b; ng[cnt]=g; cnt++;
  }
  FILE*fd=fopen(argv[2],"w"); for(int i=0;i<cnt;i++){ ll N=(ll)na[i]*na[i]-(ll)na[i]*nb[i]+(ll)nb[i]*nb[i]; if(N<=700) fprintf(fd,"%d %d %.15f %.15f\n",na[i],nb[i],creal(ng[i]),cimag(ng[i])); } fclose(fd);
  FILE*fo=fopen(argv[3],"w");
  fprintf(fo,"# checks: %d split primes; largest | |gamma_2| - 1 | = %.2e; largest |gamma_2(conj pi) - conj gamma_2(pi)| = %.2e\n",nsplit,dev_mod,dev_conj);
  fprintf(fo,"# M=%d squarefree primary n prime to 6: %d\n# X  terms  |T_import|  |T_alpha|  |T_plain|  |T_import_b1|  |T_plain_b1|  trivial  rms   (T = X^-1/2 * sum; trivial = sum of |terms|, rms = root of the sum of their squares, same normalization)\n",M,cnt);
  double YMAX=exp(WCUT);
  for(double X=64; YMAX*X<=M; X*=2){
    double complex s1=0,s2=0,s3=0,s4=0,s5=0; double tw=0,t2=0; ll terms=0; int RB=(int)(2*cbrt(YMAX*X))+4;
    for(int c=-RB;c<=RB;c++) if(((c%3)+3)%3==1) for(int d=-RB;d<=RB;d++) if(d%3==0){
      ll NB=(ll)c*c-(ll)c*d+(ll)d*d; if(NB<1||NB%2==0||(double)NB*NB*NB>YMAX*X) continue;
      double complex bz=c+d*W3[1], ab=bz/cabs(bz), ab3=ab*ab*ab; double sb=sqrt((double)NB), nb3=(double)NB*NB*NB;
      for(int i=0;i<cnt;i++){ double N=(double)na[i]*na[i]-(double)na[i]*nb[i]+(double)nb[i]*nb[i]; double w=Wf(N*nb3/X); if(w==0) continue;
        double complex nz=na[i]+nb[i]*W3[1], an=nz/cabs(nz); terms++; tw+=sb*w; t2+=sb*sb*w*w;
        s1+=conj(an)*ng[i]*conj(ab3)*sb*w; s2+=an*ng[i]*ab3*sb*w; s3+=ng[i]*sb*w;
        if(NB==1){ s4+=conj(an)*ng[i]*w; s5+=ng[i]*w; } } }
    double sx=sqrt(X);
    fprintf(fo,"%.0f %lld %.6e %.6e %.6e %.6e %.6e %.6e %.6e  re_im_import %.6e %.1e  re_im_alpha %.6e %.1e\n",X,terms,cabs(s1)/sx,cabs(s2)/sx,cabs(s3)/sx,cabs(s4)/sx,cabs(s5)/sx,tw/sx,sqrt(t2)/sx,creal(s1)/sx,cimag(s1)/sx,creal(s2)/sx,cimag(s2)/sx); fflush(fo);
  }
  fclose(fo); return 0;
}

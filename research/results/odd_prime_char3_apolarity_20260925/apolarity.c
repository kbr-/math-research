/* Char-3 apolarity test for the column model.
   Tested statement (char-0 Emsalem-Iarrobino, used in the column-model entry): for points m_1..m_r of V = F_3^d,
     HF(Sym(V)/(m_1^2,...,m_r^2))_s  ==  dim (I_Z)_s,  Z = fat points of multiplicity s-1 at the [m_j],
   with fat points defined by Hasse derivatives (the characteristic-free ideal m_P^{s-1}, the side notebook's notion).
   Also computed, as a control of the characteristic-free dual: dim (D(V)/sum_{a>=2} m_j^[a] D_{s-a})_s (divided powers),
   which must equal dim (I_Z)_s.
   Modes: d=3 all 8191 nonempty subsets of P^2(F_3), s=2..SMAX; d=4,5 random subsets (seeded).
   Output: one line per mismatch class plus totals, and a JSON summary to --out. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define MAXD 6
#define MAXM 800
static int d, s_deg, nmon[16]; static int mons[16][MAXM][MAXD];
static int binom3(int a, int b){ /* C(a,b) mod 3 by Lucas */
  int r=1; while(a||b){int x=a%3,y=b%3; if(y>x) return 0; int c=(x==2&&y==1)?2:1; r=(r*c)%3; a/=3;b/=3;} return r; }
static void gen(int deg){ int e[MAXD]={0}; nmon[deg]=0;
  /* enumerate compositions of deg into d parts */
  int stack(int i,int rem){ if(i==d-1){ e[i]=rem; memcpy(mons[deg][nmon[deg]++],e,sizeof(int)*MAXD); return 0;}
    for(int v=rem;v>=0;v--){e[i]=v; stack(i+1,rem-v);} return 0; }
  stack(0,deg); }
static int idx(int deg,const int*e){ for(int i=0;i<nmon[deg];i++){ if(!memcmp(mons[deg][i],e,sizeof(int)*d)) return i;} return -1; }
static int powm(int b,int e){ int r=1; for(int i=0;i<e;i++) r=(r*b)%3; return r; } /* 0^0=1 */
static unsigned char *M; static int rows, cols;
static int rank3(void){ int r=0; for(int c=0;c<cols&&r<rows;c++){ int p=-1; for(int i=r;i<rows;i++) if(M[i*cols+c]){p=i;break;}
    if(p<0) continue; if(p!=r) for(int j=0;j<cols;j++){unsigned char t=M[p*cols+j];M[p*cols+j]=M[r*cols+j];M[r*cols+j]=t;}
    int inv=M[r*cols+c]; /* 1->1, 2->2 */
    for(int j=0;j<cols;j++) M[r*cols+j]=(M[r*cols+j]*inv)%3;
    for(int i=0;i<rows;i++) if(i!=r&&M[i*cols+c]){ int f=M[i*cols+c]; for(int j=c;j<cols;j++) M[i*cols+j]=(M[i*cols+j]+3*3-f*M[r*cols+j])%3; }
    r++; } return r; }
/* Sym side: HF of Sym(V)/(m^2) in degree s */
static int hf_sym(int np,int P[][MAXD],int s){ int N=nmon[s]; if(s<2) return N; int K=nmon[s-2]; rows=np*K; cols=N;
  M=calloc((size_t)rows*cols,1); int r=0;
  for(int j=0;j<np;j++){ /* m^2 = sum over pairs */ for(int k=0;k<K;k++,r++){
      for(int a=0;a<d;a++) for(int b=0;b<d;b++){ int c=P[j][a]*P[j][b]%3; if(!c) continue; int e[MAXD]; memcpy(e,mons[s-2][k],sizeof e); e[a]++; e[b]++;
        int t=idx(s,e); M[r*cols+t]=(M[r*cols+t]+c)%3; } } }
  int rk=rank3(); free(M); return N-rk; }
/* fat side: dim of degree-s forms with all Hasse derivatives of order <= s-2 vanishing at each point */
static int dim_fat(int np,int P[][MAXD],int s){ int N=nmon[s]; int R=0; for(int i=0;i<=s-2;i++) R+=nmon[i]; rows=np*R; cols=N;
  if(rows==0) return N; M=calloc((size_t)rows*cols,1); int r=0;
  for(int j=0;j<np;j++) for(int i=0;i<=s-2;i++) for(int b=0;b<nmon[i];b++,r++) for(int t=0;t<N;t++){
      int c=1; for(int a=0;a<d&&c;a++){ int al=mons[s][t][a], be=mons[i][b][a]; if(be>al){c=0;break;} c=c*binom3(al,be)%3*powm(P[j][a],al-be)%3; }
      M[r*cols+t]=c; }
  int rk=rank3(); free(M); return N-rk; }
/* divided-power side: dim (D/ sum_{a>=2} m^[a] D_{s-a})_s ; m^[a] = sum_{|g|=a} m^g x^[g]; x^[g]x^[b] = prod C(g+b,g) x^[g+b] */
static int dim_dp(int np,int P[][MAXD],int s){ int N=nmon[s]; int R=0; for(int a=2;a<=s;a++) R+=nmon[s-a]; rows=np*R; cols=N;
  if(rows==0) return N; M=calloc((size_t)rows*cols,1); int r=0;
  for(int j=0;j<np;j++) for(int a=2;a<=s;a++) for(int b=0;b<nmon[s-a];b++,r++) for(int g=0;g<nmon[a];g++){
      int c=1,e[MAXD]; for(int q=0;q<d;q++){ c=c*powm(P[j][q],mons[a][g][q])%3*binom3(mons[a][g][q]+mons[s-a][b][q],mons[a][g][q])%3; e[q]=mons[a][g][q]+mons[s-a][b][q]; }
      if(c){ int t=idx(s,e); M[r*cols+t]=(M[r*cols+t]+c)%3; } }
  int rk=rank3(); free(M); return N-rk; }
static int pts[400][MAXD], npts;
static void projpts(void){ npts=0; int tot=1; for(int i=0;i<d;i++) tot*=3; for(int x=1;x<tot;x++){ int v[MAXD],y=x; for(int i=0;i<d;i++){v[i]=y%3;y/=3;}
    int lead=-1; for(int i=d-1;i>=0;i--) if(v[i]){lead=i;break;} if(v[lead]!=1) continue; memcpy(pts[npts++],v,sizeof v);} }
int main(int argc,char**argv){ d=atoi(argv[1]); int smax=atoi(argv[2]); int samples=atoi(argv[3]); unsigned seed=(unsigned)atoi(argv[4]); FILE*out=fopen(argv[5],"w");
  for(int s=0;s<=smax;s++) gen(s); projpts(); srand(seed);
  long tested=0, mism=0, dpfail=0, first=1; fprintf(out,"{\"d\":%d,\"smax\":%d,\"points\":%d,\"mismatches\":[",d,smax,npts);
  long total = (d==3)? ((1L<<npts)-1) : samples;
  for(long it=0; it<total; it++){ int P[400][MAXD], np=0;
    if(d==3){ long m=it+1; for(int i=0;i<npts;i++) if(m>>i&1) memcpy(P[np++],pts[i],sizeof(int)*MAXD); }
    else { int k=1+rand()%npts; int perm[400]; for(int i=0;i<npts;i++) perm[i]=i; for(int i=0;i<k;i++){int j=i+rand()%(npts-i); int t=perm[i];perm[i]=perm[j];perm[j]=t; memcpy(P[np++],pts[perm[i]],sizeof(int)*MAXD);} }
    for(int s=2;s<=smax;s++){ int a=hf_sym(np,P,s), b=dim_fat(np,P,s), c=dim_dp(np,P,s); tested++;
      if(b!=c) dpfail++;
      if(a!=b){ mism++; if(mism<=200){ fprintf(out,"%s{\"s\":%d,\"sym\":%d,\"fat\":%d,\"pts\":[",first?"":",",s,a,b); first=0;
          for(int j=0;j<np;j++){ fprintf(out,"%s[",j?",":""); for(int q=0;q<d;q++) fprintf(out,"%s%d",q?",":"",P[j][q]); fprintf(out,"]"); } fprintf(out,"]}"); } } }
    if(it%1000==0){ printf("it %ld tested %ld mismatches %ld dpfail %ld\n",it,tested,mism,dpfail); fflush(stdout);} }
  fprintf(out,"],\"tested\":%ld,\"mismatch_count\":%ld,\"divided_power_control_failures\":%ld}\n",tested,mism,dpfail); fclose(out);
  printf("DONE d=%d tested %ld mismatches %ld dpfail %ld\n",d,tested,mism,dpfail); return 0; }

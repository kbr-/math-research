/* Product tops tau_b = l_{b,1}^2 l_{b,2}^2 (b = 1..B, each top with its own two dense forms) on the weak monomial
   algebra A~ = tensor_c (F_3 + V_c), dim V_c = m, over F_3.  Forms: one seeded sequence of dense forms; the first 2B
   are used for B tops (nested series, one pass).  With 2B > mN the forms are linearly dependent.
   Tested statement: below the Koszul degree 8, ker(Phi_s: (+)_b A~_{s-4} -> A~_s, g -> sum g_b tau_b) equals the
   Frobenius span {(l_{b,1} x) e_b, (l_{b,2} x) e_b : x in A~_{s-5}} (tau_b is killed by l_{b,1} and l_{b,2} since
   l^3 = 0); from s = 8 the Koszul pairs (tau_c x) e_b - (tau_b x) e_c, x in A~_{s-8}, are added (reported as 'frobenius').  Reports dim ker, Frobenius rank, excess, and dim of the ideal in degree s.
   Usage: product_taylor m N seed s_list(comma) B_list(comma) out.json */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include "../odd_prime_alignment_mechanism_20260922/gf3.c"
static int m,N,NF; static unsigned char (*a)[16][8];
typedef struct { uint64_t *code; long n; } Basis;
static void enum_rec(int c,int left,uint64_t code,Basis*B){ if(c==N){ if(!left) B->code[B->n++]=code; return; } if(left>N-c) return;
  enum_rec(c+1,left,code,B); if(left) for(int r=0;r<m;r++) enum_rec(c+1,left-1,code|((uint64_t)(r+1)<<(3*c)),B); }
static long binom(int n,int k){ if(k<0||k>n) return 0; long r=1; for(int i=1;i<=k;i++) r=r*(n-k+i)/i; return r; }
static int cmpu(const void*x,const void*y){ uint64_t a=*(uint64_t*)x,b=*(uint64_t*)y; return a<b?-1:a>b; }
static Basis mk(int d){ Basis B; B.n=0; if(d<0){B.code=NULL;return B;} long cap=binom(N,d); for(int i=0;i<d;i++) cap*=m; B.code=malloc(sizeof(uint64_t)*(cap+1)); enum_rec(0,d,0,&B); qsort(B.code,B.n,sizeof(uint64_t),cmpu); return B; }
static long find(Basis*B,uint64_t c){ long lo=0,hi=B->n-1; while(lo<=hi){ long mid=(lo+hi)/2; if(B->code[mid]==c) return mid; if(B->code[mid]<c) lo=mid+1; else hi=mid-1;} return -1; }
/* polynomial in A~ as dense vector over basis of its degree; multiply vector (deg d) by form i -> deg d+1 */
static void mul_l(const unsigned char*v,Basis*S,int i,unsigned char*w,Basis*T){ for(long k=0;k<S->n;k++) if(v[k]){ uint64_t x=S->code[k];
  for(int c=0;c<N;c++) if(!((x>>(3*c))&7)) for(int r=0;r<m;r++) if(a[i][c][r]){ long j=find(T,x|((uint64_t)(r+1)<<(3*c))); w[j]=(w[j]+v[k]*a[i][c][r])%3; } } }
static long rank3(unsigned char*A,long r,long c){ /* pack into GF(3) bit planes and call the recorded bit-sliced kernel */
  int W=(int)((c+63)/64); size_t stride=2*(size_t)W; uint64_t*P=calloc((size_t)r*stride,8);
  #pragma omp parallel for schedule(static)
  for(long i=0;i<r;i++){ uint64_t*X=P+i*stride; for(long j=0;j<c;j++){ unsigned char v=A[i*c+j]; if(v==1) X[j>>6]|=1ULL<<(j&63); else if(v==2) X[W+(j>>6)]|=1ULL<<(j&63); } }
  int*piv=malloc(sizeof(int)*(c+1)); long rk=gf3_rref(P,(int)r,W,(int)c,0,piv); free(piv); free(P); return rk; }
/* image of monomial x (deg d) times l_i^2 l_j^2 into degree d+4 */
static void mul_tau(uint64_t x,int d,int i,int j,Basis*Bs,unsigned char*out){ /* Bs[d..d+4] */
  unsigned char *v0=calloc(Bs[d].n,1),*v1=calloc(Bs[d+1].n,1),*v2=calloc(Bs[d+2].n,1),*v3=calloc(Bs[d+3].n,1);
  v0[find(&Bs[d],x)]=1; mul_l(v0,&Bs[d],i,v1,&Bs[d+1]); mul_l(v1,&Bs[d+1],i,v2,&Bs[d+2]); mul_l(v2,&Bs[d+2],j,v3,&Bs[d+3]); mul_l(v3,&Bs[d+3],j,out,&Bs[d+4]);
  free(v0);free(v1);free(v2);free(v3); }
int main(int argc,char**argv){ m=atoi(argv[1]); N=atoi(argv[2]); unsigned long st=strtoul(argv[3],0,10); int sl[16],ns=0,bl[64],nb=0;
  for(char*t=strtok(argv[4],",");t;t=strtok(0,",")) sl[ns++]=atoi(t); for(char*t=strtok(argv[5],",");t;t=strtok(0,",")) bl[nb++]=atoi(t);
  int Bmax=0; for(int i=0;i<nb;i++) if(bl[i]>Bmax) Bmax=bl[i]; NF=2*Bmax; a=calloc(NF,sizeof *a);
  for(int i=0;i<NF;i++) for(int c=0;c<N;c++){ int nz=0; for(int r=0;r<m;r++){ st=st*6364136223846793005UL+1442695040888963407UL; a[i][c][r]=(st>>33)%3; nz|=a[i][c][r]; } if(!nz) a[i][c][0]=1; }
  int smax=0; for(int i=0;i<ns;i++) if(sl[i]>smax) smax=sl[i]; Basis Bs[20]; for(int d=0;d<=smax;d++) Bs[d]=mk(d);
  FILE*out=fopen(argv[6],"w"); fprintf(out,"["); int first=1;
  for(int si=0;si<ns;si++){ int s=sl[si]; Basis*S=&Bs[s-4],*T=&Bs[s];
    for(int bi=0;bi<nb;bi++){ int B=bl[bi]; long rows=(long)B*S->n;
      unsigned char*Phi=calloc((size_t)rows*T->n,1);
      #pragma omp parallel for schedule(dynamic)
      for(long r=0;r<rows;r++){ int b=r/S->n; long k=r%S->n; mul_tau(S->code[k],s-4,2*b,2*b+1,Bs,Phi+r*T->n); }
      long rk=rank3(Phi,rows,T->n); free(Phi); long ker=rows-rk;
      long frk=0; if(s>=5){ Basis*F=&Bs[s-5]; long fr=(long)2*B*F->n; unsigned char*Fm=calloc((size_t)fr*rows,1);
        #pragma omp parallel for schedule(dynamic)
        for(long r=0;r<fr;r++){ int b=r/(2*F->n); int which=(r/F->n)%2; long k=r%F->n; unsigned char*v0=calloc(F->n,1); v0[k]=1;
          mul_l(v0,F,2*b+which,Fm+r*rows+(long)b*S->n,S); free(v0); }
        long kr=0; Basis*K=(s>=8)?&Bs[s-8]:NULL; if(K) kr=(long)B*(B-1)/2*K->n;
        if(kr){ Fm=realloc(Fm,(size_t)(fr+kr)*rows); memset(Fm+(size_t)fr*rows,0,(size_t)kr*rows);
          long r=fr; for(int b=0;b<B;b++) for(int c=b+1;c<B;c++) for(long k=0;k<K->n;k++,r++){
            mul_tau(K->code[k],s-8,2*c,2*c+1,Bs,Fm+r*rows+(long)b*S->n);
            unsigned char*tmp=calloc(S->n,1); mul_tau(K->code[k],s-8,2*b,2*b+1,Bs,tmp); for(long j=0;j<S->n;j++) Fm[r*rows+(long)c*S->n+j]=(3-tmp[j])%3; free(tmp); } }
        frk=rank3(Fm,fr+kr,rows); free(Fm); }
      fprintf(out,"%s{\"m\":%d,\"N\":%d,\"s\":%d,\"B\":%d,\"forms\":%d,\"dimA1\":%d,\"ker\":%ld,\"frobenius\":%ld,\"excess\":%ld,\"ideal_dim\":%ld,\"dimAs\":%ld}\n",first?"":",",m,N,s,B,2*B,m*N,ker,frk,ker-frk,rk,T->n); first=0; fflush(out);
      printf("s=%d B=%d forms=%d ker=%ld frob=%ld excess=%ld ideal=%ld/%ld\n",s,B,2*B,ker,frk,ker-frk,rk,T->n); fflush(stdout); } }
  fprintf(out,"]\n"); fclose(out); return 0; }

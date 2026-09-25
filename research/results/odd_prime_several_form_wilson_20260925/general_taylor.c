/* Taylor generation for squares of M forms on the weak monomial algebra A~ = tensor_c (F_3 + V_c), dim V_c = m rows,
   with M > m allowed (beyond the column-independence / freeness regime).  Forms l_i = sum_{c,r} a[i][c][r] y_{r,c},
   coefficients uniform in F_3 from a seeded LCG (all columns used: dense forms).
   Tested statement: ker(Phi_s: (+)_i A~_{s-2} -> A~_s, (g_i) -> sum g_i l_i^2) equals the span of Frobenius
   (l_i m) e_i and Koszul (l_j^2 m) e_i - (l_i^2 m) e_j.  Also reports dim A~_s/(l_i^2)_s against the prediction
   [q^s] (1+m q)^N ((1+q)/(1+q+q^2))^M (free over the truncated algebra) and the Taylor prediction is the kernel test.
   Usage: general_taylor m M N_min N_max s_max seed out.json */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
static int m,M,N; static unsigned char a[16][16][8];
typedef struct { uint64_t *code; long n; } Basis; /* code: 3 bits per column, 0 empty or row+1 */
static void enum_rec(int c,int left,uint64_t code,Basis*B){ if(c==N){ if(!left) B->code[B->n++]=code; return; } if(left>N-c) return;
  enum_rec(c+1,left,code,B); if(left) for(int r=0;r<m;r++) enum_rec(c+1,left-1,code|((uint64_t)(r+1)<<(3*c)),B); }
static long binom(int n,int k){ if(k<0||k>n) return 0; long r=1; for(int i=1;i<=k;i++) r=r*(n-k+i)/i; return r; }
static int cmpu(const void*x,const void*y){ uint64_t a=*(uint64_t*)x,b=*(uint64_t*)y; return a<b?-1:a>b; }
static Basis mk(int d){ Basis B; B.n=0; if(d<0){B.code=NULL;return B;} long cap=binom(N,d); for(int i=0;i<d;i++) cap*=m; B.code=malloc(sizeof(uint64_t)*(cap+1)); enum_rec(0,d,0,&B); qsort(B.code,B.n,sizeof(uint64_t),cmpu); return B; }
static long find(Basis*B,uint64_t c){ long lo=0,hi=B->n-1; while(lo<=hi){ long mid=(lo+hi)/2; if(B->code[mid]==c) return mid; if(B->code[mid]<c) lo=mid+1; else hi=mid-1;} return -1; }
static void add_l(uint64_t x,int i,int coef,Basis*T,unsigned char*row){ for(int c=0;c<N;c++) if(!((x>>(3*c))&7)) for(int r=0;r<m;r++) if(a[i][c][r]){ long j=find(T,x|((uint64_t)(r+1)<<(3*c))); row[j]=(row[j]+coef*a[i][c][r])%3; } }
static void add_l2(uint64_t x,int i,int coef,Basis*T,unsigned char*row){ for(int c=0;c<N;c++) if(!((x>>(3*c))&7)) for(int d=c+1;d<N;d++) if(!((x>>(3*d))&7))
  for(int r=0;r<m;r++) if(a[i][c][r]) for(int q=0;q<m;q++) if(a[i][d][q]){ long j=find(T,x|((uint64_t)(r+1)<<(3*c))|((uint64_t)(q+1)<<(3*d))); row[j]=(row[j]+2*coef*a[i][c][r]*a[i][d][q])%3; } }
static long rank3(unsigned char*A,long r,long c){ long rk=0; for(long col=0;col<c&&rk<r;col++){ long p=-1; for(long i=rk;i<r;i++) if(A[i*c+col]){p=i;break;} if(p<0) continue;
    if(p!=rk) for(long j=0;j<c;j++){unsigned char t=A[p*c+j];A[p*c+j]=A[rk*c+j];A[rk*c+j]=t;}
    unsigned char inv=A[rk*c+col]; for(long j=col;j<c;j++) A[rk*c+j]=(A[rk*c+j]*inv)%3;
    #pragma omp parallel for schedule(static)
    for(long i=0;i<r;i++) if(i!=rk&&A[i*c+col]){ unsigned char f=A[i*c+col]; for(long j=col;j<c;j++) A[i*c+j]=(A[i*c+j]+9-f*A[rk*c+j])%3; }
    rk++; } return rk; }
int main(int argc,char**argv){ m=atoi(argv[1]); M=atoi(argv[2]); int Nmin=atoi(argv[3]),Nmax=atoi(argv[4]),smax=atoi(argv[5]); unsigned long seed=strtoul(argv[6],0,10); FILE*out=fopen(argv[7],"w"); fprintf(out,"["); int first=1;
  for(N=Nmin;N<=Nmax;N++){
    unsigned long st=seed*1000003UL+N; for(int i=0;i<M;i++) for(int c=0;c<N;c++){ int nz=0; for(int r=0;r<m;r++){ st=st*6364136223846793005UL+1442695040888963407UL; a[i][c][r]=(st>>33)%3; nz|=a[i][c][r]; } if(!nz) a[i][c][0]=1; }
    for(int s=2;s<=smax&&s<=N;s++){
      Basis S2=mk(s-2),T=mk(s); long dimS=(long)M*S2.n;
      unsigned char*Phi=calloc((size_t)dimS*T.n,1);
      for(int i=0;i<M;i++) for(long r=0;r<S2.n;r++) add_l2(S2.code[r],i,1,&T,Phi+((long)i*S2.n+r)*T.n);
      long rk=rank3(Phi,dimS,T.n); free(Phi); long ker=dimS-rk;
      Basis S3=mk(s-3),S4=mk(s-4); long nT=(long)M*S3.n+(long)M*(M-1)/2*S4.n; long trk=0;
      if(nT>0){ unsigned char*Tay=calloc((size_t)nT*dimS,1); long row=0;
        for(int i=0;i<M;i++) for(long r=0;r<S3.n;r++,row++) add_l(S3.code[r],i,1,&S2,Tay+row*dimS+(long)i*S2.n);
        for(int i=0;i<M;i++) for(int j=i+1;j<M;j++) for(long r=0;r<S4.n;r++,row++){ add_l2(S4.code[r],j,1,&S2,Tay+row*dimS+(long)i*S2.n); add_l2(S4.code[r],i,2,&S2,Tay+row*dimS+(long)j*S2.n); }
        trk=rank3(Tay,nT,dimS); free(Tay); }
      /* free prediction [q^s] (1+mq)^N ((1+q)/(1+q+q^2))^M, and actual HF of quotient = dim T - rk */
      long pred=0; { long c1[64]={0}; c1[0]=1; for(int k=0;k<N;k++) for(int d=63;d>0;d--) c1[d]+=m*c1[d-1];
        long inv[64]={0}; for(int d=0;d<64;d++) inv[d]=(d%3==0)?1:((d%3==1)?-1:0); /* 1/(1+q+q^2)=(1-q)/(1-q^3) */
        long w[64]={0}; w[0]=1; for(int t=0;t<M;t++){ long nw[64]={0}; for(int d=0;d<64;d++) for(int e=0;e<=d;e++) nw[d]+=w[e]*inv[d-e]; for(int d=63;d>0;d--) nw[d]+=nw[d-1]; memcpy(w,nw,sizeof w);} 
        for(int e=0;e<=s;e++) pred+=c1[e]*w[s-e]; }
      fprintf(out,"%s{\"m\":%d,\"M\":%d,\"N\":%d,\"s\":%d,\"seed\":%lu,\"ker\":%ld,\"taylor\":%ld,\"excess\":%ld,\"quotient_hf\":%ld,\"free_pred\":%ld}\n",first?"":",",m,M,N,s,seed,ker,trk,ker-trk,T.n-rk,pred); first=0; fflush(out);
      printf("m=%d M=%d N=%d s=%d ker=%ld taylor=%ld excess=%ld hf=%ld freepred=%ld\n",m,M,N,s,ker,trk,ker-trk,T.n-rk,pred); fflush(stdout);
      free(S2.code); free(T.code); free(S3.code); free(S4.code); } }
  fprintf(out,"]\n"); fclose(out); return 0; }

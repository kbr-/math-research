\\ Exact character Fourier arithmetic for bounded root cochains.
jc_cut(f,N)={truncate(f+O(T^N));};
jc_walsh(v)={
 for(bit=0,8,for(S=0,511,if(!bittest(S,bit),my(u=v[S+1],w=v[S+2^bit+1]);v[S+1]=u+w;v[S+2^bit+1]=u-w)));v;
};
jc_cube(v,roots,inverse,N)={
 my(ev=jc_walsh(vector(512,i,jc_cut(v[i]*roots[i],N))));
 ev=jc_walsh(vector(512,i,jc_cut((ev[i]+O(T^N))^3,N)));
 vector(512,i,jc_cut(ev[i]*inverse[i],N)/512);
};
jc_product3(v,w,u,roots,inverse,N)={
 my(ev=jc_walsh(vector(512,i,jc_cut(v[i]*roots[i],N))),ew=jc_walsh(vector(512,i,jc_cut(w[i]*roots[i],N))),eu=jc_walsh(vector(512,i,jc_cut(u[i]*roots[i],N))));
 ev=jc_walsh(vector(512,i,jc_cut(ev[i]*ew[i]*eu[i],N)));
 vector(512,i,jc_cut(ev[i]*inverse[i],N)/512);
};
jc_fourier(v,roots,N)={jc_walsh(vector(512,i,jc_cut(v[i]*roots[i],N)));};
jc_inverse(v,inverse,N)={my(w=jc_walsh(v));vector(512,i,jc_cut(w[i]*inverse[i],N)/512);};

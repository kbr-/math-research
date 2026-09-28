p=[1]+[0]*60
for w in (2,3,4,5,6):
 for d in range(w,61):p[d]+=p[d-w]
for ell in (41,42):
 t=18+ell
 src=sum(p[t-w] for w in range(11,19))
 tgt=sum(p[t-w] for w in (4,5,6,6,7,8))
 print(dict(excess=ell,total_weight=t,source_columns=src,target_rows=tgt,dense_entries=src*tgt))

# First nonpositive coefficient of (1+t)^s / (1+t^2)^h (semi-regular Boolean prediction)
import math,sys
def dreg(s,h,dmax=None):
    dmax=dmax or s
    # coefficients of (1+t^2)^{-h} = sum_j (-1)^j C(h+j-1,j) t^{2j}
    for d in range(0,dmax+1):
        c=0
        for j in range(0,d//2+1):
            c+=(-1)**j*math.comb(h+j-1,j)*math.comb(s,d-2*j)
        if c<=0: return d
    return None
for s in [50,100,200,400]:
    row=[]
    for h in [s//4, s//2, s, 2*s, int(s*math.log(s))]:
        d=dreg(s,h); row.append((h,d, round(s/math.sqrt(h),1)))
    print(s,row)

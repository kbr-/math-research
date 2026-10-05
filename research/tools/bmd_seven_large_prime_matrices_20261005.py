#!/usr/bin/env python3
"""Build six exact large-prime residue matrices from the retained rational pivot audit.

Singular computes determinants/factorizations; Python only assembles bounded
matrix recipes and retains complete inputs/outputs. No sampled-degree inference.
"""
import argparse, fractions, json, math, pathlib, re, subprocess, time
parser=argparse.ArgumentParser()
parser.add_argument("--profiles",type=pathlib.Path,required=True)
parser.add_argument("--out",type=pathlib.Path,required=True)
parser.add_argument("--shift",action="store_true",help="Retain exponent K=N-n0, divisible by p")
args=parser.parse_args()
profiles={}
for line in args.profiles.read_text().splitlines():
    m=re.match(r"c=(\S+) block=([ABC]) offsets=(\[.*?\]) determinant=(-?\d+) prime_divisors=(\[.*?\])",line)
    if m:
        residue,kind,offsets,det,primes=m.groups()
        assert set(json.loads(primes)) <= {2,3,5,7}
        profiles.setdefault(residue,{})[kind]=json.loads(offsets)
assert len(profiles)==6 and all(set(x)==set("ABC") for x in profiles.values())
args.out.mkdir(parents=True,exist_ok=True)
base=23
N=8*base+8
def block(kind,offsets):
    q=2*base+{"A":1,"B":3,"C":7}[kind]
    pivots={q-x for x in offsets}
    prefix=min(pivots)-1
    outliers=[e for e in range(prefix+1,q+1) if e not in pivots]
    return prefix+{"A":3,"B":2,"C":0}[kind],outliers
def source(residue, mode):
    r=fractions.Fraction(residue)
    n0=int(8*r+8)
    la,ea=block("A",profiles[residue]["A"])
    lb,eb=block("B",profiles[residue]["B"])
    lc,ec=block("C",profiles[residue]["C"])
    if mode=="alternative":
        groups=[(2,2,lc,2,2,ec,1),(1,0,la,3,4,ea,1),
                (0,1,la,2,5,ea,-1),(1,3,lc,1,3,ec,-1)]
    else:
        groups=[(2,0,lb,2,4,eb,1),(1,0,la,3,4,ea,1),
                (0,3,la,2,7,ea,-1),(1,3,lb,1,7,eb,-1)]
    peaks=[a+b+2*l for a,b,l,_,_,_,_ in groups]
    peaks += [a+b+2*e for _,_,_,a,b,ee,_ in groups for e in ee]
    M=max(peaks)
    dim=2*M-N+1
    m0=int(4*r+M-4*base)
    text=[f"// c mod p = {residue}, {mode}, p>19; N mod p={n0}.",
          "ring rr=(0,u),(t,C,X,Y,U,V),dp;",
          "proc bc(int n,int k){number ans=1;int ii;for(ii=1;ii<=k;ii++){ans=ans*(n-ii+1)/ii;}return(ans);}",
          f"matrix D[{dim}][{dim}];matrix R[1][{dim}];",
          "number ss=u^2+1/u^2;",
          "int j,k,h;poly W,cf;"]
    for j in range(dim):
        phase=(j-M)%4
        terms=["X","Y","-X","-Y"]
        if mode=="alternative":
            R,S=("U","V") if (j-M)%2==0 else ("V","U")
            text.extend([f"D[1,{j+1}]={R};",
                f"D[2,{j+1}]=(({j-m0})*(1-u^2)+({n0}))*{R}+({n0})*u*{S};"])
        else:
            text.extend([f"D[1,{j+1}]=({j-m0})*(1-u)+({n0});",
                f"D[2,{j+1}]=({(-1)**j})*(({j-m0})*(1+u)+({n0}));"])
        text.append(f"D[3,{j+1}]={terms[phase]};")
    row=3; depth=0
    for group,(ab,bb,l,a,b,ee,sign) in enumerate(groups):
        lo=ab+bb+2*l
        hi=M-((M-ab-bb)%2)
        nw=(hi-lo)//2
        if not nw:
            assert not ee
            continue
        text.append(f"matrix F{group}[{nw}][{dim}];")
        for h in range(nw):
            rdepth=M-hi+2*h
            depth=max(depth,rdepth)
            for j in range(dim):
                kh=rdepth-(dim-1)+j
                kl=rdepth-j
                val=[]
                if kh>=0: val.append(f"bc({n0},{kh})*(-u)^({kh})")
                if kl>=0: val.append(f"({sign})*C*bc({n0},{kl})*(-u)^(-{kl})")
                if val: text.append(f"F{group}[{h+1},{j+1}]="+"+".join(val)+";")
        pivots=[]
        for e in sorted(ee,reverse=True):
            pk=(hi-a-b-2*e)//2+1
            assert 1<=pk<=nw
            pivots.append(pk)
            e0=int(2*r+e-2*base)
            text.append(f"W=0;for(k=0;k<={nw};k++){{W=W+bc({e0},k)*(-ss*t+t^2)^k;}}")
            text.append(f"W=(1+t)^{a}*(1-t)^{b}*W;")
            text.append(f"for(j=1;j<={dim};j++){{R[1,j]=F{group}[{pk},j];}}")
            text.append(f"for(h={pk};h<={nw};h++){{cf=subst(W/t^(h-{pk}),t,0);for(j=1;j<={dim};j++){{F{group}[h,j]=F{group}[h,j]-cf*R[1,j];}}}}")
        for h in range(1,nw+1):
            if h not in pivots:
                row+=1
                text.append(f"for(j=1;j<={dim};j++){{D[{row},j]=F{group}[{h},j];}}")
    assert row==dim and depth<=32,(residue,mode,row,dim,depth)
    text += [f'print("dimension={dim}; maximum high depth={depth}");',
             "poly detD=det(D);"]
    if args.shift:
        n=abs(n0)
        A="+".join(f"({(-1)**(k//2)*math.comb(n,k)})*u^{k}" for k in range(0,n+1,2))
        B="+".join(f"({(-1)**((k-1)//2)*math.comb(n,k)*(1 if n0>0 else -1)})*u^{k}" for k in range(1,n+1,2))
        G="+".join(f"({math.comb(n,k)})*u^{k}" for k in range(0,n+1,2))
        H="+".join(f"({math.comb(n,k)*(-1 if n0>0 else 1)})*u^{k}" for k in range(1,n+1,2))
        dx="1" if n0>=0 else f"(u^2+1)^{n}"
        du="1" if n0>=0 else f"(u^2-1)^{n}"
        text += [f"poly AA={A};poly BB={B};poly GG={G};poly HH={H};",
            f"map shift=rr,t,u^({n0})*C,(AA*X+BB*Y)/({dx}),(AA*Y-BB*X)/({dx}),(GG*U+HH*V)/({du}),(HH*U+GG*V)/({du});",
            "detD=shift(detD);"]
    text += [
             'if(detD==0){print("ZERO formal determinant");}else{list fac=factorize(detD);print(fac);map atPowerOrigin=rr,t,0,2,0,2,0;int fi;poly oneFactor;for(fi=1;fi<=size(fac[1]);fi++){oneFactor=fac[1][fi];print("FACTOR "+string(fi)+": "+string(fac[1][fi]));print("ORIGIN "+string(fi)+": "+string(atPowerOrigin(oneFactor)));}poly product=1;int ff;for(ff=1;ff<=size(fac[1]);ff++){product=product*fac[1][ff]^fac[2][ff];}if(product!=detD){ERROR("factor product mismatch");}}',
             'print("PASS: determinant factorization");quit;']
    return "\n".join(text)+"\n",{"residue":residue,"mode":mode,"dimension":dim,"depth":depth}

# First analyze the alternative source for all six residue templates.
for residue in profiles:
    code,meta=source(residue,"alternative")
    label=residue.replace("-","minus").replace("/","over")
    script=args.out/f"{label}.sing"
    output=args.out/f"{label}.txt"
    script.write_text(code)
    print("START",json.dumps(meta),flush=True)
    start=time.monotonic()
    run=subprocess.run(["Singular","-q",str(script)],capture_output=True,text=True,timeout=150)
    out=run.stdout+run.stderr
    output.write_text(out)
    meta["elapsed_seconds"]=round(time.monotonic()-start,3)
    meta["exit_code"]=run.returncode
    meta["zero"]="ZERO formal determinant" in out
    meta["passed"]=run.returncode==0 and "PASS: determinant factorization" in out and not re.search(r"^\s*\?|FAIL|error",out,re.M|re.I)
    print("END",json.dumps(meta),flush=True)
    assert meta["passed"],f"Read failed output {output}"
print("DONE: six exact symbolic templates; actual-power nonvanishing still requires proof.")

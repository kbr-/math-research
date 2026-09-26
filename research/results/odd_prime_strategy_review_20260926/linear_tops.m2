-- Semi-regularity test for random linear tops on the graded ring G of functional PHP (26 September 2026).
-- G = F_3[x_(u,v)] / (x^2, x_(u,v)x_(u,v') functionality, x_(u,v)x_(u',v) collisions, row sums),
-- m = n+1 pigeons, n holes. For a = 0..amax random linear forms l_1..l_a over F_3, compare the Hilbert
-- function of G/(l_1..l_a) with the semi-regular prediction [(1-t)^a H_G(t)]_+ (truncated at the first
-- nonpositive coefficient). Prints one line per (n, a): observed and predicted coefficients.
setRandomSeed 20260926;
for n from 3 to 4 do (
    m := n + 1;
    R := ZZ/3[x_(0,0)..x_(m-1,n-1)];
    gens1 := flatten for u from 0 to m-1 list for v from 0 to n-1 list x_(u,v)^2;
    func := flatten flatten for u from 0 to m-1 list for v from 0 to n-1 list for w from v+1 to n-1 list x_(u,v)*x_(u,w);
    coll := flatten flatten for v from 0 to n-1 list for u from 0 to m-1 list for w from u+1 to m-1 list x_(u,v)*x_(w,v);
    rows := for u from 0 to m-1 list sum for v from 0 to n-1 list x_(u,v);
    I := ideal(gens1 | func | coll | rows);
    top := n + 2;
    HG := for d from 0 to top list hilbertFunction(d, R/I);
    for a from 0 to 2*n do (
        L := if a == 0 then ideal(0_R) else ideal for j from 1 to a list random(1, R);
        obs := for d from 0 to top list hilbertFunction(d, R/(I + L));
        -- prediction: coefficients of (1-t)^a * HG, truncated at first nonpositive
        pr := for d from 0 to top list sum for i from 0 to min(d, a) list (-1)^i * binomial(a, i) * HG#(d-i);
        tr := {}; stop := false;
        for d from 0 to top do (if stop or pr#d <= 0 then (stop = true; tr = append(tr, 0)) else tr = append(tr, pr#d));
        print("n=" | toString n | " a=" | toString a | " observed=" | toString obs | " predicted=" | toString tr);
    );
);
exit 0;

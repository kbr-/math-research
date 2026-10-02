-- Base of a five-pointed bottom level (8 October 2026; cycle bmd-20261008-w): four distinct roots 0, c1, c2, 1 and the
-- node up.  The pair matrix A_(R+1), R = 6, has rows H_k(x, y) = [T^k] (1+xT)^(-3/2) (1+yT)^(-3/2) for the six pairs and
-- columns k = 0..7.  Prints whether its ideal of 6 x 6 minors, saturated by c1 c2 (c1-1)(c2-1)(c1-c2), is the unit
-- ideal, over QQ and, as a cross-check, over ZZ/32003.
for K in {QQ, ZZ/32003} do (
R = K[c1, c2];
bin = (k) -> (p := 1_R; for i from 0 to k - 1 do p = p * (-3/2 - i) / (i + 1); p);
pair = (a, b, k) -> sum(0..k, i -> bin(i) * bin(k - i) * a^i * b^(k - i));
pts := {0_R, c1, c2, 1_R};
prs := flatten apply(4, i -> apply(toList(i + 1..3), j -> (pts#i, pts#j)));
W := matrix apply(prs, ab -> apply(8, k -> pair(ab#0, ab#1, k)));
I := minors(6, W);
F := c1 * c2 * (c1 - 1) * (c2 - 1) * (c1 - c2);
S := saturate(I, F);
print("field " | toString K | ": pair matrix of (0, c1, c2, 1) is " | toString numrows W | " x " | toString numcols W
    | "; saturated 6 x 6 minor ideal is the unit ideal: " | toString(S == ideal 1_R)
    | "; also on columns 0..6: " | toString(saturate(minors(6, W_{0..6}), F) == ideal 1_R));
);
exit 0

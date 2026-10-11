
## A necessary fixed-field check for the determinantal-ideal lead

Proposed corollary: binary oracle closure gap. Circuits use unbounded-fanin
sum/product gates and constants in F2, plus scalar oracle gates for a polynomial
f which vanishes on every Boolean input. On Boolean inputs, replacing every
oracle gate by zero gives an ordinary binary arithmetic circuit with the same
outputs and no greater size/depth. Proof is induction in circuit order:
all gate arguments lie in F2, so each oracle call returns zero.

Consequently a direct F2 version of universal constant-depth polynomial-size
determinantal-ideal oracle extraction is false, even if allowed to output a
Frobenius power of determinant. For an r by r symbolic X take
f_r=det_r(X)*(x_11^2+x_11). This is a nonzero polynomial in the ideal of
r-minors, degree r+2, and is zero at every binary point. If fixed-depth
poly(r)-size f_r-oracle circuits over F2 computed det_t, or det_t^(2^e_r),
for t=floor(r^(1/3)) and arbitrary e_r>=0, replacing oracles by zero would
compute the Boolean determinant function at polynomial size in t and constant
depth. For every Boolean value z, z^(2^e)=z. The recorded binary determinant
depth gap (explicit MOD3 reduction and Smolensky) rules this out. Use r=t^3
to avoid sparse target sizes.

This does NOT refute Andrews-Forbes or the 2026 Dey-Guo debordering result:
their stated fields are characteristic zero/large characteristic, with a
large-field premise in the new exact theorem. Extension-field oracle
arguments can make f_r nonzero. The false extension isolated here is a circuit
over F2 itself. It does not refute every small-characteristic large-field
version. The source paper's open small-characteristic root problem is separate.

Nonvacuity: f_r is nonzero since its displayed factors are nonzero in a domain;
it belongs to the principal r-minor ideal and has unbounded degree/variable
count. The function-zero condition is checked by the explicit Boolean factor.
Non-Boolean oracle inputs, extension constants, rational gates undefined at
Boolean points, or depth growing with r fall outside this corollary.

This is an attributed consequence of the recorded determinant-function
lower bound, not a new general arithmetic circuit lower bound. It makes the
finite-field premise test of the Outside lead concrete and source-sensitive.


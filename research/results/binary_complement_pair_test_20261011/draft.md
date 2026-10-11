# Complementary blocks share a residual source

Reviewed draft after the symbolic rule check. Goal progress is unchanged until
source-wide coverage and its iteration budget are established.

Work over F2. Let Gamma contain Booleanity for all retained variables y. Let
H(y), t_1(y),...,t_m(y) be binary polynomials. Two fresh complete accuracy-h
blocks, h>=2, have respective input tuples (H,t) and (1+H,t). Their private
coefficient arrays are a,b and their products are P_+,P_-. Let any additional
axioms A(y,a,b,z) be retained under substitution; their variables z are fixed.
They may include later readers, but are not silently assumed to retain the
original affine-in-whole-products grammar after substitution.

Create one complete accuracy-(h-1) block on t, with fresh coefficients u and
product P_t. Set the first source row's H-position coefficient to one and
its residual-position coefficients to zero, in both blocks. In source rows
2,...,h set H-position coefficients to zero and identify the residual-position
coefficients of both blocks with the same corresponding u row. Fix old variables
and z. Call this degree-one substitution Phi. It gives literal identities

    Phi(P_+)=(1+H)P_t,    Phi(P_-)=H P_t.

Claim: every ordinary degree-B NS or PC consequence of Gamma plus these two
complete blocks plus A transfers, after applying Phi to the target, to a
degree-B consequence of Gamma plus the one complete residual block plus Phi(A).
All fields are retained; proof cofactors may freely use the source coefficients.
No weight or survival premise is required for this algebraic transformation.

Proof. A residual input companion maps to (1+H)t_i P_t or H t_i P_t, an
explicit multiple of a target companion. The two distinguished companions
map to the same H(1+H)P_t, a Boolean consequence. Every source coefficient
field maps to zero or to a target coefficient field.

For the original-degree check, first assume t contains a nonzero polynomial.
Put d=max_i deg t_i>=0, e=deg H when H is nonconstant, and delta=max(d,e).
For constant H use e=0 and delta=d. Then every nonzero source tuple has maximum
input degree delta, and its original product degree is h(delta+1). The target
product has degree at most v=(h-1)(d+1). Each residual certificate costs at most
v+deg t_i+e <= h(delta+1)+deg t_i. A nonconstant H has H^2+H Boolean-certified
through 2e, so its product with P_t costs at most v+2e <= h(delta+1)+e.
For completeness, reduce each monomial of H^2+H by y_j^2+y_j. Every
reduction replaces a power by a smaller power, so neither the intermediate
polynomials nor the Boolean-axiom summands exceed degree 2e. The remainder
is multilinear and evaluates to zero at every Boolean assignment, hence is
zero (successively interpolate in each variable). This supplies the claimed
degree-bounded ideal certificate without an appeal to pointwise vanishing alone.
For constant H that distinguished image is zero. These ceilings are no larger
than the corresponding actual source companion degree. Zero residual inputs
have zero companions; their fields may still be mapped as stated or zeroed.

If t is empty or identically zero, take P_t=1 and omit the residual block.
All companion images are zero or H(1+H), certified through 2e within the
original degree of each nonzero distinguished companion. Set unused residual
coefficient images to zero in this case. A wholly zero source tuple has no
nonzero companions, and its fields map to constants, so it causes no exception.

Phi is constant/renaming on variables, so it does not increase proof-line or
cofactor degrees. Insert the displayed axiom-image certificates at their own
original ceilings, and replay each PC inference, or each NS summand, through
B. The transformed additional axioms Phi(A) are target axioms, and their degrees
do not increase. This proves the claim. Original padded rows retain their cost.

Reader condition. If every later input uses P_+,P_- only via their sum, it
continues to be affine in earlier whole products, since Phi(P_++P_-)=P_t.
More explicitly L+alpha P_++beta P_- maps to

    L + (alpha+(alpha+beta)H) P_t.

Equal constant coefficients alpha=beta suffice for grammar preservation,
inductively through later blocks; their own coefficient variables are fixed.
Without that condition the algebraic proof transfer still holds, but the new
H P_t term need not be affine in whole-product names. For example H=x,
t=(z), h=2 gives P_t=1+u z. The coefficient of u in x P_t is xz and cannot
equal a constant multiple of z, so x P_t is not old-affine plus a scalar multiple
of P_t in the literal polynomial ring. This is only a scope control, not proof
that no further reader normalization exists.

Boundary h=1. The same first-row substitution transfers to Gamma plus the
input axioms t_i, because the residual product is one and there are no residual
coefficient variables. It is not free elimination to Gamma. h=0 is excluded.

Nonvacuity. For arbitrary old-variable counts take Gamma=BOOL, H=x, t=(z),
h=2. Both source tuples are nonunit, the target has accuracy one, and all source
companion degrees are five. The target companion degree is three; its H multiple
and the Boolean distinguished certificate fit degree four. A later reader of
P_++P_- maps to P_t. Unused old variables give unbounded counts. This tests the
source transformation, not a hard-family result.

Degenerate cases. Empty and zero residual tuples, constants H=0,1, repeated
residual positions, inactive high-degree axioms at a small proof ceiling and the
h=1 boundary are accounted for above. Repeated positions retain their actual
arity/encoding cost. No source-domain field is omitted.

Prior comparison. The historical core-residual batch theorem already eliminates
terminal families with common span(t) and one extra direction per block at cost
B+gamma, gamma the maximum degree of a core generator, independently of block
count. Thus the proposed terminal exclusion is not a new degree gain. The
point to test here is the explicit degree-preserving retained-source map and its
effect on later readers. lem:covered-disjunction-normalizer has a unit witness
inside one tuple containing complementary inputs; it does not merge these two
tuples with retained residual rows. The costed input-basis lemma uses supplied
residual certificates for discarded inputs. Here the distinguished inputs are
killed by a consumed source row, and residual coefficient rows are identified.

Completed symbolic check: Singular independently expanded both source
products and applied the actual coefficient substitution for accuracies 1..4,
residual arities 0..3, five H choices (0,1,x,xy,x+y+xy), and five residual
patterns (independent variables, products, constants/zeros, duplicates, all zero;
only one pattern for arity zero): 320 fixtures. It verified complete companions,
all fields, original actual degrees, balanced/unbalanced reader formulas and
negative controls dropping the first-row selection, residual identification,
or the accuracy decrement. Largest raw product has at most 7^4=2401 terms
before collection, and a distinguished companion at most 7203. Native Singular
polynomial arithmetic was used, not a custom Python kernel. Accepted run
569a495e32 checked 1840 companions, 4600 fields, 16483 identities/degree
conditions and 640 negative controls, with zero failures and FINAL PASS.
The complete output is check.txt. The initial run b73a1abefa was rejected:
Singular's map requires a named polynomial argument, rather than the inline
expressions supplied there. It completed no fixtures; failed-syntax.txt retains
that tooling failure. Named source polynomials fixed the parser errors. No
larger parameter sweep is needed for this symbolic rule.

Unresolved point for review assistance: is there a nontrivial source-generated
schedule of such reductions, or a paid reader treatment, that gives more than
the already available common-core endpoint? An abstract rewrite alone does not
bound arbitrary proof-generated sources, and neither a balanced-reader property
nor a bounded number of successive consumed rows is automatic.

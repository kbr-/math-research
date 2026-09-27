\\ Verify the all-dimensional local double-pair mechanism symbolically.
\\ Work only with its universal 4-row cross block: spectator independence is
\\ proved by square characters, not tested by enlarging a dimension.
\\ Stages: exact residual derivatives; quotient identity; first two new
\\ coefficient directions; pullback of the known four-root residual ideal.
T='T; b='b; c='c; x='x; y='y;
{
my(u=T/(1+b*T),v=T/(1+c*T),cc=vector(4,j,binomial(-3/2,j-1)));
my(LA=cc[4]*u^3-cc[3]*cc[2]*u^2*v+(2/3)*(c-b)*cc[4]*cc[2]*u^3*v);
my(LB=cc[2]*cc[3]*u*v^2-cc[4]*v^3+(2/3)*(c-b)*cc[2]*cc[4]*u*v^3);
if(LA!=5/8*u^2*v||LB!=-5/8*u*v^2,error("residual derivative identity"));
if(u-v!=(c-b)*u*v,error("mixed monomial reduction"));
my(base=(1+(b+c)*T+b*c*T^2+O(T^5))^(-3/2));
my(ja=LA*base+O(T^5),jb=LB*base+O(T^5));
my(J=matrix(2,2,i,j,polcoef(if(j==1,ja,jb),i+2,T)));
if(matdet(J)!=25/64*(c-b),error("first derivative independence"));
my(e1=x+2*b,e2=2*b*x+b^2-y^2,e3=x*(b^2-y^2));
my(h=e1^2-4*e2,f=e1*h+8*e3);
if(f!=(x-2*b)*(x^2-4*y^2),error("known residual pullback"));
my(rem=lift(Mod(h^2,x^2-4*y^2)));
if(rem!=64*y^2*(y^2-b*x+b^2),error("known square remainder"));
print("PARAMETERS two distinct centers b,c; characteristic zero; no spectator sweep");
print("RESIDUAL_A = ",LA);
print("RESIDUAL_B = ",LB);
print("COEFFICIENT_JACOBIAN_ORDERS_3_4 = ",J);
print("JACOBIAN_DETERMINANT = ",matdet(J));
print("KNOWN_N3_F_PULLBACK = ",f);
print("KNOWN_N3_H_SQUARED_REMAINDER = ",rem);
print("LOCAL_ROOT_QUOTIENT_LENGTH = 4");
print("DOUBLE_PAIR_FIRST_ORDER_CONTROL_COMPLETED");
}
quit;

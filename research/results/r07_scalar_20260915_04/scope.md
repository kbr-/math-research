# R07 scalar cleanup

Final remaining R07 obligation: scalar elimination of a canonical fresh block
without increasing ordinary PC degree or changing polynomials on retained
variables. Reuse FreshENSBlock and the checked PC substitution/reuse interface.

Define complete block axioms as every companion and every fresh Boolean
equation, not the product equation. Retained base F is arbitrary: it may include
other blocks whose variables are untouched. Scalar substitution is identity on
all retained variables and sends this block's coefficients to constants.

General cleanup: over any field, if chosen constants are idempotent and every
companion image is zero, remove the block by primitive PC replay at the same
ceiling. Zero-input blocks satisfy this with all constants zero for any h.
Unit-span blocks need h>=1 and a unit combination; put its constants in row0.
Over F2 all constants are idempotent. No claim that arbitrary scalar constants
satisfy Boolean equations over a general field. No affine-degree assumption is
needed for scalar replay itself, so retain the useful broader input scope.

Boundary cases: empty input family, zero family, empty factor product h=0,
unit family at h>=1, arbitrary retained variables and zero conclusion.
Only the unit cleanup excludes h=0. Input discarded zeros can have coefficient
slots set to zero while other inputs remain; record the exact scope supplied.

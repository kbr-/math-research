"""F_2 spans of bit vectors with canonical remainders, for checks that must not reuse tools/pc_closure.py.

An independent route to a closure or kernel (a second check of a computed number) needs its own elimination;
two hand-written ones in research scripts returned non-canonical remainders (16 October 2026, a closure; 17
October 2026, independent_top.py's first run, which reduced only until the top bit was not a pivot and so gave
negative excesses). This module is that elimination, tested.

    span = Span()
    span.add(x)              # True when x was independent
    span.reduce(x)           # the canonical remainder: every pivot bit cleared, so equal classes give equal ints
    x in span
    kernel_dim(images)       # dim of {c : sum c_k images[k] = 0}, images given as ints
"""


class Span:
    """A subspace of F_2^n held as pivots keyed by leading bit."""

    def __init__(self, vecs=()):
        self.piv = {}
        for x in vecs:
            self.add(x)

    def reduce(self, x):
        """The canonical remainder of x: no bit of it is a pivot, and x - reduce(x) lies in the span."""
        r = 0
        while x:
            h = x.bit_length() - 1
            if h in self.piv:
                x ^= self.piv[h]
            else:
                r |= 1 << h
                x ^= 1 << h
        return r

    def add(self, x):
        x = self.reduce(x)
        if x:
            self.piv[x.bit_length() - 1] = x
            return True
        return False

    def __contains__(self, x):
        return self.reduce(x) == 0

    def __len__(self):
        return len(self.piv)


def kernel_dim(images):
    """The dimension of the kernel of the map sending the k-th unit vector to images[k]."""
    s = Span()
    return sum(1 for x in images if not s.add(x))

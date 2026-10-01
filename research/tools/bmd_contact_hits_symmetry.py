"""Symmetry of contact-locus points on structured planes (6 October 2026; cycles bmd-20261006-h and -l).

Reads the K points [x:y:z] listed by research/tools/bmd_cube_contact_plane_count.c and forms the nodes
a_i = x alpha_i + y beta_i + z gamma_i mod p (i = 1..N), with (alpha, beta, gamma) = (i, i^2, i^3) for --nodes poly and
(2^i, 4^i, 8^i) for --nodes geom.  For poly it reports whether the point lies on the reflection-symmetric line
z = -y / (3m), m = (N+1)/2 (a_i + a_(N+1-i) constant).  For every other point it reports the reflection centres c with
{c - a_i} = {a_i} as multisets mod p, and whether the nodes are pairwise distinct mod p.
Usage: bmd_contact_hits_symmetry.py [--nodes poly|geom] p FILE..."""
import re
import sys


def main():
    args = sys.argv[1:]
    nodes = 'poly'
    if args[0] == '--nodes':
        nodes, args = args[1], args[2:]
    p = int(args[0])
    for path in args[1:]:
        text = open(path).read()
        n = int(re.search(r'N=(\d+)', text).group(1))
        pts = [tuple(map(int, t)) for t in re.findall(r'\[(\d+):(\d+):(\d+)\]', text)]
        if nodes == 'poly':
            basis = [(i % p, i * i % p, i ** 3 % p) for i in range(1, n + 1)]
        else:
            basis = [(pow(2, i, p), pow(4, i, p), pow(8, i, p)) for i in range(1, n + 1)]
        c = (-2 * pow(3 * (n + 1), -1, p)) % p
        on, off = 0, []
        for x, y, z in pts:
            if nodes == 'poly' and ((x == 1 and (c * y - z) % p == 0) or (x == 0 and z == c * y % p)):
                on += 1
                continue
            a = [(x * al + y * be + z * ga) % p for al, be, ga in basis]
            centres = [cc for cc in range(p) if sorted((cc - v) % p for v in a) == sorted(a)]
            off.append(((x, y, z), centres, len(set(a)) == n, a))
        if nodes == 'poly':
            print('%s: N=%d, K points %d, on the symmetric line z=%d y: %d' % (path, n, len(pts), c, on))
        else:
            print('%s: N=%d, K points %d (geometric nodes)' % (path, n, len(pts)))
        for pt, centres, distinct, a in off:
            print('  point %s: nodes %s, distinct %s, reflection centres %s' % (pt, a, distinct, centres))


if __name__ == '__main__':
    main()

"""Symmetry of the contact-locus points on the polynomial-node plane (6 October 2026; cycle bmd-20261006-h).

Reads the K points [x:y:z] listed by research/tools/bmd_cube_contact_plane_count.c (BMD_PLANE=poly), forms the nodes
a_i = x i + y i^2 + z i^3 mod p (i = 1..N), and reports, for each point, whether it lies on the reflection-symmetric line
z = -y / (3m), m = (N+1)/2 (a_i + a_(N+1-i) constant), and otherwise the reflection centres c with {c - a_i} = {a_i} as
multisets mod p.  Usage: bmd_contact_hits_symmetry.py p FILE..."""
import re
import sys


def main():
    p = int(sys.argv[1])
    for path in sys.argv[2:]:
        text = open(path).read()
        n = int(re.search(r'N=(\d+)', text).group(1))
        pts = [tuple(map(int, t)) for t in re.findall(r'\[(\d+):(\d+):(\d+)\]', text)]
        # z = -y/(3m) with 3m = 3(N+1)/2, i.e. z = -2y/(3(N+1))
        c = (-2 * pow(3 * (n + 1), -1, p)) % p
        on, off = 0, []
        for x, y, z in pts:
            if (x * c * y - z) % p == 0 if x == 1 else (x == 0 and z == c * y % p):
                on += 1
                continue
            a = [(x * i + y * i * i + z * i ** 3) % p for i in range(1, n + 1)]
            centres = [cc for cc in range(p) if sorted((cc - v) % p for v in a) == sorted(a)]
            off.append(((x, y, z), centres))
        print('%s: N=%d, K points %d, on the symmetric line z=%d y: %d' % (path, n, len(pts), c, on))
        for pt, centres in off:
            print('  off-line point %s: reflection centres %s' % (pt, centres))


if __name__ == '__main__':
    main()

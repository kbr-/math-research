"""The torsion-partition values B(d, rho) of the dimension-3 law, and job strings for the symmetric kernel.

B(d, rho) (thm:cube-dimension-three-every-field): for 1 <= rho <= d, j = d - rho, q = min(rho, j); B = 0 if j = 0,
else sum_{i<=q} (p_i^2 - 1) over the balanced partition p of j + q into q parts.  On {0,1}^3 in characteristic != 2,
l_0(d+1, 4d+rho-1) = B(d, rho).
Usage: bmd_cube_torsion_partition.py DMIN DMAX [jobs|monotone]   prints the table, or with "jobs" the scan string
       3,d,m,0:B/...  for bmd_cube_symmetric_solutions (each scan stops at the first invariant top).
"""
import sys


def B(d, rho):
    j = d - rho
    if j == 0:
        return 0
    q = min(rho, j)
    s = j + q
    parts = [s // q + (1 if i < s % q else 0) for i in range(q)]
    return sum(p * p - 1 for p in parts)


def check_monotone(dmax):
    """l_0(d+1, m) on {0,1}^3 is infinite for m < 4d, B(d, m-4d+1) for 4d <= m <= 5d-1, and 0 beyond;
    it is nonincreasing in m iff B(d, rho) is nonincreasing in rho.  Returns the first violation or None."""
    for d in range(1, dmax + 1):
        for rho in range(1, d):
            if B(d, rho + 1) > B(d, rho):
                return (d, rho)
    return None


if __name__ == '__main__':
    dmin, dmax = int(sys.argv[1]), int(sys.argv[2])
    rows = [(d, rho, 4 * d + rho - 1, B(d, rho)) for d in range(dmin, dmax + 1) for rho in range(1, d + 1)]
    if len(sys.argv) > 3 and sys.argv[3] == 'monotone':
        v = check_monotone(dmax)
        print(f'B(d, rho) nonincreasing in rho for all d <= {dmax}: {v is None}' + ('' if v is None else f', first violation {v}'))
        sys.exit(0)
    if len(sys.argv) > 3 and sys.argv[3] == 'jobs':
        print('/'.join(f'3,{d},{m},0:{b}' for d, rho, m, b in rows))
    else:
        for d, rho, m, b in rows:
            print(f'd={d} rho={rho} m={m} B={b}')

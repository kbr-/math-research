"""Rooms of the window review's recorded F_2 partition-pair orbits, beside their J, a, b, I.

No statement tested: a reading of saved outputs. For each orbit of mixing_pairs_54.json (5 pigeons, 4 holes, K = 1),
mixing_pairs_65.json (6, 5, K = 2) and mixing_pairs_76.json (7, 6, K = 2) it prints the four rooms of a pair
(N - |A cup B|, |A cap B|, |B minus A|, |A minus B|) against rho = max(2K - 1, K + 2), whether B is A's complement
(congruent over F_2), and whether J > a. cor:partition-transfer-every-k gives dim J = a wherever a room reaches rho,
so an orbit with J > a and a room >= rho would contradict it. The orbits are ordered pairs and include the
complementary ones, congruent over F_2. mixing_pairs.json (4 pigeons, 3 holes, K = 1, rho = 3) holds partition
pairs among other errors; it is not read, because there every room of nonempty proper sets is at most 2 < 3
(N - |A cup B| <= 2, and |A cap B|, |A minus B|, |B minus A| <= 2), so no pair on that board has room.
"""
import json
import sys

DIR = 'research/results/common_multiplier_route_review_20261017/'
for name, n, k in (('mixing_pairs_54', 4, 1), ('mixing_pairs_65', 5, 2), ('mixing_pairs_76', 6, 2)):
    rho = max(2 * k - 1, k + 2)
    data = json.load(open(DIR + name + '.json'))
    print(f'{name}: N = {n}, K = {k}, rho = {rho}, dim W = {data["dim_W"]}')
    for o in data['orbits']:
        a, b = set(o['A']), set(o['B'])
        rooms = (n - len(a | b), len(a & b), len(b - a), len(a - b))
        comp = a | b == set(range(n)) and not a & b
        print(f'  sizes {o["sizes_and_overlap"]} A={sorted(a)} B={sorted(b)} rooms {rooms} max {max(rooms)}'
              f'{" complement" if comp else ""}: J={o["J"]} a={o["a"]} b={o["b"]} I={o["I"]}'
              f'{"  J>a" if o["J"] > o["a"] else ""}')
        if o['J'] > o['a'] and max(rooms) >= rho:
            sys.exit(f'contradiction with the corollary at {name} {o}')
print('No orbit with J > a has a room at least rho.')

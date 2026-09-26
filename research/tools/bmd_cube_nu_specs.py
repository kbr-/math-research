import itertools, random, sys
n = int(sys.argv[1]); mode = sys.argv[2]
pc = lambda r: bin(r).count('1')
out = []
if mode == 'all2':
    for nu in itertools.product(range(-1, 5), repeat=4):
        if sum(x + 1 for x in nu) >= 2:
            out.append(nu)
elif mode == 'cube':
    for d in range(1, 7):
        out.append(tuple(max(d - pc(r), -1) for r in range(1 << n)))
        out.append(tuple(max((d - pc(r)) // 2 if d - pc(r) >= 0 else -1, -1) for r in range(1 << n)))
    rng = random.Random(108)
    for _ in range(int(sys.argv[3])):
        out.append(tuple(rng.randint(-1, 5) for _ in range(1 << n)))
print('/'.join(','.join(map(str, v)) for v in out))

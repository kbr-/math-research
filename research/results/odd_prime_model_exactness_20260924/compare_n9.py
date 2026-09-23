"""Compares board (Macaulay2) and column-model excesses over the free predictions for the robust pencil classes at n = 9,
through degree 3, and checks the worst-direction criterion on the board.  Usage: python3 compare_n9.py OUT.json"""
import json, os, sys
D = os.path.dirname(os.path.abspath(__file__))
cls = json.load(open(os.path.join(D, 'n9_classes.json'))); HF = {}
for b in range(3): HF.update(json.load(open(os.path.join(D, f'm2_n9_batch{b}.json')))['HF'])
def divq(base, m):
    inv = [{0: 1, 1: -1, 2: 0}[i % 3] for i in range(4)]; c = [1, 0, 0, 0]
    for _ in range(m): c = [sum(c[i] * inv[s - i] for i in range(s + 1)) for s in range(4)]
    return [sum(base[i] * c[s - i] for i in range(s + 1)) for s in range(4)]
gam = HF['A']; Wb = divq(gam, 2); rows = []
HR = [1, 8, 27, 49]                          # column model HS_R at n = 9 (recorded, model_scaling_d3.json)
Wm = divq(HR, 2)
for k, c in enumerate(cls):
    Hb = HF.get(f'c{k}')
    if Hb is None: continue
    eb = [x - y for x, y in zip(Hb, Wb)]; em = [x - y for x, y in zip(c['model_H'], Wm)]
    rows.append(dict(counts=c['counts'], c_min=c['c_min'], board_H=Hb, board_excess=eb, model_excess=em, equal=eb == em,
                     board_free=eb == [0, 0, 0, 0], criterion_free=c['c_min'] >= 5))
    print(c['counts'], 'c_min', c['c_min'], 'board', eb, 'model', em, 'equal', eb == em, 'board free', eb == [0, 0, 0, 0], 'criterion', c['c_min'] >= 5)
print('classes', len(rows), 'board=model', sum(r['equal'] for r in rows), 'criterion agrees on board', sum(r['board_free'] == r['criterion_free'] for r in rows))
json.dump(dict(HS_A=gam, board_free=Wb, model_free=Wm, rows=rows), open(sys.argv[1], 'w'), indent=1)

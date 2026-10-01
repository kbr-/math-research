"""Summaries of the XEDGE outputs (bmd-20261004-za): per kind (balanced 0, edge 1), the range of the normalized
derivative m = |T'| |r(1+r)| / (N max|E_s|), and for edge roots the split into far (|r| >= 5) and near-real ones;
also how many roots pass the two- and three-term sector certificates (log10 margin > 0)."""
import re
for e in (2, 4):
    txt = open('research/results/bmd-20261004-za/edge-margin-e%d.txt' % e).read().split(']: ')[1]
    rows = []
    for s in re.findall(r'\[([^\[\]]+)\]', txt):
        v = [float(t.replace(' E', 'E')) for t in s.split(',')]
        if len(v) == 12:
            rows.append(v)
    for kind, name in ((0, 'balanced'), (1, 'edge')):
        R = [v for v in rows if v[0] == kind]
        groups = [('all', R)] if kind == 0 else [('far |r|>=5', [v for v in R if abs(complex(v[1], v[2])) >= 5]),
                                                 ('near |r|<5', [v for v in R if abs(complex(v[1], v[2])) < 5])]
        for g, S in groups:
            if not S:
                continue
            m = sorted(v[10] for v in S)
            print('e=%d %s %s: %d roots, m from %.3g to %.3g; two-term pass %d, three-term pass %d'
                  % (e, name, g, len(S), m[0], m[-1], sum(v[7] > 0 for v in S), sum(v[8] > 0 for v in S)))

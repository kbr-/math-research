#!/usr/bin/env python3
"""Parse the retained PARI low-degree certificate into exact field codes for an independent checker."""
import re
from pathlib import Path
s=Path('research/logs/bmd-nine-thirteen-period-20261008-9c44a4fcb6.output.txt').read_text()
assert 'NINE_THIRTEEN_INITIAL_INTERVAL_COMPLETED' in s
def code(expression):
    value=0
    for term in expression.strip().split(' + '):
        if 'a' in term:
            m=re.fullmatch(r'(?:(\d+)\*)?a(?:\^(\d+))?',term)
            assert m,term
            c=int(m[1] or 1);e=int(m[2] or 1)
        else:c=int(term);e=0
        assert 0<=c<13 and 0<=e<2
        value+=c*13**e
    assert 0<=value<169
    return value
slopes=[code(x) for x in re.search(r'POINT trial=1 slopes=\[(.*?)\]',s)[1].split(', ')]
rows=[(int(d),int(n),code(v)) for d,n,v in re.findall(r'CERTIFIED d=(\d+) N=(\d+) determinant=([^\n]+)',s)]
assert len(slopes)==9 and len(set(slopes))==9 and 0 not in slopes
assert [r[:2] for r in rows]==[(2,47),(3,140),(4,303),(5,522),(6,769)]
assert all(r[2] for r in rows)
Path('research/results/bmd-nine-thirteen-period-20261008/low-input.txt').write_text('2 12 1 1\n'+' '.join(map(str,slopes))+'\n'+'\n'.join(' '.join(map(str,r)) for r in rows)+'\n')
print('Exported five nonzero determinants, the exact field and one admissible slope tuple.')

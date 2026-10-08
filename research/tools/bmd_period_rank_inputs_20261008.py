"""Extract two retained actual matrices for the fixed backend comparison; no numerical kernel."""
import ast
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
out=ROOT/'research/results/bmd-exception-period-cover-20261008'
out.mkdir(exist_ok=True)
def assignments(path):
    result={}
    for part in path.read_text().split(';'):
        if ':=' in part:
            key,value=part.split(':=',1)
            result[key.strip()]=ast.literal_eval(value.strip())
    return result
non=assignments(ROOT/'research/results/bmd-exception-stable-projection-20261008/matrices.g')
ordinary=assignments(ROOT/'research/results/bmd-exception-relative-centres-20261008/middle.g')
for name,field,matrix in [
    ('nonordinary',non['STABLE_FIELD'],next(x[5] for x in non['STABLE_DATA'] if x[0]==0)),
    ('ordinary',ordinary['MIDDLE_FIELD'],ordinary['MIDDLE_CODES'])
]:
    n=len(matrix); degree=len(field)-1
    assert n==140 and all(len(row)==n for row in matrix)
    assert all(0<=x<3**degree for row in matrix for x in row)
    path=out/f'{name}-rank-input.txt'
    path.write_text(f'{degree} {n} {n}\n'+' '.join(map(str,field))+'\n'+
                    '\n'.join(' '.join(map(str,row)) for row in matrix)+'\n')
    print(path.relative_to(ROOT),n,degree)

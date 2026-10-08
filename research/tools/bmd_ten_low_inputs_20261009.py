#!/usr/bin/env python3
"""Convert retained exact PARI outputs into reproducible grouped determinant inputs."""
import argparse,json,re
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--series',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
manifest=[];count=0
for result in json.loads((a.series/'summary.json').read_text()):
    assert result['finished'] and result['returncode']==0 and not result['remaining']
    text=Path(result['output']).read_text();m=re.search(r'FIELD_CODES (\d+) (\d+) (\[[^\n]*\])',text);assert m
    prime,degree=int(m[1]),int(m[2]);modulus=json.loads(m[3]);assert len(modulus)==degree+1 and modulus[-1]==1
    groups=[];current=None
    for line in text.splitlines():
        m=re.fullmatch(r'POINT_CODES trial=(\d+) labels=(\[.*\])',line)
        if m:
            labels=json.loads(m[2]);assert len(labels)==10 and len(set(labels))==10 and 0 not in labels
            current={'labels':labels,'cases':[]};groups.append(current)
        m=re.fullmatch(r'CERTIFIED d=(\d+) N=(\d+) determinant_code=(\d+)',line)
        if m:
            assert current is not None
            row=list(map(int,m.groups()));assert row[2]>0;current['cases'].append(row);count+=1
    groups=[g for g in groups if g['cases']];assert sorted(c[0] for g in groups for c in g['cases'])==result['degrees']
    path=a.out/f'p{prime}-f{degree}.txt';assert not path.exists()
    lines=[' '.join(map(str,[prime,degree,*modulus])),str(len(groups))]
    for g in groups:lines.extend([' '.join(map(str,g['labels'])),str(len(g['cases'])),*[' '.join(map(str,c)) for c in g['cases']]])
    path.write_text('\n'.join(lines)+'\n');manifest.append(str(path))
(a.out/'manifest.txt').write_text('\n'.join(manifest)+'\n')
print('Exported',count,'nonzero original determinants across',len(manifest),'exact fields.')

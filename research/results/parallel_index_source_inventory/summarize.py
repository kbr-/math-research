#!/usr/bin/env python3
import argparse,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();root=Path(__file__).parent;data=json.loads((root/'inventory.json').read_text());triage=json.loads((root/'triage.json').read_text());review={i['anchor']:i for i in triage['items']}
with a.out.open('w') as f:
 for row in data['candidates']:
  note=review.get(row['anchor'],{});vals=[row['priority'],row['anchor'] or row['article'],row['title'],note.get('disposition','not_spot_reviewed'),str(row['line'])]
  f.write('\t'.join(v.replace('\t',' ').replace('\n',' ') for v in vals)+'\n')
assert data['counts']['headings']==len(data['headings'])
assert sum(data['counts']['classifications'].values())==len(data['headings'])
assert any(r['anchor']=='many-out-rows-lemma' for r in data['candidates'])
assert any(r['anchor']=='pinned-class-reduction' for r in data['scheduled'])
assert any(r['anchor']=='level-one-conservativity-checks' and any(f['id']=='conj:level-one-fresh-block-conservativity' for f in r['indexed_fragments']) for r in data['headings'])
assert not data['unresolved_index_anchors']
print(f"Saved all {len(data['candidates'])} candidates; complete heading accounting and nonheading ownership controls pass.")

import hashlib,json
from pathlib import Path
P=Path(__file__).parent;R=P.parents[2];r=json.loads((P/'citations-final.json').read_text());ids=[c['id'] for c in r['citations']]
assert len(ids)==len(set(ids))==r['counts']['citation_occurrences']
assert sum(a['citation_count'] for a in r['articles'])==len(ids)
assert sorted(i for a in r['articles'] for i in a['citation_ids'])==sorted(ids)
assert all(c['accepted_relationship'] is False for c in r['citations'])
assert all(len(c['source_claim_candidates'])==1 for c in r['citations'] if c['source_ownership']=='unique_candidate')
p=R/'research/results/parallel_index_source_inventory/inventory.json';source=json.loads(p.read_text()) if p.exists() else None
out={'valid':True,'citation_count':len(ids),'article_count':len(r['articles']),'all_article_occurrences_accounted_once':True,'automatic_relationships':0,'unresolved_index_anchors':r['unresolved_index_anchors'],'citation_snapshot_sha256':r['notebook_sha256'],'source_inventory_sha256':None if source is None else source['notebook_sha256'],'same_source_inventory_snapshot':False if source is None else r['notebook_sha256']==source['notebook_sha256'],'source_inventory_article_count':None if source is None else source['counts']['articles'],'scope':'Complete href and recognized claim-token accounting, not semantic dependency or omitted-claim adjudication.'}
(P/'acceptance.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='unresolved_index_anchors'},indent=2))

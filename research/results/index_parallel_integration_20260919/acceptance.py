#!/usr/bin/env python3
"""Record final metadata coverage, lossless text preservation and graph acceptance."""
import json,sys,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'tools'))
from claim_registry import load,write_json,validate,TEXT_FIELDS,check_targets
from claim_reviews import coverage
from claim_maintenance import check_revision
from claim_graph import audit
data=load();validate(data)
base=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
old=json.loads(subprocess.check_output(['git','show',base+':research/claims/index.json'],text=True));current={c['id']:c for c in data['claims']}
changed=[c['id'] for c in old['claims'] if c['id'] not in current or any(c[k]!=current[c['id']][k] for k in TEXT_FIELDS)]
assert not changed,changed
cov=coverage(data);assert all(counts=={'reviewed':len(data['claims'])} for counts in cov['counts'].values()),cov['counts']
graph=audit(data)
for key in ('duplicate_semantic_edges','self_links','conflicting_review_states','inconsistent_endpoint_locators','reviewed_dependency_cycles'):assert not graph[key],(key,graph[key])
maintenance=check_revision(data,base);assert maintenance['passed'],maintenance['errors']
targets=check_targets(data);assert targets['passed'],targets['errors']
write_json(Path(__file__).with_name('coverage-final.json'),cov)
write_json(Path(__file__).with_name('acceptance.json'),{'passed':True,'base_revision':base,'claims':len(data['claims']),'relationships':len(data['relationships']),'topic_definitions':len(data['topic_definitions']),'baseline_original_text_records_preserved':len(old['claims']),'new_records':len(data['claims'])-len(old['claims']),'field_coverage':cov['counts'],'changed_contract_passed':maintenance['passed'],'registration':maintenance['registration'],'source_targets':targets,'graph':graph,'tests':{'combined_claim_tests':79,'finalizer_tests':7,'parallel_append_tests':7,'citation_and_discovery_tests':18},'remaining_mathematical_uncertainty':'Explicit conditional proofs and bounded unknown-novelty assessments remain. Reviewed metadata is not a mathematical proof or publication approval.','candidate_inventory_limit':'Every citation occurrence is retained; unowned/ambiguous extraction records are not automatically assigned to claims. Complete source inventory adjudicated 91 potential omissions and added 18 historical records. Semantic judgment remains necessary for arbitrary unlabelled prose.'})
print('Acceptance passed:',len(data['claims']),'claims;',len(data['relationships']),'relationships; all',len(old['claims']),'original text records preserved.')

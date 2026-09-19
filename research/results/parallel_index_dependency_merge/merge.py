#!/usr/bin/env python3
"""Isolated merge proposal: never writes canonical registry, notebook or Git state."""
import argparse,copy,hashlib,importlib.util,json,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'tools'))
from claim_registry import load,validate,local_target,REGISTRY,references,check_targets
from claim_reviews import Evidence,make_review,claim_digest,digest
from claim_graph import audit
D=Path(__file__).parent
spec=importlib.util.spec_from_file_location('dependency_discovery',R/'tools/claim-dependencies.py');dep=importlib.util.module_from_spec(spec);spec.loader.exec_module(dep)

def core(c):return {k:c[k] for k in ('id','summary','assessment','record')}
def core_hashes(c):return {hashlib.sha256(json.dumps(core(c),sort_keys=True,ensure_ascii=a).encode()).hexdigest() for a in (True,False)}
def endpoint(e):return e['id'] if e['namespace']=='current' else e['namespace']+':'+e['id']
def normalized(edge):
 e=copy.deepcopy(edge)
 for side in ('source','target'):
  if e[side]['namespace']=='external' and e[side]['id']=='BIKPRS-1996-simulation':e[side]['id']='BIKPRS-audited-source-inputs'
 e['id']=endpoint(e['source'])+'::'+e['type']+'::'+endpoint(e['target'])
 return e

def discover():
 base=R/'research/results';out=[]
 def put(folder,names):
  for n in names:
   p=base/('parallel_index_dependencies_'+folder)/n
   if p.exists():out.append(str(p.relative_to(R)))
 put('48_160',['patch.json','patch_continued.json','patch_review_amendment.json'])
 put('160_360',['patch_160_260.json'])
 put('260_360',[f'patch-{i}-{i+10}.json' for i in range(260,360,10)])
 put('360_520',[f'batch{i}.json' for i in range(1,5)]+['provenance-resolution.json'])
 delivery=base/'parallel_index_dependencies_520_680/delivery.json'
 if delivery.exists():put('520_680',json.loads(delivery.read_text())['patch_order'])
 put('680_end',['patch_680_698.json','patch_698_710.json','patch_710_721.json','patch_721_741.json','patch_741_780.json'])
 put('780_end',['patch.json'])
 # Explicit previously reviewed six equivalent descriptions, not fuzzy equivalence.
 val=base/'parallel_index_dependencies_48_160/validation.json'
 equivalents=json.loads(val.read_text()).get('existing_scope_differences',[]) if val.exists() else []
 return {'schema_version':1,'patches':out,'equivalent_scopes':equivalents,'candidates':['research/results/index_dependency_review_20260919/candidates.json'],'discovery_scope':'Known worker README/delivery order; missing/finalizing files and coverage are reported, not assumed complete.'}

class Baselines:
 def __init__(self):self.registries={};self.content={};self.books={}
 def resolve(self,rev):return subprocess.check_output(['git','rev-parse','--verify',rev+'^{commit}'],cwd=R,text=True).strip()
 def raw(self,rev,path):
  key=(rev,str(path))
  if key not in self.content:self.content[key]=subprocess.check_output(['git','show',rev+':'+str(path)],cwd=R,stderr=subprocess.PIPE)
  return self.content[key]
 def registry(self,rev):
  if rev not in self.registries:self.registries[rev]={c['id']:c for c in json.loads(self.raw(rev,'research/claims/index.json'))['claims']}
  return self.registries[rev]
 def sha(self,rev,target):
  local=local_target(target,R)
  if not local:return None
  path,anchor=local;rel=path.relative_to(R)
  content=self.raw(rev,rel)
  if path.suffix=='.html' and anchor:
   key=(rev,str(rel))
   if key not in self.books:self.books[key]=dep.notebook_parser(content.decode())
   content=self.books[key].excerpt(anchor).encode()
  return hashlib.sha256(content).hexdigest()

def merge(data,manifest,patch_paths):
 out=copy.deepcopy(data);by={c['id']:c for c in out['claims']};ev=Evidence();bases=Baselines()
 report={'locator_normalizations':[],'conflicts':[],'warnings':[],'patches':[],'preserved_equivalent_scopes':[],'review_overrides':[],'correction_targets':[],'candidate_decisions':[],'inventory_ids':[]}
 def conflict(kind,**kw):report['conflicts'].append({'kind':kind,**kw})
 source_texts={}
 def target_name(target):
  result=manifest.get('locator_aliases',{}).get(target,target)
  local=local_target(result,R)
  if local and local[0].suffix=='.html' and local[1]:
   if local[0] not in source_texts:source_texts[local[0]]=local[0].read_text()
   text=source_texts[local[0]];book=ev.notebooks.get(local[0])
   if book is None:book=dep.notebook_parser(text);ev.notebooks[local[0]]=book
   _,_,anchor,widened=dep.source_excerpt(book,text,local[1])
   if widened:result=result.rsplit('#',1)[0]+'#'+anchor
  if target!=result:
   item={'original':target,'normalized':result,'reason':'Explicit manifest alias or existing nonheading source widened to its exact containing section.'}
   if item not in report['locator_normalizations']:report['locator_normalizations'].append(item)
  return result

 aliases={};edges={};origin={};batch_reviews={};affected=set();decisions=[]
 eq={(a['id'],a['existing_scope'],a['proposed_scope']) for a in manifest.get('equivalent_scopes',[])}
 def merge_edge(raw,where,rev=None):
  edge=normalized(raw);eid=edge['id'];aliases[raw['id']]=eid;aliases[eid]=eid
  try:edge['evidence']=[target_name(t) for t in edge['evidence']]
  except (ValueError,OSError) as ex:conflict('edge_source',edge=eid,patch=where,detail=str(ex));return
  try:
   for t in edge['evidence']:
    current=ev.sha256(t)
    if rev and current!=bases.sha(rev,t):raise ValueError('source differs from pinned revision: '+t)
  except (ValueError,OSError,subprocess.CalledProcessError) as ex:
   conflict('edge_source',edge=eid,patch=where,detail=str(ex));return
  old=edges.get(eid)
  if old:
   same=all(old[k]==edge[k] for k in ('source','target','type','scope','review_status'))
   equivalent=(eid,old['scope'],edge['scope']) in eq or (eid,edge['scope'],old['scope']) in eq
   if same or equivalent:
    if equivalent:report['preserved_equivalent_scopes'].append({'id':eid,'kept':old['scope'],'other':edge['scope'],'patch':where})
    return
   conflict('edge_scope_collision',edge=eid,kept_from=origin[eid],proposed_from=where,existing=old,proposed=edge);return
  edges[eid]=edge;origin[eid]=where
  if where!='canonical' or raw!=edge:
   for side in ('source','target'):
    if edge[side]['namespace']=='current':affected.add(edge[side]['id'])
   if edge['type'] in ('corrects','supersedes') and edge['target']['namespace']=='current':report['correction_targets'].append({'id':edge['target']['id'],'edge':eid,'scope':edge['scope'],'required_action':'Coordinator must explicitly review mathematical status; merger never changes it.'})
 for edge in data['relationships']:merge_edge(edge,'canonical')
 for path in patch_paths:
  raw=path.read_bytes();p=json.loads(raw);where=str(path.relative_to(R));rev=p.get('base_revision',p.get('baseline_revision',p.get('source_revision')))
  if rev:rev=bases.resolve(rev)
  report['patches'].append({'path':where,'sha256':hashlib.sha256(raw).hexdigest(),'revision':rev})
  for row in p.get('claims',p.get('reviews',[])):
   cid=row['id'];rowrev=rev or row.get('revision')
   try:
    if cid not in by:raise ValueError('unknown current claim')
    if not rowrev:raise ValueError('missing pinned baseline revision')
    base=bases.registry(rowrev).get(cid)
    if base is None:raise ValueError('claim missing at pinned baseline')
    supplied=next((row[k] for k in ['claim_sha256','baseline_claim_sha256','source_fields_sha256','baseline_claim_digest'] if k in row),None)
    if supplied is None:raise ValueError('missing core fingerprint')
    if supplied not in core_hashes(base):raise ValueError('supplied fingerprint does not match pinned core')
    if core(by[cid])!=core(base):raise ValueError('current core differs from pinned claim; preserve live correction')
    evidence=row.get('evidence',row.get('evidence_targets',[]));targets=[e['target'] if isinstance(e,dict) else e for e in evidence]
    hashes={a['target']:a['sha256'] for a in evidence if isinstance(a,dict)}
    hashes.update({a['target']:a['sha256'] for a in row.get('evidence_hashes',[])})
    targets=[target_name(t) for t in targets]
    hashes={target_name(t):h for t,h in hashes.items()}
    for t in targets:
     now=ev.sha256(t);then=bases.sha(rowrev,t)
     if now!=then:raise ValueError('source changed from baseline: '+t)
     if t in hashes and hashes[t]!=now:raise ValueError('supplied source fingerprint stale: '+t)
    if not targets:raise ValueError('empty source evidence')
    if row['state']=='pending' and not row.get('next_action'):raise ValueError('pending review lacks concrete next action')
    prev=batch_reviews.get(cid)
    if prev:report['review_overrides'].append({'id':cid,'earlier':prev[1],'later':where})
    batch_reviews[cid]=(row,where,rowrev,targets,base)
   except (ValueError,OSError,subprocess.CalledProcessError) as ex:conflict('claim_source',id=cid,patch=where,detail=str(ex))
  for oldid in p.get('remove_proposed_edge_ids',[]):
   eid=aliases.get(oldid,oldid)
   if eid in edges:
    if origin[eid]=='canonical':conflict('amendment_would_remove_canonical',edge=eid,patch=where)
    else:del edges[eid];del origin[eid]
   else:report['warnings'].append({'kind':'amendment_edge_absent','edge':oldid,'patch':where})
  for edge in p.get('relationships',p.get('edges',[]))+p.get('add_edges',[]):
   erev=rev or edge.get('review',{}).get('revision')
   merge_edge(edge,where,bases.resolve(erev) if erev else None)
  for decision in p.get('candidate_decisions',p.get('decisions',[])):decisions.append((decision,where))
 out['relationships']=list(edges.values())
 for cid,(row,where,rev,targets,base) in batch_reviews.items():
  current=by[cid].get('reviews',{}).get('relationships');prior=base.get('reviews',{}).get('relationships')
  if current and current!=prior and current['state']=='pending' and row['state']=='reviewed':
   # Metadata classification can also set a pending outgoing inventory. Exact current question must survive.
   if current.get('note')!=row.get('note') and manifest.get('resolve_pending_reviews',{}).get(cid)!=digest(current):
    conflict('newer_pending_review',id=cid,patch=where,current=current,proposed=row);continue
  if current and manifest.get('resolve_pending_reviews',{}).get(cid)==digest(current):
   targets=list(dict.fromkeys(targets+[a['target'] for a in current['evidence']]))
   row=dict(row);row['note']+=' Coordinator audit edges/evidence preserved; its only pending task was this source-inventory integration.'
  by[cid]['reviews']['relationships']=make_review(out,by[cid],'relationships',targets,revision=rev,date='2026-09-19',reviewer='Codex parallel dependency integration (dry run)',state=row['state'],note=row['note']+' Integrated only after pinned core/source validation.',next_action=row.get('next_action'),evidence=ev)
  report['inventory_ids'].append(cid)
 # Refresh every affected incident endpoint against the completed edge set; never claim a newly finished outgoing inventory.
 for cid in sorted(affected-set(report['inventory_ids'])):
  c=by[cid];old=c.get('reviews',{}).get('relationships');targets=[a['target'] for a in old['evidence']] if old else [a['target'] for a in references(c) if local_target(a['target'],R)]
  state=old['state'] if old else 'pending';note=(old['note'] if old else 'Outgoing dependency inventory has not been reviewed.')+' Incident metadata refreshed after scoped edge merge; outgoing scope unchanged.'
  nxt=old.get('next_action') if old else 'Review all direct source dependencies and applicable relationships for this claim.'
  try:c['reviews']['relationships']=make_review(out,c,'relationships',targets,revision=manifest['input_revision'],date='2026-09-19',reviewer='Codex parallel dependency integration (dry run)',state=state,note=note,next_action=nxt,evidence=ev)
  except (ValueError,OSError) as ex:conflict('endpoint_refresh',id=cid,detail=str(ex))
 candidate_map={}
 for name in manifest.get('candidates',[]):
  for c in json.loads((R/name).read_text())['candidates']:candidate_map[c['id']]=c
 existing_decisions={d['candidate_id']:copy.deepcopy(d) for d in out.get('dependency_decisions',[])}
 for d in existing_decisions.values():
  if d.get('relation_id'):d['relation_id']=aliases.get(d['relation_id'],d['relation_id'])
 for decision,where in decisions:
  cid=decision['candidate_id'];candidate=candidate_map.get(cid);edgeid=aliases.get(decision.get('relation_id'),decision.get('relation_id'))
  try:
   if candidate is None:raise ValueError('candidate missing from explicit inventory')
   if decision['candidate_sha256']!=candidate['candidate_sha256']:raise ValueError('candidate fingerprint mismatch')
   if not dep.is_current(candidate,out,ev):raise ValueError('candidate source/core evidence stale')
   if decision['state']=='accepted':
    e=edges.get(edgeid)
    if not e or e['source']['namespace']!='current' or e['source']['id']!=candidate['source'] or e['target']['namespace']!='current' or e['target']['id'] not in candidate['targets']:raise ValueError('accepted edge does not match candidate endpoints')
   existing_decisions[cid]={'candidate_id':cid,'candidate_sha256':candidate['candidate_sha256'],'state':decision['state'],'reason':decision['reason'],'reviewer':decision.get('reviewer','Codex parallel dependency integration (dry run)'),'date':decision.get('date','2026-09-19'),'relation_id':edgeid}
   report['candidate_decisions'].append({'id':cid,'state':decision['state'],'validated':True})
  except ValueError as ex:conflict('candidate_decision',id=cid,patch=where,detail=str(ex))
 out['dependency_decisions']=list(existing_decisions.values())
 try:validate(out);report['schema_valid']=True
 except ValueError as ex:report['schema_valid']=False;conflict('schema',detail=str(ex))
 report['correction_targets']=[a for a in report['correction_targets'] if a['edge'] in edges]
 report['target_validation']=check_targets(out)
 if not report['target_validation']['passed']:conflict('local_targets',errors=report['target_validation']['errors'])
 report['graph']=audit(out);report['inventory_count']=len(report['inventory_ids']);report['incident_endpoints_refreshed']=sorted(affected-set(report['inventory_ids']))
 report['uncovered_assigned_ids']=[c['id'] for c in data['claims'][48:866] if c['id'] not in batch_reviews and c.get('reviews',{}).get('relationships',{}).get('state')!='reviewed']
 report['ready_for_coordinator_review']=not report['conflicts'];report['canonical_written']=False
 return out,report

def safe_output(path):
 p=path.resolve()
 if not p.is_relative_to(D.resolve()):raise ValueError('Outputs must stay in this isolated merge directory')
 return p

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--manifest',type=Path);ap.add_argument('--patch',type=Path,action='append',default=[]);ap.add_argument('--candidates',action='append',default=[]);ap.add_argument('--write-manifest',type=Path);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--report',type=Path,required=True);args=ap.parse_args()
 manifest=json.loads(args.manifest.read_text()) if args.manifest else discover();manifest['candidates']=manifest.get('candidates',[])+args.candidates
 paths=[R/(p['path'] if isinstance(p,dict) else p) for p in manifest['patches']]+[p.resolve() for p in args.patch]
 for entry in manifest['patches']:
  if isinstance(entry,dict) and entry.get('sha256'):
   if hashlib.sha256((R/entry['path']).read_bytes()).hexdigest()!=entry['sha256']:raise ValueError('Manifest patch hash changed: '+entry['path'])
 original=REGISTRY.read_bytes();manifest['input_revision']=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip();manifest['input_registry_sha256']=hashlib.sha256(original).hexdigest()
 if args.write_manifest:safe_output(args.write_manifest).write_text(json.dumps(manifest,indent=2)+'\n')
 out,report=merge(json.loads(original),manifest,paths);report['input_revision']=manifest['input_revision'];report['input_registry_sha256']=manifest['input_registry_sha256']
 report['input_still_current']=REGISTRY.read_bytes()==original
 if not report['input_still_current']:report['ready_for_coordinator_review']=False;report['conflicts'].append({'kind':'live_registry_changed_during_merge'})
 safe_output(args.out).write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');safe_output(args.report).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({k:report[k] for k in ('inventory_count','schema_valid','ready_for_coordinator_review','input_still_current')}));print('Conflicts:',len(report['conflicts']),'dependency cycles:',len(report['graph']['reviewed_dependency_cycles']))
 return 0 if report['ready_for_coordinator_review'] else 1
if __name__=='__main__':raise SystemExit(main())

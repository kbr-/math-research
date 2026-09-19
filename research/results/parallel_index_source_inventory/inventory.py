#!/usr/bin/env python3
"""Inventory every research-record heading and explicit claim signal, without inference of completeness."""
import argparse,bisect,hashlib,html,importlib.util,json,re,subprocess,sys
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'tools'))
from claim_registry import load,references,local_target,write_json
spec=importlib.util.spec_from_file_location('nb',ROOT/'tools/notebook-excerpt.py');nb=importlib.util.module_from_spec(spec);spec.loader.exec_module(nb)
def plain(t):return re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]+>',' ',t))).strip()
def sha(t):return hashlib.sha256(t.encode()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();text=(ROOT/'notebook.html').read_text();book=nb.Notebook(text);data=load();record=book.anchor('research-record');nodes=[n for n in book.nodes if record['start']<=n['start']<record['end']];articles=[n for n in nodes if n['tag']=='article'];heads=[n for n in nodes if n['tag'].startswith('h')];headstarts=[n['start'] for n in heads];artstarts=[n['start'] for n in articles];lines=[0]+[m.end() for m in re.finditer('\n',text)]
byanchor=defaultdict(list);ownership=[];unresolved=[]
allids={m.group(2):(m.start(),m.group(1)) for m in re.finditer(r'<([A-Za-z0-9]+)\b[^>]*\bid="([^"]+)"[^>]*>',text)}
historical=set(re.findall(r'(?:lem|thm|prop|cor|obs|ex|audit|def|claim|conj|check):[A-Za-z0-9][A-Za-z0-9_.+-]*',(ROOT/"php_codex_handoff/manuscript/CLAIM_INDEX.md").read_text()))
for c in data['claims']:
 for r in references(c):
  loc=local_target(r['target'])
  if not loc or loc[0].resolve()!=(ROOT/'notebook.html').resolve() or not loc[1]:continue
  anchor=loc[1];byanchor[anchor].append(c['id'])
  try:
   node=book.anchor(anchor);end=node['start']+len(book.excerpt(anchor));ownership.append((node['start'],end,c['id'],anchor,node['tag']))
  except ValueError:
   if anchor in allids:
    start,tag=allids[anchor];close=text.find('</'+tag+'>',start)
    if close>=0:ownership.append((start,close+len(tag)+3,c['id'],anchor,tag))
    else:unresolved.append({'id':c['id'],'target':r['target'],'reason':'Cannot bound nonheading anchor.'})
   else:unresolved.append({'id':c['id'],'target':r['target'],'reason':'Cannot locate anchor.'})
artclaims=defaultdict(set)
for start,end,label,anchor,tag in ownership:
 k=bisect.bisect_right(artstarts,start)-1
 if k>=0 and start<articles[k]['end']:artclaims[articles[k]['anchor']].add(label)
# Whole-record markers, including those outside any indexed interval.
markers=[]
pattern=re.compile(r'<(?:strong|b)\b[^>]*>(.*?)</(?:strong|b)>',re.S|re.I)
statement=re.compile(r'^(?:(?:working|verified|conditional|exact|finite|general|corrected|revised|new|informal|structural|main|negative|counterexample|source|local|full|specialized|imported)\s+)*(?:theorem|lemma|proposition|corollary|claim|conjecture|definition|obstruction|counterexample|finite check|classification|refutation)\b',re.I)
for m in pattern.finditer(text,record['start'],record['end']):
 if statement.search(plain(m.group(1))):markers.append((m.start(),'statement_marker',plain(m.group(1)),plain(text[m.start():m.start()+1000])[:650]))
labels=re.compile(r'(?:lem|thm|prop|cor|obs|ex|audit|def|claim|conj|check|proof|note|third-party):[A-Za-z0-9][A-Za-z0-9_.+-]*')
for m in re.finditer(r'<code\b[^>]*>(.*?)</code>|`([^`\n]+)`',text[record['start']:record['end']],re.S|re.I):
 pos=record['start']+m.start();body=plain(m.group(1) or m.group(2));ls=labels.fullmatch(body)
 if ls:markers.append((pos,'explicit_label',body,plain(text[max(record['start'],pos-180):pos+450])[:650]))
for m in labels.finditer(text,record['start'],record['end']):
 pos=m.start();value=m.group(0)
 if text.rfind('<',0,pos)>text.rfind('>',0,pos):continue
 if not any(k=='explicit_label' and v==value and abs(q-pos)<120 for q,k,v,ct in markers):markers.append((pos,'explicit_label',value,plain(text[max(record['start'],pos-180):pos+450])[:650]))
for m in re.finditer(r'<p\b[^>]*>(.*?)</p>',text[record['start']:record['end']],re.S|re.I):
 pos=record['start']+m.start();body=plain(m.group(1))
 if 'entry-meta' not in m.group(0).split('>',1)[0] and statement.search(body) and not re.match(r'\s*<(?:strong|b)\b',m.group(1),re.I):markers.append((pos,'paragraph_statement',body[:100],body[:650]))
markers.sort();byhead=defaultdict(list)
for pos,kind,value,context in markers:
 k=bisect.bisect_right(headstarts,pos)-1
 if k>=0:byhead[k].append({'kind':kind,'value':value,'line':bisect.bisect_right(lines,pos),'context':context,'registered_label':value in {c['id'] for c in data['claims']} if kind=='explicit_label' else None,'historical_label':value in historical if kind=='explicit_label' else None,'fragment_owners':[label for lo,hi,label,anchor,tag in ownership if lo<=pos<hi and tag not in ('article','h3','h4','h5','h6')]})
procedural=re.compile(r'\b(proof|setup|notation|scope|degree accounting|budget|check|evidence|timing|process|next|remaining|outcome|summary|review|record|reproduc|framework|plan|inventory|implementation|maintenance|metadata|validation|source audit)\b',re.I)
mathword=re.compile(r'\b(theorem|lemma|corollary|proposition|conjecture|classification|criterion|equivalence|counterexample|obstruction|separation|lower bound|upper bound|frontier|identity|normal form|reduction)\b',re.I)
rows=[]
for i,node in enumerate(heads):
 start=node['start'];end=heads[i+1]['start'] if i+1<len(heads) else record['end'];k=bisect.bisect_right(artstarts,start)-1;article=articles[k] if k>=0 and start<articles[k]['end'] else None
 if article:end=min(end,article['close'])
 body=text[start:end];title=plain(text[start:node['end']]);direct=sorted(set(byanchor[node['anchor']])) if node['anchor'] else []
 enclosing=[{'id':label,'anchor':anchor,'tag':tag} for lo,hi,label,anchor,tag in ownership if lo<start<hi and tag!='article'];broad=[label for lo,hi,label,anchor,tag in ownership if lo<=start<hi and tag=='article'];signals=byhead[i]
 theorem=bool(mathword.search(title));mathcount=body.count('\\(')+body.count('\\[');strong=any(s['kind'] in ('statement_marker','paragraph_statement') and not s['fragment_owners'] for s in signals)
 unknown=[s for s in signals if s['kind']=='explicit_label' and not s['registered_label'] and not s['historical_label']]
 scheduled=node['anchor']=='pinned-class-reduction'
 if direct:status='directly_indexed';priority='covered'
 elif node['tag']=='h3' and not node['anchor'] and not strong and not unknown:status='entry_title_overview';priority='low'
 elif scheduled:status='scheduled_root_addition';priority='scheduled'
 elif enclosing:status='inside_indexed_heading';priority='review_embedded_statement' if strong or theorem else 'likely_subsection'
 elif unknown:status='unowned_explicit_label';priority='high'
 elif strong or theorem:status='unowned_statement_signal';priority='high' if not procedural.search(title) else 'medium'
 elif mathcount and not procedural.search(title):status='unowned_mathematical_section';priority='medium'
 elif mathcount:status='unowned_setup_or_proof';priority='low'
 else:status='unowned_nonmathematical_or_unrecognized';priority='low'
 rows.append({'anchor':node['anchor'],'article':article['anchor'] if article else None,'line':bisect.bisect_right(lines,start),'title':title,'direct_claims':direct,'enclosing_heading_claims':enclosing,'broad_article_claims':sorted(set(broad)),'sibling_article_claims':sorted(artclaims[article['anchor']]) if article else [],'classification':status,'priority':priority,'math_delimiters':mathcount,'signals':signals,'section_sha256':sha(body),'indexed_fragments':[{'id':label,'anchor':anchor,'tag':tag} for lo,hi,label,anchor,tag in ownership if start<=lo<end and tag not in ('article','h3','h4','h5','h6')],'tag':node['tag'],'short_evidence':plain(body[len(text[start:node['end']]):])[:500]})
report={'schema_version':1,'baseline_revision':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'notebook_sha256':sha(text),'registry_sha256':sha((ROOT/'research/claims/index.json').read_text()),'scope':'Full research-record HTML traversed, including unindexed articles and heading regions. Every heading and all matched strong/bold statement markers and formatted or plain-text claim labels retained; HTML attributes excluded. Signals are heuristic candidates, not assertions of omitted independent claims; arbitrary unlabeled prose mathematics can escape detection. Article-level index ownership is reported as broad, not treated as proof that each internal statement has its own claim.','counts':{'articles':len(articles),'headings':len(rows),'statement_and_label_signals':len(markers),'classifications':dict(Counter(r['classification'] for r in rows)),'priorities':dict(Counter(r['priority'] for r in rows))},'unresolved_index_anchors':unresolved,'headings':rows,'candidates':[r for r in rows if r['priority'] in ('high','medium','review_embedded_statement')],'all_unowned_headings':[r for r in rows if r['classification'] not in ('directly_indexed','entry_title_overview')],'scheduled':[r for r in rows if r['priority']=='scheduled']}
write_json(a.out,report);print(json.dumps(report['counts'],indent=2));print('Candidate count:',len(report['candidates']))

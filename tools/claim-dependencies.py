#!/usr/bin/env python3
"""Discover dependency evidence, not proof dependencies, with bounded review output."""
import argparse
from collections import defaultdict
import hashlib
import html
import importlib.util
import json
from pathlib import Path
import re
import sys

from claim_registry import ROOT, REGISTRY, load, local_target, references, write_json, require, validate
from claim_reviews import Evidence


def hashed(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def notebook_parser(text):
    spec=importlib.util.spec_from_file_location('notebook_excerpt',ROOT/'tools/notebook-excerpt.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.Notebook(text)


def lean_code(text):
    """Mask nested comments and strings, retaining offsets and line numbers."""
    out=list(text);i=0;depth=0;quoted=False
    while i<len(text):
        if depth:
            if text.startswith('/-',i): depth+=1;size=2
            elif text.startswith('-/',i): depth-=1;size=2
            else: size=1
        elif quoted:
            if text[i]=='\\': size=min(2,len(text)-i)
            else:
                if text[i]=='"': quoted=False
                size=1
        elif text.startswith('/-',i): depth=1;size=2
        elif text.startswith('--',i):
            end=text.find('\n',i);size=(len(text) if end<0 else end)-i
        elif text[i]=='"': quoted=True;size=1
        else: i+=1;continue
        for j in range(i,i+size):
            if out[j]!='\n':out[j]=' '
        i+=size
    return ''.join(out)


def source_excerpt(book, text, anchor):
    try:
        node=book.anchor(anchor)
        return book.excerpt(anchor),node['start'],anchor,False
    except ValueError:
        matches=list(re.finditer(r'\bid=["\']'+re.escape(anchor)+r'["\']',text))
        require(len(matches)==1,'Missing or ambiguous source anchor: '+anchor)
        position=matches[0].start()
        for node in sorted(book.nodes,key=lambda n:n['start'],reverse=True):
            if not node['anchor'] or node['start']>position:continue
            region=book.excerpt(node['anchor'])
            if node['start']<=position<node['start']+len(region):
                return region,node['start'],node['anchor'],True
        raise ValueError('No containing passage for '+anchor)

def scan(data, root=ROOT):
    text=(root/'notebook.html').read_text();book=notebook_parser(text)
    ids={c['id'] for c in data['claims']};anchors=defaultdict(set);files=defaultdict(set)
    fingerprints={c['id']:hashed({k:c[k] for k in ('id','summary','assessment','record')}) for c in data['claims']}
    regions=defaultdict(set);problems=[]
    for c in data['claims']:
        for r in references(c):
            local=local_target(r['target'],root)
            if not local:continue
            path,anchor=local
            if path.resolve()==(root/'notebook.html').resolve() and anchor:
                anchors[anchor].add(c['id']);regions[c['id']].add(anchor)
            elif path.suffix=='.lean':files[path.resolve()].add(c['id'])
    # A few historical index rows link only to the manuscript and Lean file.
    # Their explicit Lean Source headers supply the later formalization record.
    for path,owners in files.items():
        header=re.match(r'\s*/-(.*?)-/',path.read_text(),re.S)
        if not header:continue
        for target in re.findall(r'^Source:\s*(\S+)',header.group(1),re.M):
            local=local_target(target,root)
            if local and local[0].resolve()==(root/'notebook.html').resolve() and local[1]:
                anchors[local[1]].update(owners)
                for owner in owners:regions[owner].add(local[1])
    candidates={};processed=set();source_articles=defaultdict(set);other_references=[];widened_regions=[]
    for anchor,owners in anchors.items():
        try:
            _,_,resolved,_=source_excerpt(book,text,anchor)
            node=book.anchor(resolved)
        except ValueError as exc:problems.append({'anchor':anchor,'error':str(exc)});continue
        article=node
        while article and article['tag']!='article':article=article['scope']
        if article: source_articles[article['anchor']].update(owners)

    def add(source,targets,method,locator,region,token,line,context,shared=False,hint=None):
        targets=sorted(set(targets)-{source})
        if not targets:return
        key={'source':source,'targets':targets,'method':method,'locator':locator,'token':token}
        identifier=hashed(key)[:24]
        if identifier not in candidates:
            candidates[identifier]=dict(key,id=identifier,source_sha256=hashlib.sha256(region.encode()).hexdigest(),
                source_claim_sha256=fingerprints[source],target_claim_sha256={t:fingerprints[t] for t in targets},
                proposed_type='depends_on' if method=='lean_declaration_reference' else 'cites',
                ownership_ambiguous=shared or len(targets)!=1,
                hint=hint,occurrences=[],existing_relationships=[e['id'] for e in data['relationships']
                    if e['source']['namespace']=='current' and e['source']['id']==source
                    and e['target']['namespace']=='current' and e['target']['id'] in targets])
        candidates[identifier]['occurrences'].append({'line':line,'context':context})
        return candidates[identifier]

    equation_definitions=defaultdict(list)
    for anchor,owners in anchors.items():
        try:region,offset,actual_anchor,widened=source_excerpt(book,text,anchor)
        except ValueError:continue
        for token in sorted(set(re.findall(r'\\tag\{([^}]+)\}',region))):
            item={'claims':sorted(owners),'locator':'https://kbr.is-a.dev/math-research/#'+actual_anchor,
                  'sha256':hashlib.sha256(region.encode()).hexdigest(),'widened':widened}
            if item not in equation_definitions[token]:equation_definitions[token].append(item)

    for source,region_anchors in regions.items():
        for anchor in sorted(region_anchors):
            try:region,offset,actual_anchor,widened=source_excerpt(book,text,anchor)
            except ValueError as exc:problems.append({'claim':source,'anchor':anchor,'error':str(exc)});continue
            processed.add(source)
            locator='https://kbr.is-a.dev/math-research/#'+actual_anchor
            if widened:widened_regions.append({'claim':source,'anchor':anchor,'containing_anchor':actual_anchor})
            base_line=text.count('\n',0,offset)+1
            own_tags=set(re.findall(r'\\tag\{([^}]+)\}',region))
            for match in re.finditer(r'\(([A-Za-z][A-Za-z0-9_.-]*)\)',region):
                token=match.group(1)
                if token in own_tags or token not in equation_definitions:continue
                definitions=equation_definitions[token]
                targets={label for item in definitions for label in item['claims']}
                candidate=add(source,targets,'equation_reference',locator,region,token,
                    base_line+region.count('\n',0,match.start()),
                    strip_markup(region[max(0,match.start()-180):match.end()+180]),
                    widened or len(anchors[anchor])>1 or len(definitions)>1,
                    'Named equation reference; definitions may be shared/reused. Check proof role and scope.')
                if candidate:candidate['definition_evidence']=definitions
            for match in re.finditer(r'<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',region,re.S):
                href=match.group(1);target_anchor=None
                if href.startswith('#'):target_anchor=href[1:]
                else:
                    try:local=local_target(href,root)
                    except ValueError:local=None
                    if local and local[0].resolve()==(root/'notebook.html').resolve():target_anchor=local[1]
                if not target_anchor:
                    other_references.append({'claim':source,'locator':locator,'target':href})
                    continue
                targets=anchors.get(target_anchor,set());shared=widened or len(anchors[anchor])>1
                if not targets:
                    try:
                        node=book.anchor(target_anchor)
                        while node and node['tag']!='article':node=node['scope']
                        targets=source_articles.get(node['anchor'],set()) if node else set()
                        shared=True
                    except ValueError: targets=set()
                start=region.rfind('<p',0,match.start());end=region.find('</p>',match.end())
                paragraph=region[max(0,start):end+4] if start>=0 and end>=0 else region[max(0,match.start()-160):match.end()+160]
                clean=re.sub(r'\s+',' ',strip_markup(paragraph)).strip()
                hint='dependency-language; check negation and scope' if re.search(r'depend|\buses?\b|\bby\b',clean,re.I) else None
                if targets:
                    add(source,targets,'notebook_link',locator,region,href,
                        base_line+region.count('\n',0,match.start()),clean,shared,hint)
                else:problems.append({'claim':source,'locator':locator,'unmapped_link':href})
            for match in re.finditer(r'(?:<code>|`)((?:lem|thm|cor|prop|def|audit|obs|ctx|conj|third-party):[^<`\s]+)(?:</code>|`)',region):
                if match.group(1) in ids:
                    add(source,[match.group(1)],'claim_label',locator,region,match.group(1),
                        base_line+region.count('\n',0,match.start()),
                        strip_markup(region[max(0,match.start()-120):match.end()+120]),widened or len(anchors[anchor])>1)

    decls=defaultdict(set);sources={}
    for path,owners in files.items():
        source=path.read_text();sources[path]=source
        header=re.match(r'\s*/-(.*?)-/',source,re.S)
        declaration_header=re.search(r'^Declarations?:\s*(.*?)(?=\n[A-Z][A-Za-z ]*:|\Z)',header.group(1),re.M|re.S) if header else None
        if declaration_header:
            for name in re.findall(r'\bMathResearch\.[\w.]+',declaration_header.group(1)):
                decls[name].update(owners)
    short=defaultdict(set)
    for name,owners in decls.items():short[name.rsplit('.',1)[-1]].update(owners)
    for path,owners in files.items():
        source=sources[path];code=lean_code(source);locator='../'+str(path.relative_to(root))
        for match in re.finditer(r'^import\s+((?:claims|third-party-claims)\.\S+)',code,re.M):
            target=(root/'formalization'/match.group(1).replace('.','/')).with_suffix('.lean').resolve()
            for owner in owners:
                add(owner,files.get(target,set()),'lean_import',locator,source,match.group(1),
                    source.count('\n',0,match.start())+1,match.group(0),len(owners)>1,
                    'Module import only; may be unused or support another claim.')
        code=re.sub(r'^import[^\n]*',lambda m:' '*len(m.group()),code,flags=re.M)
        for match in re.finditer(r'\b(?:MathResearch\.)?[A-Za-z_][A-Za-z_0-9.]*',code):
            token=match.group();targets=decls.get(token,short.get(token,set()))
            if not targets:continue
            context=source[max(0,match.start()-100):match.end()+100]
            for owner in owners:
                add(owner,targets,'lean_declaration_reference',locator,source,token,
                    source.count('\n',0,match.start())+1,context,len(owners)>1,
                    'Identifier occurrence, not elaborated dependency; inspect owning theorem and name resolution.')
    values=list(candidates.values())
    for c in values:
        c['candidate_sha256']=hashed({k:c[k] for k in ('source','targets','method','locator','token',
            'source_sha256','source_claim_sha256','target_claim_sha256','ownership_ambiguous')})
        if 'definition_evidence' in c:
            c['candidate_sha256']=hashed([c['candidate_sha256'],c['definition_evidence']])
    return {'schema_version':1,'claims':len(ids),'claims_with_notebook_regions':len(processed),'lean_files':len(files),
            'claims_without_notebook_regions':sorted(ids-processed),
            'candidate_count':len(values),'candidates':values,'unresolved':problems,
            'external_or_file_references':other_references,
            'widened_source_regions':widened_regions,
            'scope':'Generated evidence candidates only. No relationship is accepted by this scan.'}


def is_current(candidate, data, evidence=None):
    evidence=evidence or Evidence()
    try:
        if evidence.sha256(candidate['locator'])!=candidate['source_sha256']:return False
    except (OSError,ValueError):return False
    for item in candidate.get('definition_evidence',[]):
        try:
            if evidence.sha256(item['locator'])!=item['sha256']:return False
        except (OSError,ValueError):return False
    claims={c['id']:c for c in data['claims']}
    for key,expected in {candidate['source']:candidate['source_claim_sha256'],**candidate['target_claim_sha256']}.items():
        if key not in claims or hashed({k:claims[key][k] for k in ('id','summary','assessment','record')})!=expected:return False
    return True


def decision_state(candidate, data, evidence=None):
    if not is_current(candidate,data,evidence):return 'stale'
    decision=next((d for d in data.get('dependency_decisions',[]) if d['candidate_id']==candidate['id']),None)
    if decision is None:return 'unreviewed'
    return decision['state'] if decision['candidate_sha256']==candidate['candidate_sha256'] else 'stale'


def record_decision(data, candidate, *, state, reason, reviewer, date, relation_id=None, evidence=None):
    require(bool(reason.strip()) and bool(reviewer.strip()),'Decision needs a reason and reviewer')
    require(is_current(candidate,data,evidence),'Candidate evidence is stale; rescan before deciding')
    if state=='accepted':
        edge=next((e for e in data['relationships'] if e['id']==relation_id),None)
        require(edge is not None,'Accepted candidate must name an already recorded relationship')
        require(edge['source']['namespace']=='current' and edge['source']['id']==candidate['source']
                and edge['target']['namespace']=='current' and edge['target']['id'] in candidate['targets'],
                'Recorded relationship does not match candidate endpoints')
    record={'candidate_id':candidate['id'],'candidate_sha256':candidate['candidate_sha256'],
            'state':state,'reason':reason,'reviewer':reviewer,'date':date,'relation_id':relation_id}
    records=data.setdefault('dependency_decisions',[])
    prior=next((d for d in records if d['candidate_id']==candidate['id']),None)
    if prior is None:records.append(record)
    else:prior.update(record)
    return validate(data)


def strip_markup(text):
    # Only actual known markup, never a mathematical inequality such as q<n.
    tags='p|div|span|strong|em|b|i|a|code|sup|sub|br|small|h[1-6]|table|thead|tbody|tr|th|td|ul|ol|li|details|summary'
    pieces=re.split(r'(\\\([\s\S]*?\\\)|\\\[[\s\S]*?\\\])',text)
    return ''.join(part if i%2 else re.sub(r'</?(?:'+tags+r')(?:\s+[^<>]*?)?\s*/?>',' ',part,flags=re.I)
                   for i,part in enumerate(pieces))


def metadata_packet(data, label, root=ROOT, limit=6, width=700):
    """Bounded retrieval evidence only; omissions and ownership remain explicit."""
    claim=next((c for c in data['claims'] if c['id']==label),None)
    require(claim is not None, 'Unknown claim: '+label)
    require(limit>0 and width>0, 'Packet limits must be positive')
    text=(root/'notebook.html').read_text();book=notebook_parser(text)
    passages=[];seen=set()
    for reference in references(claim):
        local=local_target(reference['target'],root)
        if not local or local[0].resolve()!=(root/'notebook.html').resolve() or not local[1]:continue
        region,offset,anchor,widened=source_excerpt(book,text,local[1])
        if anchor in seen:continue
        seen.add(anchor)
        blocks=[]
        for match in re.finditer(r'<(p|div)\b[^>]*>.*?</\1>',region,re.S):
            body=html.unescape(strip_markup(match.group()))
            body=re.sub(r'\s+',' ',body).strip()
            if not body:continue
            signal=bool(re.search(r'working|lemma|theorem|status|counter|hypothes|requir|conditional|'
                                 r'\bnot\b|\bno\b|scope|remaining|supersed|correct|conjecture',body,re.I))
            blocks.append({'line':text.count('\n',0,offset+match.start())+1,
                           'text':body,'signal':signal,'formula':match.group(1)=='div'})
        # Preserve document order, including a formula immediately after a signal.
        selected=[]
        for i,block in enumerate(blocks):
            if block['signal'] or (block['formula'] and i and blocks[i-1]['signal']):selected.append(block)
        if not selected:selected=blocks[:1]
        excerpts=[{'line':b['line'],'text':b['text'][:width],
                   'truncated':len(b['text'])>width} for b in selected[:limit]]
        passages.append({'target':'https://kbr.is-a.dev/math-research/#'+anchor,
                         'source_sha256':hashlib.sha256(region.encode()).hexdigest(),
                         'widened':widened,'excerpts':excerpts,
                         'omitted_selected_blocks':max(0,len(selected)-limit),
                         'total_blocks':len(blocks),'included_blocks':len(excerpts)})
    return {'id':label,'summary':claim['summary'],'assessment':claim['assessment'],
            'proof_ready':False,
            'formalization_scope':{'status':claim['formalization']['status'],'scope':claim['formalization']['scope']},
            'references':references(claim),'passages':passages,
            'scope':'Selected retrieval evidence, not a complete proof audit. Original assessment is '
                    'preserved verbatim. Check source when meaning, qualifications or ownership remain unclear.'}


def packet_text(packet):
    lines=[packet['id'],'Summary: '+packet['summary'],'Assessment: '+packet['assessment'],
           'Orientation only: selected excerpts do not establish proof readiness.']
    formal=packet['formalization_scope']
    if formal['status'] not in (None,'no_record','not_started'):
        lines.append('Recorded formalization: '+str(formal['status'])+'; '+str(formal['scope']))
    for passage in packet['passages']:
        lines.append('Source: '+passage['target']+(' [widened; ownership needs review]' if passage['widened'] else ''))
        for item in passage['excerpts']:
            lines.append(str(item['line'])+': '+item['text']+(' [truncated]' if item['truncated'] else ''))
        lines.append(f"Blocks: {passage['included_blocks']}/{passage['total_blocks']}; "
                     f"{passage['omitted_selected_blocks']} additional signal blocks omitted.")
    lines.append(packet['scope'])
    return '\n'.join(lines)+'\n'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    s=sub.add_parser('scan');s.add_argument('--out',type=Path,required=True)
    v=sub.add_parser('show');v.add_argument('--input',type=Path,required=True)
    v.add_argument('--claim',required=True);v.add_argument('--method');v.add_argument('-n',type=int,default=10)
    v.add_argument('--state',choices=['unreviewed','accepted','rejected','pending','stale'])
    d=sub.add_parser('decide');d.add_argument('--input',type=Path,required=True)
    d.add_argument('--candidate',required=True);d.add_argument('--state',choices=['accepted','rejected','pending'],required=True)
    d.add_argument('--reason',required=True);d.add_argument('--reviewer',required=True);d.add_argument('--date',required=True)
    d.add_argument('--relation-id')
    p=sub.add_parser('packet',help='Compact status, scope and qualification evidence')
    p.add_argument('--claim',required=True);p.add_argument('-n',type=int,default=6)
    p.add_argument('--width',type=int,default=700);p.add_argument('--out',type=Path)
    s=sub.add_parser('record-scan',help='Inventory every research-article citation, including unindexed regions')
    s.add_argument('--out',type=Path,required=True)
    v=sub.add_parser('record-show',help='Bounded lookup in a complete record citation inventory')
    v.add_argument('--input',type=Path,required=True);v.add_argument('--article');v.add_argument('--claim')
    v.add_argument('--ownership',choices=['unique_candidate','ambiguous_candidates','broad_article_only','unowned'])
    v.add_argument('--kind',choices=['hyperlink','explicit_claim_label']);v.add_argument('-n',type=int,default=10)
    v.add_argument('--out',type=Path)
    args=parser.parse_args()
    if args.command=='record-scan':
        from record_citations import scan_record
        report=scan_record(load());write_json(args.out,report)
        print(json.dumps(report['counts'],indent=2));print('Complete occurrence inventory saved; no relationships inferred.')
    elif args.command=='record-show':
        from record_citations import select,sha
        require(args.n>0,'Limit must be positive')
        report=json.loads(args.input.read_text());require(report.get('method')=='full-record-html-citations-v1','Wrong report format')
        rows=select(report,article=args.article,claim=args.claim,ownership=args.ownership,kind=args.kind)
        stale=sha((ROOT/'notebook.html').read_text())!=report['notebook_sha256']
        registry_stale=sha(json.dumps(load(),sort_keys=True,ensure_ascii=False))!=report['registry_sha256']
        if args.out:write_json(args.out,{'source_report':str(args.input),'notebook_changed':stale,'registry_changed':registry_stale,'citations':rows,'count':len(rows)})
        for r in rows[:args.n]:
            print(r['id'],r['article'],r['line'],r['kind'],r['source_ownership'],'=>',r['target'])
            print('  Heading:',r['heading']);print('  Claims:',','.join(r['source_claim_candidates']) or '(none)')
            print('  Context:',r['context'][:400])
        print(f'{len(rows)} occurrences; {max(0,len(rows)-args.n)} omitted. Notebook changed since scan: {stale}; registry changed: {registry_stale}. No proof dependency inferred.')
    elif args.command=='packet':
        packet=metadata_packet(load(),args.claim,limit=args.n,width=args.width)
        if args.out:write_json(args.out,packet)
        print(packet_text(packet),end='')
    elif args.command=='scan':
        report=scan(load());write_json(args.out,report)
        print(json.dumps({k:v for k,v in report.items() if k not in ('candidates','unresolved','external_or_file_references','widened_source_regions')},indent=2))
        print(f"Broadened source regions (flagged ambiguous): {len(report['widened_source_regions'])}")
        print(f"Unresolved mappings: {len(report['unresolved'])}; complete evidence saved.")
    elif args.command=='show':
        require(args.n>0,'Limit must be positive')
        report=json.loads(args.input.read_text())
        data=load();evidence=Evidence()
        rows=[c for c in report['candidates'] if c['source']==args.claim and (not args.method or c['method']==args.method)
              and (not args.state or decision_state(c,data,evidence)==args.state)]
        for row in rows[:args.n]:
            print(row['id'],decision_state(row,data,evidence),row['method'],'=>',','.join(row['targets']))
            print('  Source:',row['locator'],'Ambiguous ownership:',row['ownership_ambiguous'])
            context=re.sub(r'\s+',' ',row['occurrences'][0]['context'])
            print('  Evidence:',context[:400]+('…' if len(context)>400 else ''))
        print(f'{len(rows)} candidates; {max(0,len(rows)-args.n)} omitted. Discovery alone does not confirm dependencies.')
    else:
        report=json.loads(args.input.read_text());data=load()
        candidate=next((c for c in report['candidates'] if c['id']==args.candidate),None)
        require(candidate is not None,'Unknown candidate')
        write_json(REGISTRY,record_decision(data,candidate,state=args.state,reason=args.reason,
                   reviewer=args.reviewer,date=args.date,relation_id=args.relation_id))
        print('Recorded candidate decision; no relationship was created automatically.')


if __name__=='__main__':
    try:main()
    except (OSError,ValueError) as exc:sys.exit(f'claim-dependencies: {exc}')

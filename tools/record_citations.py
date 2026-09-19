"""Complete research-article citation occurrences, without automatic graph edges."""
from bisect import bisect_right
from collections import Counter, defaultdict
import hashlib
from html import unescape
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

from claim_registry import ROOT, local_target, references

LABEL = re.compile(r'\b(?:lem|thm|prop|cor|obs|ex|audit|def|claim|conj|check|proof|note|local|criterion|third-party|imp|draft|ctx|open|q|rem):[A-Za-z0-9][A-Za-z0-9_.+-]*')
VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def plain(text):
    return re.sub(r'\s+', ' ', unescape(re.sub(r'<[^>]*>', ' ', text))).strip()


class CitationHTML(HTMLParser):
    """Record DOM occurrences; comments and attributes are never claim-label prose."""
    def __init__(self, text, label_pattern=LABEL):
        super().__init__(convert_charrefs=False)
        self.label_pattern=label_pattern
        self.text=text; self.offsets=[0]+[m.end() for m in re.finditer('\n',text)]
        self.stack=[];self.ids=defaultdict(list);self.links=[];self.labels=[];self.open_links=[]
        self.feed(text);self.close()

    def pos(self):
        line,column=self.getpos();return self.offsets[line-1]+column

    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs);node={'tag':tag,'start':self.pos(),'end':None,'anchor':attrs.get('id')}
        if node['anchor']:self.ids[node['anchor']].append(node)
        if tag=='a' and 'href' in attrs:
            link={'offset':node['start'],'target':attrs['href'],'text_parts':[]}
            self.links.append(link);self.open_links.append(link)
        if tag not in VOID:self.stack.append(node)
        else:node['end']=self.pos()+len(self.get_starttag_text())

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag,attrs)
        if tag not in VOID:self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag=='a' and self.open_links:self.open_links.pop()
        for i in range(len(self.stack)-1,-1,-1):
            if self.stack[i]['tag']==tag:
                node=self.stack[i];end=self.text.find('>',self.pos())+1
                node['end']=end;del self.stack[i:];break

    def handle_data(self, value):
        if any(n['tag'] in {'script','style'} for n in self.stack):return
        for link in self.open_links:link['text_parts'].append(value)
        for match in self.label_pattern.finditer(value):
            self.labels.append({'offset':self.pos()+match.start(),'target':match.group().rstrip('.'),'text':match.group().rstrip('.')})

    def handle_entityref(self, name):
        for link in self.open_links:link['text_parts'].append(unescape('&'+name+';'))

    def handle_charref(self, name):
        for link in self.open_links:link['text_parts'].append(unescape('&#'+name+';'))


def scan_record(data, root=ROOT):
    root=Path(root);text=(root/'notebook.html').read_text()
    spec=importlib.util.spec_from_file_location('record_notebook',ROOT/'tools/notebook-excerpt.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);book=module.Notebook(text)
    record=book.anchor('research-record')
    prefixes={c['id'].split(':',1)[0] for c in data['claims']}
    extra='|'.join(re.escape(p) for p in sorted(prefixes))
    pattern=re.compile(LABEL.pattern.replace('(?:', '(?:'+extra+'|', 1))
    dom=CitationHTML(text,pattern)
    articles=[n for n in book.nodes if n['tag']=='article' and record['start']<=n['start']<record['end']]
    starts=[n['start'] for n in articles]
    def article_at(offset):
        k=bisect_right(starts,offset)-1
        return articles[k] if k>=0 and offset<articles[k]['end'] else None
    anchors=defaultdict(set);intervals=[];unresolved=[]
    for claim in data['claims']:
        for ref in references(claim):
            loc=local_target(ref['target'],root)
            if not loc or loc[0].resolve()!=(root/'notebook.html').resolve() or not loc[1]:continue
            anchor=loc[1];anchors[anchor].add(claim['id'])
            try:
                n=book.anchor(anchor);lo=n['start'];hi=lo+len(book.excerpt(anchor));tag=n['tag']
            except ValueError:
                options=dom.ids.get(anchor,[])
                if len(options)!=1 or options[0]['end'] is None:
                    unresolved.append({'claim':claim['id'],'target':ref['target'],'reason':'Missing, duplicate or unclosed anchor.'});continue
                n=options[0];lo,hi,tag=n['start'],n['end'],n['tag']
            intervals.append({'start':lo,'end':hi,'id':claim['id'],'anchor':anchor,'tag':tag})
    article_claims=defaultdict(set)
    for i in intervals:
        a=article_at(i['start'])
        if a:article_claims[a['anchor']].add(i['id'])
    by_article=defaultdict(list);headings=defaultdict(list)
    for h in book.nodes:
        if h['tag'].startswith('h'):
            a=article_at(h['start'])
            if a:headings[a['anchor']].append(h)
    historical_path=root/'php_codex_handoff/manuscript/CLAIM_INDEX.md'
    historical=set(LABEL.findall(historical_path.read_text())) if historical_path.exists() else set()
    known={c['id'] for c in data['claims']};counts=Counter();ordinal=Counter();out=[]
    all_events=[('hyperlink',r) for r in dom.links]+[('explicit_claim_label',r) for r in dom.labels]
    all_events.sort(key=lambda z:(z[1]['offset'],z[0]))
    record_outside=[]
    for kind,event in all_events:
        pos=event['offset']
        if not record['start']<=pos<record['end']:continue
        article=article_at(pos)
        if article is None:
            record_outside.append({'kind':kind,'line':bisect_right(dom.offsets,pos),'target':event['target']});continue
        aid=article['anchor'];heads=[h for h in headings[aid] if h['start']<=pos];heading=heads[-1] if heads else None
        contained=[i for i in intervals if i['start']<=pos<i['end']]
        narrow=[i for i in contained if i['tag']!='article'];broad=[i for i in contained if i['tag']=='article']
        if narrow:
            size=min(i['end']-i['start'] for i in narrow);nearest=[i for i in narrow if i['end']-i['start']==size]
        else:nearest=[]
        owners=sorted({i['id'] for i in nearest});ownership='unique_candidate' if len(owners)==1 else 'ambiguous_candidates' if owners else 'broad_article_only' if broad else 'unowned'
        target=event['target'];target_ids=[];target_state=None;namespace=None
        if kind=='explicit_claim_label':
            target_ids=[target] if target in known else []
            namespace='current_and_historical' if target in known and target in historical else 'current' if target in known else 'historical' if target in historical else 'unregistered'
            target_state=namespace
        else:
            parsed=urlsplit(target)
            loc=(root/'notebook.html',parsed.fragment) if not parsed.path and not parsed.scheme and not parsed.netloc and parsed.fragment else local_target(target,root)
            if loc and loc[0].resolve()==(root/'notebook.html').resolve() and loc[1]:
                target_ids=sorted(anchors.get(loc[1],[]))
                target_state='indexed_anchor' if target_ids else 'unindexed_anchor' if loc[1] in dom.ids else 'missing_anchor'
            else:target_state='external_or_file'
        key=(aid,kind,target);ordinal[key]+=1
        identifier=sha(json.dumps([*key,ordinal[key]],ensure_ascii=False))[:24]
        context=(plain(text[article['start']:pos])[-160:]+' '+plain(text[pos:article['end']])[:420]).strip()
        row={'id':identifier,'kind':kind,'article':aid,'line':bisect_right(dom.offsets,pos),'article_offset':pos-article['start'],
             'heading':None if heading is None else {'anchor':heading['anchor'],'title':plain(text[heading['start']:heading['end']]),'line':bisect_right(dom.offsets,heading['start'])},
             'target':target,'text':plain(''.join(event['text_parts'])) if kind=='hyperlink' else event['text'],
             'source_ownership':ownership,'source_claim_candidates':owners,
             'enclosing_claim_candidates':sorted({i['id'] for i in contained}),
             'article_claim_candidates':sorted(article_claims[aid]),'target_claim_candidates':target_ids,
             'target_status':target_state,'context':context,'accepted_relationship':False}
        out.append(row);by_article[aid].append(identifier);counts[kind]+=1
    artrows=[]
    for a in articles:
        fragment=text[a['start']:a['end']]
        artrows.append({'id':a['anchor'],'line':bisect_right(dom.offsets,a['start']),'sha256':sha(fragment),
                        'claim_candidates':sorted(article_claims[a['anchor']]),'citation_ids':by_article[a['anchor']],
                        'citation_count':len(by_article[a['anchor']])})
    return {'schema_version':1,'method':'full-record-html-citations-v1','notebook_sha256':sha(text),
            'registry_sha256':sha(json.dumps(data,sort_keys=True,ensure_ascii=False)),
            'counts':{'articles':len(artrows),'articles_with_citations':sum(bool(a['citation_ids']) for a in artrows),
                      'hyperlinks':counts['hyperlink'],'explicit_claim_labels':counts['explicit_claim_label'],
                      'citation_occurrences':len(out),'source_ownership':dict(Counter(r['source_ownership'] for r in out)),
                      'target_status':dict(Counter(r['target_status'] for r in out))},
            'articles':artrows,'citations':out,'record_occurrences_outside_articles':record_outside,
            'unresolved_index_anchors':unresolved,
            'scope':'Every href-bearing HTML anchor and every recognized claim-label token in visible research-article text nodes is retained, including unindexed articles. HTML attributes, comments, script/style contents and living sections are excluded. Links and labels can overlap as distinct occurrence kinds. Owning headings include unanchored siblings; source owners are candidates, never inferred proof use. Implicit prose citations or labels split across text nodes are outside token discovery. No edges are created.'}


def select(report, *, article=None, claim=None, ownership=None, kind=None):
    return [r for r in report['citations'] if (article is None or r['article']==article)
            and (claim is None or claim in r['source_claim_candidates'] or claim in r['target_claim_candidates'])
            and (ownership is None or r['source_ownership']==ownership) and (kind is None or r['kind']==kind)]

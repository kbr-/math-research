"""Mechanical new-entry claim inventory checks; not a detector of unlabelled mathematics."""
import html
from html.parser import HTMLParser
import re
from claim_registry import references,local_target


class Entries(HTMLParser):
    def __init__(self,text):
        super().__init__(convert_charrefs=True)
        self.entries=[];self.active=None;self.in_record=False
        self.feed(text);self.close()
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='section' and attrs.get('id')=='research-record':self.in_record=True
        if not self.in_record:return
        if tag=='article':
            if self.active is not None:raise ValueError('Nested research article')
            if not attrs.get('id'):raise ValueError('Research article needs a stable ID')
            self.active={'id':attrs['id'],'attrs':attrs,'anchors':{attrs['id']},'code':[],'text':[],'in_code':0}
        if self.active is not None:
            if attrs.get('id'):self.active['anchors'].add(attrs['id'])
            if tag=='code':self.active['in_code']+=1
    def handle_data(self,text):
        if self.active is not None:
            self.active['text'].append(text)
            if self.active['in_code']:self.active['code'].append(text)
    def handle_endtag(self,tag):
        if self.active is not None and tag=='code':self.active['in_code']=max(0,self.active['in_code']-1)
        if tag=='article' and self.active is not None:self.entries.append(self.active);self.active=None
    def close(self):
        super().close()
        if self.active is not None:raise ValueError('Unclosed research article')
        ids=[e['id'] for e in self.entries]
        if len(ids)!=len(set(ids)):raise ValueError('Duplicate research article ID')


def article_ids(text):
    """The IDs Entries(text) would list, without parsing article bodies: earlier notebook versions are
    read only to tell which entries are new, and a full parse of each cost about 0.4 s per 8 MB."""
    return {html.unescape(m.group(2)) for m in _articles(text)[0]}


ARTICLE_START=re.compile(r'<article\b[^>]*?(?<![\w-])id=(["\'])(.*?)\1')


def _articles(text):
    """Start tags of the articles Entries would list (from the research-record section on); comments
    are blanked to spaces so that match offsets are offsets in text."""
    blanked=re.sub(r'<!--.*?-->',lambda m:' '*len(m.group()),text,flags=re.S)
    start=re.search(r'<section\b[^>]*(?<![\w-])id=(["\'])research-record\1',blanked)
    if not start:return [],0,blanked
    return (list(ARTICLE_START.finditer(blanked,start.start())),
            len(re.findall(r'<article\b',blanked[start.start():])),blanked)


def new_entries(previous,current):
    """Entries(current).entries restricted to articles absent from previous, parsing only those articles.
    Duplicate IDs anywhere in the record still fail closed."""
    found,tags,blanked=_articles(current)
    if tags!=len(found):raise ValueError('Research article needs a stable ID')
    ids=[html.unescape(m.group(2)) for m in found]
    if len(ids)!=len(set(ids)):raise ValueError('Duplicate research article ID')
    before=article_ids(previous)
    pieces=[]
    for m,key in zip(found,ids):
        if key in before:continue
        end=blanked.find('</article>',m.start())
        pieces.append(current[m.start():] if end<0 else current[m.start():end+len('</article>')])
    return Entries('<section id="research-record">'+''.join(pieces)+'</section>').entries if pieces else []


def check_entries(previous,current,data,root,grandfathered=(),notebook_path=None):
    notebook_path = notebook_path or root/'notebook.html'
    # An unchanged notebook has no new entries; a callable grandfathered set is read only when needed.
    entries=[] if previous==current else new_entries(previous,current)
    if entries and callable(grandfathered):grandfathered=grandfathered()
    entries=[e for e in entries if e['id'] not in set(grandfathered)]
    claims={c['id']:c for c in data['claims']}
    historical=root/'php_codex_handoff/manuscript/CLAIM_INDEX.md'
    historical_ids=set(re.findall(r'`([^`\s]+:[^`\s]+)`',historical.read_text())) if historical.exists() else set()
    prefixes={key.split(':',1)[0] for key in claims|dict.fromkeys(historical_ids)}|{'lem','thm','prop','cor','def','ex','obs','conj','check','audit','local','third-party'}
    pattern=r'(?<![\w-])(?:'+ '|'.join(re.escape(p) for p in sorted(prefixes))+r'):[\w][\w.-]*'
    errors=[];rows=[]
    # Resolve every claim's source links once, not once per new entry.
    anchors={}
    if entries:
        from notebooks import catalogue
        items=catalogue(root);here=notebook_path.resolve()
        # Many claims cite the same notebook. Resolve each path once in this snapshot,
        # keeping the cache local so subsequent checks observe changed links.
        resolved_paths={notebook_path:here}
        for key,claim in claims.items():
            for ref in references(claim):
                target=local_target(ref['target'],root,items)
                if target:
                    path,anchor=target
                    if path not in resolved_paths:resolved_paths[path]=path.resolve()
                    if resolved_paths[path]==here:anchors.setdefault(key,set()).add(anchor)
    for entry in entries:
        label=entry['id'];attrs=entry['attrs'];raw=attrs.get('data-claims','').strip()
        declared=set(raw.split()) if raw and raw!='none' else set()
        if not raw:errors.append(f'{label}: declare data-claims="ID ..." or "none" with data-claim-note')
        if raw=='none' and not attrs.get('data-claim-note','').strip():
            errors.append(f'{label}: no-claim declaration needs a specific data-claim-note')
        if 'none' in declared:errors.append(f'{label}: none cannot be mixed with claim IDs')
        missing=declared-claims.keys()
        for key in sorted(missing):errors.append(f'{label}: declared claim is not registered: {key}')
        # Check code labels and backtick labels, not URLs or arbitrary prose tokens.
        quoted=' '.join(entry['code'])+' '+' '.join(re.findall(r'`([^`]+)`',''.join(entry['text'])))
        for key in sorted(set(re.findall(pattern,quoted))-claims.keys()-historical_ids):
            errors.append(f'{label}: explicit claim label is unregistered: {key}')
        linked={key for key,found in anchors.items() if found&set(entry['anchors'])}
        for key in sorted(linked-declared):errors.append(f'{label}: source-linked claim missing from inventory: {key}')
        for key in sorted(declared-linked-missing):errors.append(f'{label}: declared claim needs a source link to this entry: {key}')
        rows.append({'entry':label,'declared':sorted(declared),'source_linked':sorted(linked),'no_claim_reason':attrs.get('data-claim-note')})
    return {'passed':not errors,'errors':errors,'entries':rows,
            'scope':'New-entry declarations, explicit labels and source links are checked. Unlabelled mathematical novelty and truthful no-claim declarations still need editorial review.'}

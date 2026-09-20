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


def check_entries(previous,current,data,root,grandfathered=(),notebook_path=None):
    notebook_path = notebook_path or root/'notebook.html'
    before={e['id'] for e in Entries(previous).entries}|set(grandfathered)
    entries=[e for e in Entries(current).entries if e['id'] not in before]
    claims={c['id']:c for c in data['claims']}
    historical=root/'php_codex_handoff/manuscript/CLAIM_INDEX.md'
    historical_ids=set(re.findall(r'`([^`\s]+:[^`\s]+)`',historical.read_text())) if historical.exists() else set()
    prefixes={key.split(':',1)[0] for key in claims|dict.fromkeys(historical_ids)}|{'lem','thm','prop','cor','def','ex','obs','conj','check','audit','local','third-party'}
    pattern=r'(?<![\w-])(?:'+ '|'.join(re.escape(p) for p in sorted(prefixes))+r'):[\w][\w.-]*'
    errors=[];rows=[]
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
        linked=set()
        for key,claim in claims.items():
            for ref in references(claim):
                target=local_target(ref['target'],root)
                if target and target[0].resolve()==notebook_path.resolve() and target[1] in entry['anchors']:
                    linked.add(key);break
        for key in sorted(linked-declared):errors.append(f'{label}: source-linked claim missing from inventory: {key}')
        for key in sorted(declared-linked-missing):errors.append(f'{label}: declared claim needs a source link to this entry: {key}')
        rows.append({'entry':label,'declared':sorted(declared),'source_linked':sorted(linked),'no_claim_reason':attrs.get('data-claim-note')})
    return {'passed':not errors,'errors':errors,'entries':rows,
            'scope':'New-entry declarations, explicit labels and source links are checked. Unlabelled mathematical novelty and truthful no-claim declarations still need editorial review.'}

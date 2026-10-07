"""Changed-claim completeness gate, separate from the historical curation backlog."""
import re
import subprocess
from collections import defaultdict
from pathlib import Path
from claim_registry import ROOT, parse_json, TEXT_FIELDS
from claim_reviews import FIELDS, Evidence, coverage
from claim_registration import check_entries, article_ids

# Preserve append-only historical entries predating the inventory requirement.
ENTRY_INVENTORY_BASE = "552e562f5253700258438272da90a9f4a31d00f6"


def baseline(revision='HEAD', root=ROOT):
    if revision=='EMPTY':return 'EMPTY', {'claims':[],'relationships':[],'topic_definitions':[]}
    commit=subprocess.check_output(['git','rev-parse',revision+'^{commit}'],cwd=root,text=True).strip()
    path='research/claims/index.json'
    listed=subprocess.check_output(['git','ls-tree','--name-only',commit,'--',path],cwd=root,text=True).strip()
    if not listed:return commit, {'claims':[],'relationships':[],'topic_definitions':[]}
    return commit,parse_json(subprocess.check_output(['git','show',commit+':'+path],cwd=root,text=True))


class UnchangedArticles:
    """Whether a cited anchor lies in a notebook article byte-identical to its text at the base revision. Appending
    one entry changes the notebook file, and re-hashing every article cited from it found nothing new while it took
    about a second (3 October 2026): only articles whose text changed since the base can change a hash in this diff.
    An anchor inside an article (a heading or claim anchor) excerpts no further than that article."""

    def __init__(self, root, base, evidence=None, source_texts=None):
        self.root, self.base, self.texts = root, base, {}
        self.evidence = evidence
        self.source_texts = source_texts if source_texts is not None else {}

    def __call__(self, path, anchor):
        if path.suffix != '.html' or not anchor:
            return False
        if path not in self.texts:
            shown = subprocess.run(['git', 'show', f'{self.base}:{path.relative_to(self.root).as_posix()}'],
                                   cwd=self.root, capture_output=True, text=True)
            previous = shown.stdout if shown.returncode == 0 else ''
            then = {m.group(1): m.group(0) for m in Evidence.ARTICLE.finditer(previous)}
            if self.evidence is None:
                current = path.read_text()
                now = {m.group(1): m.group(0) for m in Evidence.ARTICLE.finditer(current)}
            else:
                # Populate the same parsed snapshot later used for changed evidence hashes.
                self.evidence.article(path, anchor)
                current, now = self.evidence.sources[path], self.evidence.articles[path]
            self.source_texts[path] = previous, current
            inner = {name: ident for ident, text in now.items() for name in re.findall(r'\bid="([^"]+)"', text)}
            self.texts[path] = then, now, inner
        then, now, inner = self.texts[path]
        ident = inner.get(anchor)
        return ident is not None and ident in then and then[ident] == now[ident]


def maintenance(before, after, root=ROOT, changed_paths=(), base=None, source_texts=None):
    old={c['id']:c for c in before['claims']};new={c['id']:c for c in after['claims']}
    required=defaultdict(set);reasons=defaultdict(list);errors=[]
    def need(label,fields,reason):
        if label in new:required[label].update(fields);reasons[label].append(reason)
    for label in old.keys()-new.keys():errors.append(f'{label}: stable claim removed; retain its historical record')
    for label,claim in new.items():
        if label not in old:
            need(label,FIELDS,'new claim');continue
        prior=old[label]
        if any(prior[k]!=claim[k] for k in TEXT_FIELDS):
            need(label,FIELDS,'statement, assessment or source record changed')
        for field in FIELDS:
            if field!='relationships' and prior[field]!=claim[field]:need(label,[field],field+' changed')
            if prior.get('reviews',{}).get(field)!=claim.get('reviews',{}).get(field):need(label,[field],field+' review changed')
    old_topics={t['id']:t for t in before.get('topic_definitions',[])}
    new_topics={t['id']:t for t in after.get('topic_definitions',[])}
    changed_topics={key for key in old_topics.keys()|new_topics.keys() if old_topics.get(key)!=new_topics.get(key)}
    for label,c in new.items():
        if changed_topics.intersection(c['topics']):need(label,['topics'],'topic definition changed')
    old_edges={e['id']:e for e in before['relationships']};new_edges={e['id']:e for e in after['relationships']}
    changed_edges=[]
    for key in sorted(old_edges.keys()|new_edges.keys()):
        if old_edges.get(key)==new_edges.get(key):continue
        changed_edges.append(key)
        for edge in (old_edges.get(key),new_edges.get(key)):
            if not edge:continue
            for endpoint in ('source','target'):
                e=edge[endpoint]
                if e['namespace']=='current':need(e['id'],['relationships'],'incident relationship changed')
        edge=new_edges.get(key)
        if edge:
            if not edge['evidence'] or not edge.get('review'):
                errors.append(f'{key}: changed relationship needs evidence and an explicit review note')
            if edge['type'] in ('corrects','supersedes') and edge['target']['namespace']=='current':
                label=edge['target']['id'];need(label,['mathematical_status', 'significance'],'correction/supersession requires status and significance review')
                if label in old and old[label].get('reviews',{}).get('mathematical_status')==new[label].get('reviews',{}).get('mathematical_status'):
                    errors.append(f'{label}: explicitly refresh status review for {key}; no automatic retraction inferred')
                if label in old and old[label].get('reviews',{}).get('significance')==new[label].get('reviews',{}).get('significance'):
                    errors.append(f'{label}: explicitly refresh significance review for {key}')
    evidence=Evidence(root);changed_paths=set(changed_paths)
    unchanged=UnchangedArticles(root,base,evidence,source_texts) if base and base!='EMPTY' else (lambda path,anchor:False)
    # Changed cited sources matter even if someone forgot to edit the index.
    # Corpus-wide negative mapping census changes stay visible in backlog instead.
    for label,claim in new.items():
        for field,review in claim.get('reviews',{}).items():
            for item in review['evidence']:
                target=evidence.local(item['target'])
                if not target or str(target[0].relative_to(root)) not in changed_paths:continue
                if unchanged(*target):continue   # its article is as it was at the base
                try:current=evidence.sha256(item['target'],item.get('normalization'))
                except (OSError,ValueError):current='missing'
                if current!=item['sha256']:need(label,[field],'cited evidence changed')
    # Only the claims under review need their state; the whole backlog is claim-index.py coverage.
    report=coverage(after,root,set(required),evidence)
    rows={(r['id'],r['field']):r for r in report['fields']}
    for label,fields in required.items():
        for field in sorted(fields):
            row=rows[(label,field)];review=new[label].get('reviews',{}).get(field)
            if row['state'] in ('unreviewed','stale'):
                errors.append(f'{label}: {field} is {row["state"]}');continue
            if not review or not review['note'].strip() or not review['evidence']:
                errors.append(f'{label}: {field} needs a reasoned evidence-backed disposition')
            elif row['state']=='pending' and not review['next_action']:
                errors.append(f'{label}: pending {field} needs a specific next action')
            if field=='significance' and row['state']=='reviewed':
                significance=new[label].get('significance') or {}
                if significance.get('category', 'unassessed')=='unassessed':
                    errors.append(f'{label}: classify significance or record a pending question with next action')
    return {'passed':not errors,'errors':errors,
            'required_reviews':[{'id':label,'fields':sorted(fields),'reasons':sorted(set(reasons[label]))}
                                for label,fields in sorted(required.items())],
            'changed_relationships':changed_edges,'coverage':report['counts'],
            'scope':'Changed claims/relationships must have current evidence-backed dispositions. '
                    'Pending questions remain pending; unchanged historical backlog is not excused or blocked.'}


def check_revision(after, revision='HEAD', root=ROOT):
    if revision=='EMPTY':
        commit,before=baseline(revision,root)
        changed=subprocess.check_output(['git','ls-files'],cwd=root,text=True).splitlines()
    else:
        commit=subprocess.check_output(['git','rev-parse',revision+'^{commit}'],cwd=root,text=True).strip()
        changed=subprocess.check_output(['git','diff','--name-only',commit,'--'],cwd=root,text=True).splitlines()
        # An index tracked and identical at the base needs no second parse: `after` is the base's registry.
        # (git diff omits untracked files, so tracking is checked separately.)
        path='research/claims/index.json'
        tracked=subprocess.check_output(['git','ls-tree','--name-only',commit,'--',path],cwd=root,text=True).strip()
        before=after if tracked and path not in changed else baseline(commit,root)[1]
    source_texts={}
    result=maintenance(before,after,root,changed,base=commit,source_texts=source_texts)
    result['base_revision']=commit
    from notebooks import paths
    registrations=[]
    notebooks=[(n,n.relative_to(root).as_posix()) for n in paths(root)]
    at_base=set() if commit=='EMPTY' else set(subprocess.check_output(
        ['git','ls-tree','--name-only',commit,'--',*[r for _,r in notebooks]],cwd=root,text=True).splitlines())
    for notebook,relative in notebooks:
        if relative in at_base and relative not in changed:
            continue   # identical to the base: no new entries to register
        def notebook_at(ref):
            if ref=='EMPTY':return ''
            if ref==commit and notebook in source_texts:return source_texts[notebook][0]
            shown=subprocess.run(['git','show',ref+':'+relative],cwd=root,text=True,capture_output=True)
            return shown.stdout if shown.returncode==0 else ''
        grandfathered=lambda:article_ids(notebook_at(ENTRY_INVENTORY_BASE))
        current=source_texts[notebook][1] if notebook in source_texts else notebook.read_text()
        registration=check_entries(notebook_at(commit),current,after,root,grandfathered,notebook)
        registrations.append(registration)
    result['registration']={'passed':all(r['passed'] for r in registrations),
                            'errors':[e for r in registrations for e in r['errors']],
                            'entries':[e for r in registrations for e in r['entries']]}
    result['errors'].extend(result['registration']['errors'])
    result['passed']=not result['errors']
    return result

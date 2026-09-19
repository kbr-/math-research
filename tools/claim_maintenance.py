"""Changed-claim completeness gate, separate from the historical curation backlog."""
import subprocess
from collections import defaultdict
from pathlib import Path
from claim_registry import ROOT, parse_json, TEXT_FIELDS, local_target
from claim_reviews import FIELDS, coverage
from claim_registration import check_entries, Entries

# Preserve append-only historical entries predating the inventory requirement.
ENTRY_INVENTORY_BASE = "552e562f5253700258438272da90a9f4a31d00f6"


def baseline(revision='HEAD', root=ROOT):
    if revision=='EMPTY':return 'EMPTY', {'claims':[],'relationships':[],'topic_definitions':[]}
    commit=subprocess.check_output(['git','rev-parse',revision+'^{commit}'],cwd=root,text=True).strip()
    path='research/claims/index.json'
    listed=subprocess.check_output(['git','ls-tree','--name-only',commit,'--',path],cwd=root,text=True).strip()
    if not listed:return commit, {'claims':[],'relationships':[],'topic_definitions':[]}
    return commit,parse_json(subprocess.check_output(['git','show',commit+':'+path],cwd=root,text=True))


def maintenance(before, after, root=ROOT, changed_paths=()):
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
                label=edge['target']['id'];need(label,['mathematical_status'],'correction/supersession requires status review')
                if label in old and old[label].get('reviews',{}).get('mathematical_status')==new[label].get('reviews',{}).get('mathematical_status'):
                    errors.append(f'{label}: explicitly refresh status review for {key}; no automatic retraction inferred')
    report=coverage(after,root)
    rows={(r['id'],r['field']):r for r in report['fields']}
    # Changed cited sources matter even if someone forgot to edit the index.
    # Corpus-wide negative mapping census changes stay visible in backlog instead.
    for row in report['fields']:
        if row['state']=='stale':
            for reason in row.get('reasons',[]):
                if not reason.startswith('source changed: '):continue
                target=local_target(reason[len('source changed: '):],root)
                if target and str(target[0].relative_to(root)) in changed_paths:
                    need(row['id'],[row['field']],'cited evidence changed')
    for label,fields in required.items():
        for field in sorted(fields):
            row=rows[(label,field)];review=new[label].get('reviews',{}).get(field)
            if row['state'] in ('unreviewed','stale'):
                errors.append(f'{label}: {field} is {row["state"]}');continue
            if not review or not review['note'].strip() or not review['evidence']:
                errors.append(f'{label}: {field} needs a reasoned evidence-backed disposition')
            elif row['state']=='pending' and not review['next_action']:
                errors.append(f'{label}: pending {field} needs a specific next action')
    return {'passed':not errors,'errors':errors,
            'required_reviews':[{'id':label,'fields':sorted(fields),'reasons':sorted(set(reasons[label]))}
                                for label,fields in sorted(required.items())],
            'changed_relationships':changed_edges,'coverage':report['counts'],
            'scope':'Changed claims/relationships must have current evidence-backed dispositions. '
                    'Pending questions remain pending; unchanged historical backlog is not excused or blocked.'}


def check_revision(after, revision='HEAD', root=ROOT):
    commit,before=baseline(revision,root)
    command=['git','ls-files'] if commit=='EMPTY' else ['git','diff','--name-only',commit,'--']
    changed=subprocess.check_output(command,cwd=root,text=True).splitlines()
    result=maintenance(before,after,root,changed)
    result['base_revision']=commit
    notebook=root/'notebook.html'
    if notebook.exists():
        def notebook_at(ref):
            if ref=='EMPTY':return ''
            shown=subprocess.run(['git','show',ref+':notebook.html'],cwd=root,text=True,capture_output=True)
            return shown.stdout if shown.returncode==0 else ''
        grandfathered={e['id'] for e in Entries(notebook_at(ENTRY_INVENTORY_BASE)).entries}
        registration=check_entries(notebook_at(commit),notebook.read_text(),after,root,grandfathered)
        result['registration']=registration
        result['errors'].extend(registration['errors'])
        result['passed']=not result['errors']
    return result

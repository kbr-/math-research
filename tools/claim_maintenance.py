"""Changed-claim completeness gate, separate from the historical curation backlog."""
import multiprocessing
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


def can_fork():
    """Whether this process may start forked workers: the platform has fork, and the process is not itself a
    daemonic worker (such as a worker of the parallel test runner), which may have no children."""
    return 'fork' in multiprocessing.get_all_start_methods() and not multiprocessing.current_process().daemon


_HASH={}


def _hash(keys):
    """Hashes of one source file's cited evidence, in a forked worker; None where the parent is to fail itself."""
    if 'evidence' not in _HASH:_HASH['evidence']=Evidence(_HASH['root'])   # this worker's own reader
    evidence,out=_HASH['evidence'],[]
    for key in keys:
        try:out.append((key,evidence.sha256(*key)))
        except Exception:out.append((key,None))   # whatever it is, the parent meets it if it asks for the key
    return out


class Hasher:
    """Fills an Evidence cache from forked workers, one batch for each source file.  A worker reads what the
    parent had not parsed at the fork itself, so its hashes are the parent's unless a file changes during the
    run.  It uses the pool it is given, or forks its own at the first batch that is worth it, which the caller
    must allow by having no thread of its own then; a batch of a few keys, a single file, or a process that may
    not fork is left to the parent's own lazy hashing."""
    WORTH=40

    def __init__(self,evidence,root,pool=None,jobs=6):
        self.evidence,self.root,self.jobs,self.pool,self.own=evidence,root,jobs,pool,pool is None

    def fill(self,keys):
        batches=defaultdict(list)
        for key in dict.fromkeys(keys):
            if key in self.evidence.cache:continue
            local=self.evidence.local(key[0])
            if local:batches[local[0]].append(key)
        if len(batches)<2 or sum(map(len,batches.values()))<self.WORTH:return
        if not can_fork():return
        if self.pool is None:
            # Forked here, the workers start with the sources this process has parsed so far.
            _HASH.clear();_HASH.update(root=self.root,evidence=self.evidence)
            self.pool=multiprocessing.get_context('fork').Pool(min(self.jobs,len(batches)))
        ordered=sorted(batches.values(),key=len,reverse=True)   # the largest file first
        for result in self.pool.map(_hash,ordered,chunksize=1):
            for key,value in result:
                if value is not None:self.evidence.cache[key]=value

    def close(self):
        if self.own and self.pool is not None:
            self.pool.close();self.pool.join()


def maintenance(before, after, root=ROOT, changed_paths=(), base=None, source_texts=None, pool=None):
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
    cited=[]
    for label,claim in new.items():
        for field,review in claim.get('reviews',{}).items():
            for item in review['evidence']:
                target=evidence.local(item['target'])
                if not target or str(target[0].relative_to(root)) not in changed_paths:continue
                if unchanged(*target):continue   # its article is as it was at the base
                cited.append((label,field,item))
    # Hashes of different source files are independent, so they are computed in forked workers, one batch for
    # each file, and put into the parent's cache: first those of changed files, then those of the claims
    # found to need review.
    hasher=Hasher(evidence,root,pool)
    try:
        hasher.fill((item['target'],item.get('normalization')) for _,_,item in cited)
        for label,field,item in cited:
            try:current=evidence.sha256(item['target'],item.get('normalization'))
            except (OSError,ValueError):current='missing'
            if current!=item['sha256']:need(label,[field],'cited evidence changed')
        hasher.fill((item['target'],item.get('normalization')) for label in required
                    for review in new[label].get('reviews',{}).values() for item in review['evidence'])
    finally:
        hasher.close()
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


_REGISTER={}


def _register(index):
    """One notebook's registration check, in a forked worker: the same call as the sequential path below."""
    notebook,relative=_REGISTER['todo'][index]
    commit,root=_REGISTER['commit'],_REGISTER['root']
    def notebook_at(ref):
        if ref=='EMPTY':return ''
        shown=subprocess.run(['git','show',ref+':'+relative],cwd=root,text=True,capture_output=True)
        return shown.stdout if shown.returncode==0 else ''
    return check_entries(notebook_at(commit),notebook.read_text(),_REGISTER['after'],root,
                         lambda:article_ids(notebook_at(ENTRY_INVENTORY_BASE)),notebook)


def _register_send(index,sender):
    """A registration worker's whole life: send the result, or die and let the parent check that notebook."""
    sender.send(_register(index))
    sender.close()


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
    from notebooks import paths
    registrations=[]
    notebooks=[(n,n.relative_to(root).as_posix()) for n in paths(root)]
    at_base=set() if commit=='EMPTY' else set(subprocess.check_output(
        ['git','ls-tree','--name-only',commit,'--',*[r for _,r in notebooks]],cwd=root,text=True).splitlines())
    # Identical to the base: no new entries to register.
    todo=[(n,r) for n,r in notebooks if not (r in at_base and r not in changed)]
    # Each notebook's registration is independent of the others and of the maintenance check, so with several
    # changed notebooks each runs in a forked process beside it (the processes share the loaded registry).
    # They are plain processes with a pipe each, which give this process no thread, so the maintenance check
    # can fork its hashing workers later.  A worker reads the notebook itself where the sequential path below
    # uses the maintenance check's snapshot: the same text unless the file changes during the run.
    workers=[]
    if len(todo)>1 and can_fork():
        _REGISTER.update(todo=todo,commit=commit,root=root,after=after)
        context=multiprocessing.get_context('fork')
        for index in range(len(todo)):
            receiver,sender=context.Pipe(duplex=False)
            process=context.Process(target=_register_send,args=(index,sender))
            process.start();sender.close()   # a worker that dies ends the wait for its answer
            workers.append((process,receiver))
    try:
        result=maintenance(before,after,root,changed,base=commit,source_texts=source_texts)
        answered=[]
        for process,receiver in workers:
            try:answered.append(receiver.recv())
            except EOFError:answered.append(None)   # died without an answer: checked below, in this process
    except BaseException:
        for process,_ in workers:process.terminate()
        raise
    finally:
        for process,_ in workers:process.join()
    if workers:
        registrations=[r for r in answered if r is not None]
        todo=[item for item,r in zip(todo,answered) if r is None]
    result['base_revision']=commit
    for notebook,relative in todo:
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

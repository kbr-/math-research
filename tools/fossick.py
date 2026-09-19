#!/usr/bin/env python3
"""Incremental, human-reviewed significance screening; selection never advances coverage."""
import argparse
from bisect import bisect_right
import copy
import fcntl
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

from claim_registry import load as load_claims, local_target, references
from claim_reviews import Evidence, digest
from claim_evidence import normalize_evidence, ARTICLE_NORMALIZATION
from claim_attention import atomic, load as load_attention, latest as latest_attention
from notebook_context import excerpt

ROOT = Path(__file__).resolve().parents[1]
STATE = 'research/notes/FOSSICK_STATE.json'
DISPOSITIONS = ('no_candidate', 'candidate_linked', 'already_assessed')


def read_state(root):
    path = root / STATE
    if not path.exists():
        return dict(version=1, scan=None, ended_at=None, ledger={}, active=None, receipts={})
    s = json.loads(path.read_text())
    if s.get('version') != 1 or not isinstance(s.get('ledger'), dict):
        raise ValueError('Unsupported or malformed Fossick state')
    return s


def save_state(root, state):
    atomic(root / STATE, json.dumps(state, ensure_ascii=False, indent=2) + '\n')


def revision(root):
    return subprocess.check_output(['git', 'rev-parse', 'HEAD^{commit}'], cwd=root, text=True).strip()


def inventory(root):
    data = load_claims(root / 'research/claims/index.json')
    source = (root / 'notebook.html').read_text()
    # Repeated bounded batches need not reparse unchanged evidence. The cache is
    # disposable; its key covers the full content of every referenced local file.
    paths = {root/'notebook.html', root/'research/claims/index.json', Path(__file__),
             Path(__file__).with_name('claim_evidence.py'), Path(__file__).with_name('claim_registry.py')}
    for c in data['claims']:
        for review in c.get('reviews', {}).values():
            for item in review.get('evidence', []):
                target = local_target(item['target'], root)
                if target:
                    paths.add(target[0])
    hashes=[]
    for path in sorted(paths):
        h=hashlib.sha256()
        with path.open('rb') as f:
            for chunk in iter(lambda:f.read(1024*1024), b''):
                h.update(chunk)
        hashes.append((str(path), h.hexdigest()))
    key=digest(hashes)
    cache=root/'research/logs/fossick-inventory.json'
    if cache.exists():
        cached=json.loads(cache.read_text())
        if cached.get('key')==key:
            return data,cached['rows']
    book = excerpt.Notebook(source)
    record = book.anchor('research-record')
    nodes = [n for n in book.nodes if n['tag'] == 'article' and record['start'] <= n['start'] < record['end']]
    starts = [n['start'] for n in nodes]
    owners = {n['anchor']: set() for n in nodes}
    # Source references, not inferred proof dependencies.
    for c in data['claims']:
        for ref in references(c):
            target = local_target(ref['target'], root)
            if target and target[0].resolve() == (root/'notebook.html').resolve() and target[1]:
                try:
                    position = book.anchor(target[1])['start']
                except ValueError:
                    match = re.search(r'\bid=["\']' + re.escape(target[1]) + r'["\']', source)
                    if not match:
                        raise ValueError('Missing claim source anchor: ' + target[1])
                    position = match.start()
                i = bisect_right(starts, position) - 1
                if i >= 0 and position < nodes[i]['end']:
                    owners[nodes[i]['anchor']].add(c['id'])
    claims = {c['id']: c for c in data['claims']}
    edges = {label: [] for label in claims}
    for e in data['relationships']:
        for side in ('source', 'target'):
            if e[side]['namespace'] == 'current':
                edges[e[side]['id']].append(e)
    evidence = Evidence(root)
    rows = []
    for n in nodes:
        raw = source[n['start']:n['end']]
        try:
            normalized = normalize_evidence(raw, ARTICLE_NORMALIZATION)
            normalization = ARTICLE_NORMALIZATION
        except ValueError:
            # Legacy free-form HTML is not silently repaired. Raw bytes remain
            # conservative evidence when no generated decoration is involved.
            if 'data-generated="finish-turn-' in raw or '<!-- TIMING ' in raw:
                raise
            normalized, normalization = raw, 'legacy-raw'
        labels = sorted(owners[n['anchor']])
        current_evidence = {}
        for label in labels:
            c = claims[label]
            for review in c.get('reviews', {}).values():
                for item in review.get('evidence', []):
                    key = (item['target'], item.get('normalization'))
                    current_evidence[str(key)] = evidence.sha256(*key)
        payload = {'source': digest(normalized), 'normalization': normalization,
                   'claims': {label: claims[label] for label in labels},
                   'edges': {label: sorted(edges[label], key=lambda e: e['id']) for label in labels},
                   'evidence': current_evidence}
        title = re.search(r'<h[23][^>]*>([\s\S]*?)</h[23]>', raw)
        status = re.search(r'<p class="entry-meta">([\s\S]*?)</p>', normalized)
        rows.append(dict(id=n['anchor'], fingerprint=digest(payload), source_sha256=payload['source'],
                         normalization=normalization, claims=labels,
                         title=excerpt.visible_text(title.group(1)) if title else n['anchor'],
                         status=excerpt.visible_text(status.group(1)) if status else '',
                         preview=excerpt.visible_text(normalized)[:600]))
    atomic(cache,json.dumps({'key':key,'rows':rows},ensure_ascii=False))
    return data, rows


def work(state, rows):
    ids = [r['id'] for r in rows]
    missing = set(state['ledger']) - set(ids)
    if missing:
        raise ValueError('Previously screened anchors missing on this branch: ' + ', '.join(sorted(missing)[:5]))
    if state['scan']:
        terminal = state['scan']['terminal']
        if terminal not in ids:
            raise ValueError('Pinned terminal anchor missing; do not reset the cursor')
        rows = rows[:ids.index(terminal)+1]
    pending = [r for r in rows if state['ledger'].get(r['id'], {}).get('fingerprint') != r['fingerprint']]
    frontier = None
    for r in rows:
        if r in pending:
            break
        frontier = r['id']
    return pending, frontier


def prepare(root, limit=20):
    if not 1 <= limit <= 100:
        raise ValueError('Batch limit must be between 1 and 100')
    state = read_state(root)
    data, rows = inventory(root)
    head = revision(root)
    if state['scan']:
        ancestor = subprocess.run(['git', 'merge-base', '--is-ancestor', state['scan']['revision'], head], cwd=root)
        if ancestor.returncode:
            raise ValueError('Divergent scan revision; finish/reconcile the recorded branch before continuing')
    pending, frontier = work(state, rows)
    if not state['scan'] or (not pending and not state['active']):
        if rows:
            state['scan'] = {'revision': head, 'terminal': rows[-1]['id']}
        pending, frontier = work(state, rows)
    state['ended_at'] = frontier
    state['last_counts']={'remaining':len(pending),'revisits':sum(r['id'] in state['ledger'] for r in pending)}
    if state['active']:
        current = {r['id']: r for r in pending}
        for row in state['active']['items']:
            if row['id'] not in current or row['fingerprint'] != current[row['id']]['fingerprint']:
                raise ValueError('Active batch sources changed; use refresh to reselect unfinished work')
    elif pending:
        selected = [{'id': r['id'], 'fingerprint': r['fingerprint']} for r in pending[:limit]]
        state['active'] = {'id': digest([state['scan'], selected]), 'items': selected}
    save_state(root, state)
    return batch(state, rows), data


def batch(state, rows):
    by_id = {r['id']: r for r in rows}
    active = state['active']
    items = []
    for r in active['items'] if active else []:
        item = copy.deepcopy(by_id[r['id']])
        item.update(disposition=None, note='', reviews=[], attention=[])
        items.append(item)
    pending, _ = work(state, rows)
    return dict(version=1, batch_id=active['id'] if active else None,
                expected_state=digest(state), scan=state['scan'], ended_at=state['ended_at'],
                remaining=len(pending), revisits=sum(r['id'] in state['ledger'] for r in pending), items=items)


def complete(root, proposal, output):
    state = read_state(root)
    token = digest(proposal)
    if token in state['receipts']:
        result = state['receipts'][token]
        write_report(output, result)
        return result
    if proposal.get('expected_state') != digest(state) or not state['active'] or proposal.get('batch_id') != state['active']['id']:
        raise ValueError('Stale batch/state; read next again without discarding completed work')
    data, rows = inventory(root)
    by_id = {r['id']: r for r in rows}
    claims = {c['id']: c for c in data['claims']}
    attention = latest_attention(load_attention(root))
    ev = Evidence(root)
    active = {r['id']: r for r in state['active']['items']}
    accepted = []
    seen = set()
    for item in proposal['items']:
        label = item['id']
        if label in seen:
            raise ValueError('Duplicate batch article')
        seen.add(label)
        if label not in active or label not in by_id or item['fingerprint'] != active[label]['fingerprint'] or item['fingerprint'] != by_id[label]['fingerprint']:
            raise ValueError('Batch source changed or not selected: ' + label)
        disposition = item.get('disposition')
        if disposition is None:
            continue
        if disposition not in DISPOSITIONS or not item.get('note', '').strip():
            raise ValueError('Each completion needs a disposition and reason')
        reviews = item.get('reviews', [])
        flags = item.get('attention', [])
        if any(c not in by_id[label]['claims'] for c in reviews + flags):
            raise ValueError('Assessment references must be source-linked claims')
        if disposition == 'already_assessed' and (not reviews or set(reviews) != set(by_id[label]['claims'])):
            raise ValueError('Reuse requires reviews of every source-linked claim')
        for c in reviews:
            review = claims[c].get('reviews', {}).get('significance')
            if not review or not review.get('evidence') or not review.get('note'):
                raise ValueError('Missing evidence-backed significance review: ' + c)
            from claim_reviews import claim_digest, field_value
            if review['claim_sha256'] != claim_digest(claims[c]) or review['value_sha256'] != digest(field_value(data, claims[c], 'significance')):
                raise ValueError('Stale significance assessment: ' + c)
            if any(ev.sha256(e['target'], e.get('normalization')) != e['sha256'] for e in review['evidence']):
                raise ValueError('Stale review source: ' + c)
        if disposition == 'candidate_linked' and not flags:
            raise ValueError('Candidate needs a persisted attention reference')
        from claim_attention import candidate, fingerprint
        required = [c for c in by_id[label]['claims'] if candidate(claims[c]) or c in attention]
        if any(c not in flags for c in required):
            raise ValueError('Preserve known candidate attention references: ' + label)
        if any(c not in attention or attention[c]['fingerprint'] != fingerprint(data, claims[c]) for c in flags):
            raise ValueError('Missing/stale attention item; sync or record candidate first')
        state['ledger'][label] = {k: by_id[label][k] for k in ('fingerprint', 'source_sha256', 'normalization')}
        state['ledger'][label].update(disposition=disposition, note=item['note'], reviews=reviews,
                                      attention=flags, revision=revision(root))
        accepted.append(label)
    if not accepted:
        raise ValueError('No screened items supplied; selection is not completion')
    remaining = [r for r in state['active']['items'] if r['id'] not in accepted]
    state['active'] = dict(state['active'], items=remaining) if remaining else None
    pending, state['ended_at'] = work(state, rows)
    state['last_counts']={'remaining':len(pending),'revisits':sum(r['id'] in state['ledger'] for r in pending)}
    result = dict(batch_id=proposal['batch_id'], accepted=accepted, ended_at=state['ended_at'],
                  remaining=len(pending), scan=state['scan'], proposal_sha256=token)
    state['receipts'][token] = result
    # Report first: a failed state write leaves a repeatable completion, never a
    # cursor without its evidence. Reports are immutable at an existing path.
    write_report(output, result)
    save_state(root, state)
    return result


def write_report(path, report):
    text = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
    if path.exists() and path.read_text() != text:
        raise ValueError('Refusing to overwrite a different batch/report')
    atomic(path, text)


def brief(root):
    state = read_state(root)
    if not state['scan']:
        return 'Fossick: not started.\n'
    counts=state.get('last_counts',{})
    return (f'Fossick ended_at: {state["ended_at"] or "none"}; last scan: {counts.get("remaining","unknown")} pending '
            f'({counts.get("revisits","unknown")} revisits); next refreshes source changes and later entries; '
            f'unfinished batch: {state["active"]["id"][:12] if state["active"] else "none"}.\n')


def display(proposal, data, compact=False):
    claims = {c['id']: c for c in data['claims']}
    print(f'ended_at={proposal["ended_at"]}; remaining={proposal["remaining"]}; revisits={proposal["revisits"]}')
    for r in proposal['items']:
        if compact:
            from collections import Counter
            counts=Counter((claims[c].get('significance') or {}).get('category','unassessed') for c in r['claims'])
            print(r['id']+'\t'+r['title']+'\t'+str(dict(counts)))
            if not r['claims']:print('  NO INDEXED CLAIM: '+r['preview'])
            continue
        print(f'\n{r["id"]}\t{r["title"]}\n  {r["status"][:200]}')
        if not r['claims']:
            print('  NO INDEXED CLAIM: ' + r['preview'])
        for label in r['claims']:
            c=claims[label];s=c.get('significance') or {}
            print(f'  {label}\t{s.get("category")}/{s.get("novelty")}')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest='command',required=True)
    n=sub.add_parser('next');n.add_argument('--limit',type=int,default=20);n.add_argument('--out',type=Path,required=True);n.add_argument('--compact',action='store_true')
    c=sub.add_parser('complete');c.add_argument('--batch',type=Path,required=True);c.add_argument('--out',type=Path,required=True)
    sub.add_parser('status');sub.add_parser('refresh')
    args=p.parse_args()
    try:
        # All state writers share a lock; digest checks reject stale readers.
        lock=ROOT/'research/logs/fossick.lock';lock.parent.mkdir(parents=True,exist_ok=True)
        with lock.open('a') as f:
            fcntl.flock(f,fcntl.LOCK_EX)
            if args.command=='next':
                proposal,data=prepare(ROOT,args.limit);write_report(args.out,proposal);display(proposal,data,args.compact)
            elif args.command=='complete':
                result=complete(ROOT,json.loads(args.batch.read_text()),args.out)
                print(f'Completed {len(result["accepted"])} articles; ended_at={result["ended_at"]}; remaining={result["remaining"]}. Report: {args.out}')
            elif args.command=='refresh':
                state=read_state(ROOT);state['active']=None;save_state(ROOT,state)
                print('Unfinished selection cleared; completed ledger preserved. Run next to reselect.')
            else:print(brief(ROOT),end='')
    except (ValueError,OSError,KeyError) as e:p.exit(2,f'fossick: {e}\n')


if __name__=='__main__':main()

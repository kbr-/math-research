"""Small, durable attention history; mathematical assessments stay in the registry."""
import copy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile

STATES = ('pending', 'reviewed', 'actioned', 'dismissed')
HISTORY = 'research/claims/attention.json'
VIEW = 'research/ATTENTION.md'


def fingerprint(data, claim):
    edges = sorted((e for e in data['relationships'] if e['type'] in ('corrects', 'supersedes', 'obstructs')
                    and any(e[k]['namespace'] == 'current' and e[k]['id'] == claim['id']
                            for k in ('source', 'target'))), key=lambda e: e['id'])
    # Review dates alone do not reopen an item; changed evidence/scope does.
    reviews = {k: {f: v.get(f) for f in ('state', 'note', 'next_action', 'evidence')}
               for k, v in claim.get('reviews', {}).items()
               if k in ('significance', 'mathematical_status', 'formalization')}
    payload = {k: claim.get(k) for k in ('id', 'summary', 'assessment', 'record',
               'significance', 'mathematical_status', 'formalization')}
    payload.update(reviews=reviews, corrections=edges)
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def candidate(claim):
    sig = claim.get('significance') or {}
    review = claim.get('reviews', {}).get('significance') or {}
    return (sig.get('publication_status') in ('candidate', 'draft', 'preprint')
            or sig.get('novelty') == 'candidate'
            or (sig.get('category') in ('independent_result', 'general_tool', 'negative_result')
                and sig.get('novelty') == 'unknown')
            or review.get('state') == 'pending')


def headline(claim, decided):
    """Results the user should see first; the rest are queued only because their novelty is unknown.

    Headline: a publication or novelty candidate, an independent or negative result, or an
    item an agent or the user has decided on. Automatically queued reusable tools and
    other pending items form the second group (user, 23 September 2026).
    """
    sig = claim.get('significance') or {}
    return (sig.get('publication_status') in ('candidate', 'draft', 'preprint')
            or sig.get('novelty') == 'candidate'
            or sig.get('category') in ('independent_result', 'negative_result')
            or claim['id'] in decided)


def decided_claims(history):
    return {e['claim'] for e in history['events'] if e['actor'] != 'automatic'}


def pending_groups(data, history):
    """Pending claim IDs split into (headline, automatically queued), each sorted."""
    claims = {c['id']: c for c in data['claims']}
    decided = decided_claims(history)
    pending = sorted(k for k, v in latest(history).items() if v['state'] == 'pending')
    top = [k for k in pending if headline(claims[k], decided)]
    return top, [k for k in pending if k not in top]


def load(root):
    path = root / HISTORY
    if not path.exists():
        return {'version': 1, 'events': []}
    data = json.loads(path.read_text())
    if set(data) != {'version', 'events'} or data['version'] != 1 or not isinstance(data['events'], list):
        raise ValueError('Invalid attention history')
    for row in data['events']:
        if (set(row) != {'claim', 'fingerprint', 'state', 'note', 'actor', 'at'}
                or row['state'] not in STATES
                or any(not isinstance(row[k], str) or not row[k].strip() for k in row)
                or len(row['fingerprint']) != 64):
            raise ValueError('Invalid attention event; preserve history and repair explicitly')
    return data


def latest(history):
    return {e['claim']: e for e in history['events']}


def event(claim, digest, state, note, actor):
    return dict(claim=claim, fingerprint=digest, state=state, note=note, actor=actor,
                at=datetime.now(timezone.utc).isoformat(timespec='seconds'))


def reconcile(data, history):
    """Deterministic selection; no literature searches and no automatic verdicts."""
    result = copy.deepcopy(history)
    previous = latest(history)
    ids = {c['id'] for c in data['claims']}
    if previous.keys() - ids:
        raise ValueError('Attention history references removed claim IDs')
    added = []
    for c in data['claims']:
        old = previous.get(c['id'])
        if not old and not candidate(c):
            continue
        digest = fingerprint(data, c)
        if old and old['fingerprint'] == digest:
            continue
        note = ('Recorded claim, scope, evidence or correction changed; reconsider prior decision.'
                if old else 'Significance metadata requests candidate attention; not a novelty verdict.')
        result['events'].append(event(c['id'], digest, 'pending', note, 'automatic'))
        added.append(c['id'])
    return result, added


def decide(data, history, label, state, note, actor='agent'):
    if state not in STATES or not note.strip() or actor not in ('agent', 'user'):
        raise ValueError('Decision needs a valid state, actor and a nonempty reason')
    claim = next((c for c in data['claims'] if c['id'] == label), None)
    if claim is None:
        raise ValueError('Unknown claim ID')
    result, _ = reconcile(data, history)
    row = event(label, fingerprint(data, claim), state, note.strip(), actor)
    old = latest(result).get(label)
    if old and all(old[k] == row[k] for k in ('fingerprint', 'state', 'note', 'actor')):
        return result
    result['events'].append(row)
    return result


def atomic(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    name = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent, delete=False) as f:
            name = f.name
            f.write(text)
        os.replace(name, path)
    finally:
        if name and Path(name).exists():
            Path(name).unlink()


def overview(data, history):
    from claim_notices import link, links, inline
    claims = {c['id']: c for c in data['claims']}
    lines = ['# Results and questions for attention', '',
             '> Generated by `tools/claim-attention.py`; do not edit. Assessments live in',
             '> `claims/index.json`; decisions and their history live in `claims/attention.json`.', '',
             'Pending means attention requested, not an established novel result. Review states are',
             'workflow decisions, not theorem status or publication approval. See [the workflow](claims/README.md#significance-check-and-attention).', '']
    rows = latest(history)
    top, rest = pending_groups(data, history)
    sections = [('Pending: headline results', top,
                 'Publication or novelty candidates, independent and negative results, and items an '
                 'agent or the user decided on.'),
                ('Pending: automatically queued', rest,
                 'Queued automatically because their novelty is unknown, mostly reusable tools; '
                 'lower priority than the headline results.')]
    sections += [(state.capitalize(), sorted(k for k, v in rows.items() if v['state'] == state), None)
                 for state in STATES if state != 'pending']
    for title, selected, intro in sections:
        if not selected:
            continue
        lines += ['## ' + title, '']
        if intro:
            lines += [intro, '']
        for position, label in enumerate(selected):
            c = claims[label]; e = rows[label]; sig = c.get('significance') or {}
            review = c.get('reviews', {}).get('significance') or {}
            refs = links(c)
            claim_link = link(label, refs[0]['target']) if refs else label
            # Presentation only: derive a short heading without adding or changing
            # mathematical metadata. Preserve acronym case already in the ID.
            heading = label.partition(':')[2] or label
            heading = heading.replace('-', ' ').replace('_', ' ')
            heading = heading[:1].upper() + heading[1:]
            if position:
                lines += ['---', '']
            lines += [f'### {heading}', '', f'**Claim:** {claim_link}', '',
                      inline(c['summary']), '',
                      f'**Significance:** `{sig.get("category", "unassessed")}` · '
                      f'**Novelty:** `{sig.get("novelty", "unknown")}`', '',
                      f'**Why it matters:** {inline(sig.get("rationale") or review.get("note") or "Pending assessment.")}', '',
                      f'**Decision ({e["actor"]}):** {inline(e["note"])}', '']
            if sig.get('next_action') or review.get('next_action'):
                lines += ['**Next:** ' + inline(sig.get('next_action') or review['next_action']), '']
    if not rows:
        lines += ['No candidates flagged.', '']
    return '\n'.join(lines)


def current(data, history):
    """Current state per tracked claim, for agents and workflows such as Fossick.

    Derived from the event history and the registry; never stored separately.
    """
    claims = {c['id']: c for c in data['claims']}
    top, rest = pending_groups(data, history)
    group = {**{k: 'headline' for k in top}, **{k: 'automatic' for k in rest}}
    items = []
    for label, e in sorted(latest(history).items()):
        sig = claims[label].get('significance') or {}
        items.append(dict(claim=label, state=e['state'], group=group.get(label), actor=e['actor'],
                          note=e['note'], at=e['at'], category=sig.get('category'),
                          novelty=sig.get('novelty'), summary=' '.join(claims[label]['summary'].split())))
    return {'version': 1, 'items': items}


def save(root, data, history):
    atomic(root / HISTORY, json.dumps(history, ensure_ascii=False, indent=2) + '\n')
    atomic(root / VIEW, overview(data, history))


def sync(root, data):
    history, added = reconcile(data, load(root))
    save(root, data, history)
    return history, added


def brief(data, history, limit=30):
    """Every headline item, then a count of the automatically queued rest."""
    top, rest = pending_groups(data, history)
    if not top and not rest:
        return 'Significance attention: no pending items.\n'
    claims = {c['id']: c for c in data['claims']}
    lines = [f'Significance attention: {len(top)} headline and {len(rest)} automatically queued '
             'pending items; research/ATTENTION.md has scope and next actions. Tell the user about new '
             'headline items.']
    for label in top[:limit]:
        text = ' '.join(claims[label]['summary'].split())
        lines.append(f'- {label}: {text[:120]}' + ('…' if len(text) > 120 else ''))
    if len(top) > limit:
        lines.append(f'{len(top)-limit} further headline items omitted; tools/claim-attention.py list --all')
    return '\n'.join(lines) + '\n'

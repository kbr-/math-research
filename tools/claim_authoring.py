#!/usr/bin/env python3
"""Prepare source-backed registry proposals; canonical writes are deliberately separate."""
import math
import re
import argparse
from copy import deepcopy
import json
from pathlib import Path

from claim_registry import ROOT, REGISTRY, load, read_json, validate, require, write_json, check_targets
from claim_reviews import FIELDS, Evidence, make_review, digest
from claim_maintenance import maintenance
from result_names import letter_code_labels

REQUIRED = 'REQUIRED: '


def template(identifier, existing=None):
    """An intentionally non-importable questionnaire, never an all-null claim."""
    claim = deepcopy(existing) if existing else {
        'id': identifier, 'summary': REQUIRED + 'precise summary',
        'assessment': REQUIRED + 'status and exact qualifications',
        'record': REQUIRED + 'Markdown link to dated source',
        'mathematical_status': REQUIRED + 'schema status or null with pending review',
        'formalization': REQUIRED + 'status, scope, references, artifacts object',
        'topics': REQUIRED + 'list of existing or supplied topic IDs',
        'significance': REQUIRED + 'assessment object or null with pending review'}
    claim.pop('reviews', None)
    return {'claim': claim, 'dispositions': {field: {
        'state': REQUIRED + 'reviewed, pending or not_applicable',
        'note': REQUIRED + 'field-specific finding or precise unresolved question',
        'targets': [REQUIRED + 'source evidence locator'],
        'next_action': REQUIRED + 'specific action if pending; otherwise null'} for field in FIELDS}}


def questionnaire(data, identifier):
    existing = next((c for c in data['claims'] if c['id'] == identifier), None)
    return {'base_sha256': digest(data),
            'provenance': {'revision': REQUIRED + 'immutable source revision',
                           'date': REQUIRED + 'YYYY-MM-DD', 'reviewer': REQUIRED + 'reviewer'},
            'submissions': [template(identifier, existing)], 'relationships': [], 'topic_definitions': []}


def ensure_answered(value):
    if isinstance(value, str):
        require(not value.startswith(REQUIRED), 'Unanswered authoring questionnaire: ' + value)
    elif isinstance(value, dict):
        for item in value.values():
            ensure_answered(item)
    elif isinstance(value, list):
        for item in value:
            ensure_answered(item)


SIMILAR_AT = 0.4


def _words(text):
    return set(re.findall(r'[a-z]{3,}', text.lower()))


def similar_claims(claims, summary, count=3):
    """Existing claims whose summaries resemble the given one, by cosine similarity of word sets weighted by
    inverse document frequency: [(score, id), ...], highest first.  A new statement was registered twice in one
    notebook within two days because a keyword search missed the first (10 October 2026); this is the search a
    registration cannot skip."""
    sets = [(claim['id'], _words(claim.get('summary', ''))) for claim in claims]
    frequency = {}
    for _, words in sets:
        for word in words:
            frequency[word] = frequency.get(word, 0) + 1
    weight = {word: math.log(1 + len(sets) / seen) ** 2 for word, seen in frequency.items()}
    unseen = math.log(1 + len(sets)) ** 2
    mine = _words(summary)
    size = math.sqrt(sum(weight.get(word, unseen) for word in mine)) or 1.0
    scored = []
    for identifier, words in sets:
        other = math.sqrt(sum(weight[word] for word in words)) or 1.0
        scored.append((sum(weight[word] for word in mine & words) / (size * other), identifier))
    return sorted(scored, reverse=True)[:count]


def prepare(before, request, root=ROOT):
    """Return a validated full proposal without mutating before or writing any files."""
    ensure_answered(request)
    require(set(request) == {'base_sha256', 'provenance', 'submissions', 'relationships', 'topic_definitions'},
            'Unexpected/missing authoring request keys')
    require(request['base_sha256'] == digest(before), 'Registry changed: refresh questionnaire against the current base')
    require(bool(request['submissions']), 'At least one explicit claim submission is required')
    meta = request['provenance']
    require(set(meta) == {'revision', 'date', 'reviewer'}, 'Supply revision, date and reviewer')
    after = deepcopy(before)
    for key in ('relationships', 'topic_definitions'):
        known = {item['id'] for item in after[key]}
        for item in request[key]:
            require(item['id'] not in known, 'Authoring proposals append ' + key + '; existing IDs require a separate reviewed edit')
            after[key].append(deepcopy(item)); known.add(item['id'])
    positions = {claim['id']: i for i, claim in enumerate(after['claims'])}
    submitted = set()
    for submission in request['submissions']:
        require(set(submission) == {'claim', 'dispositions'}, 'Submission requires claim and dispositions only')
        claim = deepcopy(submission['claim'])
        require('reviews' not in claim, 'Supply human dispositions; hashes are generated from actual evidence')
        require(claim['id'] not in submitted, 'Duplicate claim submission')
        submitted.add(claim['id'])
        claim['reviews'] = {}
        if claim['id'] in positions:
            after['claims'][positions[claim['id']]] = claim
        else:
            after['claims'].append(claim)
    validate(after)
    linked = {}
    for item in after['relationships']:
        linked.setdefault(item['source']['id'], set()).add(item['target']['id'])
        linked.setdefault(item['target']['id'], set()).add(item['source']['id'])
    for identifier in sorted(submitted - set(positions)):
        summary = next(claim['summary'] for claim in after['claims'] if claim['id'] == identifier)
        for score, other in similar_claims(before['claims'], summary):
            require(score < SIMILAR_AT or other in linked.get(identifier, ()),
                    f'{identifier} resembles the registered {other} (similarity {score:.2f}): read that record, '
                    'then relate the two in the spec (rediscovers, refines, depends_on or cites) or register '
                    'nothing new')
    evidence = Evidence(root)
    claims = {claim['id']: claim for claim in after['claims']}
    for submission in request['submissions']:
        claim = claims[submission['claim']['id']]
        dispositions = submission['dispositions']
        require(set(dispositions) == set(FIELDS), 'Supply all five explicit field dispositions')
        for field, disposition in dispositions.items():
            require(set(disposition) == {'state', 'note', 'targets', 'next_action'}, 'Unexpected/missing disposition keys')
            require(bool(disposition['note'].strip()) and bool(disposition['targets']),
                    field + ': a reason and source evidence are required')
            require(disposition['state'] != 'pending' or bool(disposition['next_action']),
                    field + ': pending question requires a next action')
            value = claim.get(field)
            if field == 'formalization':
                value = value['status']
            if field != 'relationships' and (value is None or value == []):
                require(disposition['state'] in ('pending', 'not_applicable'),
                        field + ': missing metadata cannot be marked reviewed')
            claim['reviews'][field] = make_review(after, claim, field, disposition['targets'],
                **meta, state=disposition['state'], note=disposition['note'],
                next_action=disposition['next_action'], evidence=evidence)
    validate(after)
    report = maintenance(before, after, root)
    targets = check_targets(after, root)
    require(targets['passed'], 'Broken source targets: ' + json.dumps(targets['errors']))
    report['targets'] = targets
    require(report['passed'], 'Incomplete proposal: ' + '; '.join(report['errors']))
    return after, report


def _existing_dispositions(claim, targets, extra_note=''):
    """Carry an existing claim's reviews over as dispositions.  extra_note is appended to the relationships review
    (a string) or per field (a dict field -> note), e.g. significance for a correction."""
    notes = extra_note if isinstance(extra_note, dict) else {'relationships': extra_note}
    out = {}
    for field in FIELDS:
        review = claim.get('reviews', {}).get(field)
        if review is None:
            out[field] = {'state': 'pending', 'note': 'Unreviewed before this edit.', 'targets': list(targets),
                          'next_action': 'Review this field.'}
            continue
        note = review['note'] + ((' ' + notes[field]) if notes.get(field) else '')
        out[field] = {'state': review['state'], 'note': note,
                      'targets': [e['target'] for e in review.get('evidence', [])] or list(targets),
                      'next_action': review.get('next_action')}
    return out


def _spec_texts(spec):
    """The new prose a spec writes into the registry: claim text, relationship scopes, overrides, refresh notes."""
    for item in spec.get('claims', []):
        for key in ('summary', 'assessment', 'rationale', 'next_action', 'formalization_scope'):
            if isinstance(item.get(key), str):
                yield item[key]
    for relation in spec.get('relationships', []):
        if len(relation) > 3 and isinstance(relation[3], str):
            yield relation[3]
    for fields in spec.get('overrides', {}).values():
        for value in fields.values():
            if isinstance(value, str):
                yield value
    for note in spec.get('refresh', {}).values():
        for value in (note.values() if isinstance(note, dict) else [note]):
            if isinstance(value, str):
                yield value


def build(data, spec, revision):
    """Expand a compact claim spec into a complete authoring request.

    spec keys: source {record, targets, label}, reviewer, date, claims [...], relationships [[src, type, tgt, scope]],
    optional refresh {id: note or {field: note}}, overrides {id: {field: value}}, topics (default for new claims),
    topic_definitions [{id, title, description}] for topics the registry does not define yet.
    A new claim may carry a complete `formalization` object (status, scope, references, artifacts) when it is
    registered already formalized; otherwise it starts as not_started with `formalization_scope`.
    Every existing claim that is an endpoint of a new relationship is refreshed automatically (its relationships
    review gains a note), which is what the maintenance check requires; refresh/overrides add more."""
    require(set(spec) <= {'source', 'reviewer', 'date', 'claims', 'relationships', 'refresh', 'overrides', 'topics',
                          'topic_definitions'},
            'Unexpected claim-spec keys')
    for topic in spec.get('topic_definitions', []):
        require(set(topic) == {'id', 'title', 'description'}, 'A topic definition needs exactly id, title and description')
    coded = sorted({code for text in _spec_texts(spec) for code in letter_code_labels(text)})
    require(not coded, 'Claim text names results by letter codes ' + ', '.join(coded) + ': cite them by '
            'descriptive names (Naming results), e.g. "the first-active substitution lemma", not "Lemma FA"')
    source = spec['source']; targets = source['targets']; label = source.get('label', 'Source entry')
    existing = {c['id']: c for c in data['claims']}
    submissions, new_ids = [], set()
    for item in spec.get('claims', []):
        require(set(item) <= {'id', 'summary', 'assessment', 'status', 'rationale', 'next_action', 'topics', 'category',
                              'novelty', 'formalization_scope', 'formalization', 'notes'},
                'Unexpected claim keys in ' + item.get('id', '?'))
        cid = item['id']; new_ids.add(cid)
        claim = {'id': cid, 'summary': item['summary'], 'assessment': item['assessment'], 'record': source['record'],
                 'mathematical_status': item['status'],
                 'formalization': deepcopy(item['formalization']) if 'formalization' in item else
                 {'status': 'not_started',
                  'scope': item.get('formalization_scope', 'Informal proof or computation; no Lean verification.'),
                  'references': list(targets), 'artifacts': []},
                 'topics': item.get('topics', spec.get('topics')),
                 'significance': {'category': item.get('category', 'route_specific'), 'rationale': item['rationale'],
                                  'novelty': item.get('novelty', 'not_claimed'), 'publication_status': 'not_applicable',
                                  'references': list(targets), 'next_action': item.get('next_action')}}
        require(bool(claim['topics']), cid + ': topics are required (per claim or spec-wide)')
        notes = item.get('notes', {})
        default = {'mathematical_status': 'Status checked against the entry and its verification gate.',
                   'formalization': ('Lean artifacts checked against their verification reports.'
                                     if 'formalization' in item else 'No Lean artifact.'),
                   'topics': 'Topics checked against the entry.',
                   'significance': 'Significance assessed at this checkpoint.', 'relationships': 'New claim; relationships recorded.'}
        submissions.append({'claim': claim, 'dispositions': {f: {'state': 'reviewed', 'note': notes.get(f, default[f]),
                                                                  'targets': list(targets), 'next_action': None} for f in FIELDS}})
    meta = {'revision': revision, 'date': spec['date'], 'reviewer': spec['reviewer']}
    relationships, touched = [], {}
    for src, kind, tgt, scope in spec.get('relationships', []):
        relationships.append({'id': src + '::' + kind + '::' + tgt, 'type': kind,
                              'source': {'namespace': 'current', 'id': src, 'locator': None},
                              'target': {'namespace': 'current', 'id': tgt, 'locator': None}, 'scope': scope,
                              'evidence': list(targets), 'review_status': 'reviewed', 'review': dict(meta, note=scope)})
        for end, other in ((src, tgt), (tgt, src)):
            if end in existing and end not in new_ids:
                touched.setdefault(end, []).append(other)
    refresh = dict(spec.get('refresh', {}))
    for cid, others in touched.items():
        refresh.setdefault(cid, label + ': new relationship with ' + ', '.join(sorted(set(others))) + '.')
    for cid in list(spec.get('overrides', {})):
        refresh.setdefault(cid, '')
    for cid, note in refresh.items():
        require(cid in existing, 'Refresh of unknown claim ' + cid)
        claim = deepcopy(existing[cid]); claim.pop('reviews', None)
        claim.update(spec.get('overrides', {}).get(cid, {}))
        submissions.append({'claim': claim, 'dispositions': _existing_dispositions(existing[cid], targets, note)})
    return {'base_sha256': digest(data), 'provenance': meta, 'submissions': submissions,
            'relationships': relationships, 'topic_definitions': deepcopy(spec.get('topic_definitions', []))}


STATEMENT = re.compile(r'<p><strong>(?:Lemma|Theorem|Corollary|Proposition|Statement|Claim|Conjecture)\b[^<]*'
                       r'</strong>.*?</p>(?:\s*\\\[.*?\\\])?', re.S)
SHOWN = 700     # characters of an entry statement shown beside a summary


def _plain(fragment):
    return ' '.join(re.sub(r'<[^>]+>', ' ', fragment).replace('&lt;', '<').replace('&gt;', '>')
                    .replace('&amp;', '&').split())


def source_notebook(target, root=ROOT):
    """The notebook file and anchor a spec target URL points at: the main notebook, or a side notebook under
    research/branches/NAME/ for a .../branches/NAME/#anchor link."""
    if '#' not in target:
        return None, None
    page, anchor = target.split('#', 1)
    side = re.search(r'/branches/([\w.-]+)/?$', page)
    return (root / 'research/branches' / side.group(1) / 'notebook.html' if side else root / 'notebook.html'), anchor


def statement_drift(spec, spec_path, root=ROOT):
    """Lines that show each new claim's summary beside its source entry's statement paragraphs, and whether the
    entry's notebook changed after the spec was last edited.

    On 16 October 2026 the error cube floor was registered from its pre-review spec: the entry had been
    corrected after review, the spec had not, and the registered summary denied the level-wise floor the
    reviewed entry proves.  Showing the two side by side, and asking for --summaries-checked when the notebook
    is newer than the spec, makes the comparison part of registration."""
    lines, newer = [], False
    targets = spec.get('source', {}).get('targets', [])
    for target in targets:
        path, anchor = source_notebook(target, root)
        if path is None or not path.exists():
            continue
        text = path.read_text(encoding='utf-8')
        start = text.find(f'<article id="{anchor}"')
        if start < 0:
            lines.append(f'Entry #{anchor} is not yet in {path.relative_to(root)}; its statements were not compared.')
            continue
        article = text[start:text.find('</article>', start)]
        statements = [_plain(m.group(0)) for m in STATEMENT.finditer(article)]
        if spec_path is not None and path.stat().st_mtime > Path(spec_path).stat().st_mtime:
            newer = True
        for item in spec.get('claims', []):
            lines.append(f'{item.get("id")}: registered summary: {item.get("summary", "")[:SHOWN]}')
            for statement in statements or ['(no Lemma, Theorem, Corollary, Proposition or Statement paragraph)']:
                lines.append(f'  entry #{anchor}: {statement[:SHOWN]}' + (' …' if len(statement) > SHOWN else ''))
    return lines, newer


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--registry', type=Path, default=REGISTRY)
    sub = parser.add_subparsers(dest='mode', required=True)
    form = sub.add_parser('template', help='Write an intentionally incomplete questionnaire')
    form.add_argument('claim')
    form.add_argument('--out', type=Path, required=True)
    proposal = sub.add_parser('prepare', help='Validate completed answers and emit a full proposal')
    proposal.add_argument('--request', type=Path, required=True)
    proposal.add_argument('--out', type=Path, required=True)
    proposal.add_argument('--report', type=Path, required=True)
    spec = sub.add_parser('build', help='Expand a compact claim spec into a request; optionally prepare it too')
    spec.add_argument('--spec', type=Path, required=True)
    spec.add_argument('--out', type=Path, required=True, help='the complete authoring request')
    spec.add_argument('--revision', help='source revision (default: git HEAD)')
    spec.add_argument('--proposal', type=Path, help='also run prepare and write the proposed registry here')
    spec.add_argument('--report', type=Path, help='prepare report (required with --proposal)')
    spec.add_argument('--summaries-checked', action='store_true',
                      help='the summaries were compared with the entry statements printed beside them')
    args = parser.parse_args()
    destinations = [args.out] + ([args.report] if args.mode == 'prepare' else [])
    if args.mode == 'build' and args.proposal:
        require(args.report is not None, '--proposal needs --report')
        destinations += [args.proposal, args.report]
    require(len({p.resolve() for p in destinations}) == len(destinations), 'Output paths must differ')
    for path in destinations:
        require(path.resolve() != args.registry.resolve(), 'Proposal must not overwrite canonical input')
        require(not path.exists(), 'Refusing to overwrite existing output: ' + str(path))
    data = load(args.registry)
    if args.mode == 'template':
        write_json(args.out, questionnaire(data, args.claim))
    elif args.mode == 'build':
        import subprocess
        revision = args.revision or subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        compact = read_json(args.spec)
        lines, newer = statement_drift(compact, args.spec)
        print('\n'.join(lines))
        require(not (newer and args.proposal and not args.summaries_checked),
                'The source notebook changed after the spec was last edited: compare each summary above with the '
                'entry statements beside it, correct the spec if they differ, then rerun with --summaries-checked')
        request = build(data, compact, revision)
        write_json(args.out, request)
        if args.proposal:
            proposed, report = prepare(data, request)
            write_json(args.proposal, proposed); write_json(args.report, report)
            print('Saved ' + str(args.proposal) + ' (validated proposal); copy it over the registry, then render.')
    else:
        proposed, report = prepare(data, read_json(args.request))
        write_json(args.out, proposed)
        write_json(args.report, report)
    print('Saved ' + str(args.out) + '; canonical registry unchanged.')


if __name__ == '__main__':
    main()

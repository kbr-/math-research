"""Field-level curation provenance and staleness; no automatic mathematical judgments."""
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path

from claim_registry import ROOT, TEXT_FIELDS, local_target, require

FIELDS = ('mathematical_status', 'formalization', 'topics', 'significance', 'relationships')


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def claim_digest(claim):
    return digest({key: claim[key] for key in ('id', *TEXT_FIELDS)})


def field_value(data, claim, field):
    if field == 'relationships':
        return [e for e in data['relationships'] if any(
            e[end]['namespace'] == 'current' and e[end]['id'] == claim['id'] for end in ('source', 'target'))]
    if field == 'topics':
        return [t for t in data.get('topic_definitions', []) if t['id'] in claim['topics']]
    return claim[field]


class Evidence:
    def __init__(self, root=ROOT):
        self.root, self.cache, self.notebooks = root, {}, {}

    def sha256(self, target):
        if target in self.cache:
            return self.cache[target]
        local = local_target(target, self.root)
        if local is None:
            return None
        path, anchor = local
        if path.suffix == '.html' and anchor:
            if path not in self.notebooks:
                spec = importlib.util.spec_from_file_location('notebook_excerpt', ROOT/'tools/notebook-excerpt.py')
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                self.notebooks[path] = module.Notebook(path.read_text())
            content = self.notebooks[path].excerpt(anchor).encode()
        else:
            content = path.read_bytes()
        self.cache[target] = hashlib.sha256(content).hexdigest()
        return self.cache[target]


def make_review(data, claim, field, targets, *, revision, date, note,
                reviewer, state='reviewed', next_action=None, evidence=None):
    require(field in FIELDS, 'Unknown review field')
    evidence = evidence or Evidence()
    return {'state': state, 'revision': revision, 'date': date, 'reviewer': reviewer,
            'note': note, 'next_action': next_action, 'claim_sha256': claim_digest(claim),
            'value_sha256': digest(field_value(data, claim, field)),
            'evidence': [{'target': target, 'sha256': evidence.sha256(target)} for target in targets]}


def coverage(data, root=ROOT):
    evidence = Evidence(root)
    counts = {field: Counter() for field in FIELDS}
    rows = []
    for claim in data['claims']:
        for field in FIELDS:
            review = claim.get('reviews', {}).get(field)
            state = 'unreviewed' if review is None else review['state']
            reasons = []
            if review:
                if claim_digest(claim) != review['claim_sha256']:
                    reasons.append('claim text changed')
                if digest(field_value(data, claim, field)) != review['value_sha256']:
                    reasons.append('field value changed')
                for item in review['evidence']:
                    try:
                        current = evidence.sha256(item['target'])
                    except (OSError, ValueError):
                        current = 'missing'
                    if current != item['sha256']:
                        reasons.append('source changed: ' + item['target'])
                if reasons:
                    state = 'stale'
            counts[field][state] += 1
            rows.append({'id': claim['id'], 'field': field, 'state': state,
                         'topics': claim['topics'], 'reasons': reasons,
                         'next_action': review['next_action'] if review else 'Review source and populate this field.'})
    topic_ids = {t for c in data['claims'] for t in (c['topics'] or ['unclassified'])}
    by_topic = {}
    for topic in sorted(topic_ids):
        subset = [r for r in rows if topic in (r['topics'] or ['unclassified'])]
        by_topic[topic] = {'claims': len({r['id'] for r in subset}),
                          'counts': {field: dict(Counter(r['state'] for r in subset if r['field'] == field))
                                     for field in FIELDS}}
    return {'schema_version': data['schema_version'], 'claims': len(data['claims']),
            'counts': {field: dict(values) for field, values in counts.items()},
            'by_topic': by_topic, 'fields': rows}

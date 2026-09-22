"""Field-level curation provenance and staleness; no automatic mathematical judgments."""
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import re

from claim_registry import ROOT, TEXT_FIELDS, local_target, require
from claim_evidence import ARTICLE_NORMALIZATION, FRAGMENT_NORMALIZATION, normalize_evidence

FIELDS = ('mathematical_status', 'formalization', 'topics', 'significance', 'relationships')


def verified_declarations(text):
    """Names with an actual standard-axiom report, not merely echoed in a header."""
    if re.search(r'^\s*(?:error:|FAIL:)',text,re.M):
        return set()
    result=set()
    for name,axioms in re.findall(r"'([^'\n]+)' depends on axioms:\s*\[([^\]]*)\]",text):
        used={a.strip() for a in axioms.split(',') if a.strip()}
        if not used <= {'propext','Classical.choice','Quot.sound'}:
            return set()
        result.add(name)
    result.update(re.findall(r"'([^'\n]+)' does not depend on any axioms",text))
    return result


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def claim_digest(claim):
    return digest({key: claim[key] for key in ('id', *TEXT_FIELDS)})


def incident_edges(data):
    """Each current claim's incident relationships, in registry order, each edge once."""
    result = {}
    for e in data['relationships']:
        for label in {e[end]['id'] for end in ('source', 'target') if e[end]['namespace'] == 'current'}:
            result.setdefault(label, []).append(e)
    return result


def field_value(data, claim, field, edges=None):
    if field == 'relationships':
        if edges is not None:
            return edges.get(claim['id'], [])
        return [e for e in data['relationships'] if any(
            e[end]['namespace'] == 'current' and e[end]['id'] == claim['id'] for end in ('source', 'target'))]
    if field == 'topics':
        return [t for t in data.get('topic_definitions', []) if t['id'] in claim['topics']]
    return claim[field]


class Evidence:
    def __init__(self, root=ROOT):
        self.root, self.cache, self.notebooks = root, {}, {}

    def sha256(self, target, normalization=None):
        key = (target, normalization)
        if key in self.cache:
            return self.cache[key]
        local = local_target(target, self.root)
        if local is None:
            if normalization is not None:
                raise ValueError('Normalized evidence requires a local anchored HTML source')
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
        if normalization is not None:
            if not (path.suffix == '.html' and anchor):
                raise ValueError('Article normalization requires an anchored HTML target')
            content = normalize_evidence(content.decode(), normalization).encode()
        self.cache[key] = hashlib.sha256(content).hexdigest()
        return self.cache[key]

    def snapshot(self, target):
        normalization = None
        local = local_target(target, self.root)
        if local is not None:
            path, anchor = local
            if path.suffix == '.html' and anchor:
                self.sha256(target)  # Load and validate the raw excerpt first.
                excerpt = self.notebooks[path].excerpt(anchor)
                # Legacy sources need no decoration normalization. In particular,
                # do not parse their historical free-form HTML more strictly than
                # the existing excerpt reader just to refresh a metadata review.
                generated = re.search(
                    r'<!-- TIMING [A-Za-z0-9_.-]+ -->|'
                    r'<(?:div|span)\b[^>]*\bdata-generated=[\"\']'
                    r'finish-turn-(?:producer|timing)-v1[\"\']', excerpt)
                if generated:
                    normalization = (ARTICLE_NORMALIZATION
                                     if self.notebooks[path].anchor(anchor)['tag'] == 'article'
                                     else FRAGMENT_NORMALIZATION)
        item = {'target': target, 'sha256': self.sha256(target, normalization)}
        if normalization is not None:
            item['normalization'] = normalization
        return item

    def formalization_inventory(self):
        key='__formalization_inventory__'
        if key not in self.cache:
            rows=[]
            for name in ('claims','third-party-claims'):
                for path in sorted((self.root/'formalization'/name).rglob('*.lean')):
                    rows.append((str(path.relative_to(self.root)),hashlib.sha256(path.read_bytes()).hexdigest()))
            self.cache[key]=digest(rows)
        return self.cache[key]


def make_review(data, claim, field, targets, *, revision, date, note,
                reviewer, state='reviewed', next_action=None, evidence=None):
    require(field in FIELDS, 'Unknown review field')
    evidence = evidence or Evidence()
    review={'state': state, 'revision': revision, 'date': date, 'reviewer': reviewer,
            'note': note, 'next_action': next_action, 'claim_sha256': claim_digest(claim),
            'value_sha256': digest(field_value(data, claim, field)),
            'evidence': [evidence.snapshot(target) for target in targets]}
    if field=='formalization' and claim['formalization']['status']=='no_record':
        review['inventory_sha256']=evidence.formalization_inventory()
    return review


def coverage(data, root=ROOT):
    evidence = Evidence(root)
    edges = incident_edges(data)
    counts = {field: Counter() for field in FIELDS}
    rows = []
    for claim in data['claims']:
        for field in FIELDS:
            review = claim.get('reviews', {}).get(field)
            state = 'unreviewed' if review is None else review['state']
            reasons = []
            if review:
                if review.get('inventory_sha256') and review['inventory_sha256']!=evidence.formalization_inventory():
                    reasons.append('formalization inventory changed; rerun mapping audit')
                if claim_digest(claim) != review['claim_sha256']:
                    reasons.append('claim text changed')
                if digest(field_value(data, claim, field, edges)) != review['value_sha256']:
                    reasons.append('field value changed')
                for item in review['evidence']:
                    try:
                        current = evidence.sha256(item['target'], item.get('normalization'))
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

"""Derived notices for the legacy human index; never alter canonical claim text.

Metadata-only and deterministic: rendering does not silently re-audit sources.
"""
import re

START = '<!-- CLAIM-STATUS-NOTICES:START -->\n'
END = '<!-- CLAIM-STATUS-NOTICES:END -->\n\n'
LABELS = {
    'conditional': 'Conditional result — hypotheses remain required',
    'retracted': 'Retracted claim — consult the dated record',
    'refutation': 'Refutation / counterexample result — this does not mean this record is false',
}


def strip_notices(text):
    """Strip exactly one generated region, fail closed on malformed/duplicate markers."""
    starts, ends = text.count(START.rstrip()), text.count(END.strip())
    if not starts and not ends:
        return text
    if starts != 1 or ends != 1:
        raise ValueError('Malformed or duplicated generated claim-notice region')
    left, right = text.find(START), text.find(END)
    if left < 0 or right < left:
        raise ValueError('Unterminated or reversed generated claim-notice region')
    return text[:left] + text[right + len(END):]


def inline(text):
    return re.sub(r'\s+', ' ', text).strip()


def links(claim):
    # Deferred import permits claim_registry to call this helper from render/import.
    from claim_registry import markdown_links
    return markdown_links(claim['record'])


def link(label, target):
    return '[' + label.replace('[', '\\[').replace(']', '\\]') + '](<' + target + '>)'


def render_notices(data):
    """Show scoped correction/supersession notices and special recorded statuses.

Do not infer whole-claim invalidity from a relationship, a name, or legacy prose.
"""
    claims = {c['id']: c for c in data['claims']}
    affected = {}
    for edge in data.get('relationships', []):
        if edge['type'] not in ('corrects', 'supersedes') or edge['target']['namespace'] != 'current':
            continue
        affected.setdefault(edge['target']['id'], []).append(edge)
    lines = []
    for claim in data['claims']:
        status = claim.get('mathematical_status')
        edges = sorted(affected.get(claim['id'], []), key=lambda e: e['id'])
        if status not in LABELS and not edges:
            continue
        records = links(claim)
        owner = link(claim['id'], records[0]['target'])
        label = LABELS.get(status, (status or 'unreviewed').replace('_', ' '))
        lines.append('- **' + owner + '** — recorded status: ' + label + '.')
        status_review = claim.get('reviews', {}).get('mathematical_status')
        if status_review and status_review['state'] != 'reviewed':
            lines.append('  Status review disposition: ' + status_review['state'] + '.')
        if status == 'retracted':
            lines.append('  Dated record: ' + ', '.join(link(r['label'], r['target']) for r in records) + '.')
        for edge in edges:
            source = edge['source']
            source_claim = claims.get(source['id']) if source['namespace'] == 'current' else None
            targets = [r['target'] for r in links(source_claim)] if source_claim else []
            targets += ([source['locator']] if source.get('locator') else []) + edge.get('evidence', [])
            targets = list(dict.fromkeys(targets))
            source_name = link(source['id'], targets[0]) if targets else '`' + source['id'] + '`'
            kind = 'Scoped correction' if edge['type'] == 'corrects' else 'Scoped supersession'
            review = edge.get('review') or {}
            reviewed = edge['review_status']
            if review.get('date'):
                reviewed += '; relationship review ' + review['date']
            lines.append('  ' + kind + ' from ' + source_name + ' (' + reviewed + '): ' + inline(edge['scope']))
            if targets:
                lines.append('  Sources: ' + ', '.join(link('record' if i == 0 else 'evidence ' + str(i), t)
                                                       for i, t in enumerate(targets)) + '.')
    if not lines:
        return ''
    return (START + '### Current status and scoped corrections\n\n'
            'Generated from structured metadata. The table below preserves historical assessment text; '
            'these notices show recorded qualifications. A scoped correction or supersession '
            'does not by itself retract the whole claim. Metadata review dates are not theorem dates, '
            'and rendering does not reverify source evidence.\n\n'
            + '\n'.join(lines) + '\n\n' + END)

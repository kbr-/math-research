#!/usr/bin/env python3
"""The registered claims a draft's claim summaries resemble, before the review.

Registration refuses a new claim that resembles a registered one unless the spec relates the two
(claim_authoring.similar_claims), but registration comes after the entry is drafted and reviewed.  On 11 October
2026 an entry presented as new what a registered finite check already had for three of its six sizes; its
reviewer found the earlier claim.  This tool runs the same search on a compact spec when it is first drafted
and prints, for each of its claims, the registered claims its summary most resembles, with scores, whatever
the spec's relationships say and whatever the threshold: the author reads those records before writing the
entry's claim of novelty.

Usage: claim_resemblance.py SPEC.json [--count N] [--registry PATH]
The spec is the compact form `claim-index.py author build` takes (a "claims" list with "id" and "summary").
It also prints, per claim, the three Working mathematical context sentences of the notebook whose words the
claim most contains. Prints the registry's size, which the work grows with.
"""
import argparse
import math
import re
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from claim_authoring import SIMILAR_AT, similar_claims
from notebook_math import strip_tags


DEFAULT_REGISTRY = ROOT / 'research' / 'claims' / 'index.json'
RUN_LOG = ROOT / 'research' / 'logs' / 'claim-searches.jsonl'


def log_run(idents, path=None):
    """Append this run to the ignored log of record searches, which the finisher reads: an entry of 11 October
    2026 said what its corollary added before the nearest registered claims were read, the tool having been
    run only after the review.  A log that cannot be written is not an error."""
    import time
    try:
        path = path or RUN_LOG
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('a') as handle:
            handle.write(json.dumps({'unix_s': time.time(), 'query': 'claim_resemblance ' + ' '.join(idents)}) + '\n')
    except OSError:
        pass


def resemblances(registered, spec, count=5):
    """[(draft id, [(score, registered id, summary start), ...]), ...] for the spec's claims; a claim already
    registered under an id of the spec, itself or a sibling, is not compared: registration compares the spec only
    with the registry before it, so a run after registering gives the same answer as one before (16 October 2026,
    when a run after registration listed the spec's own claims as the nearest)."""
    summaries = {claim['id']: claim.get('summary', '') for claim in registered}
    own = {claim['id'] for claim in spec.get('claims', [])}
    out = []
    for claim in spec.get('claims', []):
        others = [c for c in registered if c['id'] not in own]
        found = similar_claims(others, claim['summary'], count)
        out.append((claim['id'], [(score, ident, summaries[ident][:160]) for score, ident in found]))
    return out


def record_anchors(claim):
    return tuple(re.findall(r'#([\w-]+)', json.dumps(claim.get('record'))))


def siblings(registered, spec):
    """[(related id, [(sibling id, summary start), ...]), ...]: for every registered claim the spec relates, the
    other claims registered from the same record entry, unless the spec relates or declares them. 16 October 2026:
    a spec related thm:conjunction-quotient-rank and missed thm:punctured-quotient-contraction, registered from the
    same entry, of which its corollary was a consequence; neither the summary resemblance nor the searches found it."""
    by_id = {claim['id']: claim for claim in registered}
    own = {claim['id'] for claim in spec.get('claims', [])}
    related = {edge[2] for edge in spec.get('relationships', []) if len(edge) > 2} | \
              {edge[0] for edge in spec.get('relationships', []) if edge and edge[0] not in own}
    groups = {}
    for claim in registered:
        groups.setdefault(record_anchors(claim), []).append(claim['id'])
    out = []
    for ident in sorted(related):
        if ident not in by_id or not record_anchors(by_id[ident]):
            continue
        rest = [other for other in groups.get(record_anchors(by_id[ident]), [])
                if other != ident and other not in related and other not in own]
        if rest:
            out.append((ident, [(other, by_id[other].get('summary', '')[:160]) for other in rest]))
    return out


QUEUED_AT = 0.4    # measured 11 October 2026 on one notebook's 34 claims and 66 queued items: the known answered
                    # item scores 0.53, and 8 pairs reach 0.4 (34 reach 0.3, 211 reach 0.2)


def queued_matches(nodes, spec, threshold=QUEUED_AT):
    """[(share, draft id, queued id), ...], most alike first: queued items whose wording a draft claim's summary
    shares.  The share is the common content words over those of the queued item, so a long summary does not
    hide a short question.  On 11 October 2026 a queued check waited in the queue long after the lemma that
    answers it was registered by an entry developing another item; a hint to read the item, not a verdict."""
    import lead_queue
    flat = [(n.ident, lead_queue.content_words(n.text)) for top in nodes for n in [top] + top.children]
    out = []
    for claim in spec.get('claims', []):
        words = lead_queue.content_words('): ' + claim.get('summary', '') + ' ' + claim.get('assessment', ''))
        for ident, item in flat:
            if len(item) >= 5:
                share = len(words & item) / len(item)
                if share >= threshold:
                    out.append((round(share, 2), claim['id'], ident))
    return sorted(out, reverse=True)


CONTEXT_SHOWN = 3   # Working-context sentences printed per claim
CONTEXT_STOP = set('with that this from which their have each when only does into than then them they also must over '
                   'under were what where while about after before other these those such'.split())


def _stems(text):
    """Five-letter prefixes of the words of four or more letters, without markup and inline formulas: weights,
    weighted and weight share one."""
    text = re.sub(r'\\\(.*?\\\)', ' ', strip_tags(text))
    return {w[:5] for w in re.findall(r'[a-z]{4,}', text.lower()) if w not in CONTEXT_STOP}


def context_sentences(notebook_text):
    """[(sentence html, first link href or ''), ...] of the notebook's Working mathematical context section."""
    found = re.search(r'<section id="working-context">(.*?)</section>', notebook_text, re.S)
    if not found:
        return []
    body = ' '.join(re.sub(r'<h[1-6][^>]*>.*?</h[1-6]>', ' ', found.group(1), flags=re.S).split())
    out = []
    for sentence in re.split(r'(?<=[.;])\s+(?=[A-Z<])', body):
        link = re.search(r'href="([^"]+)"', sentence)
        out.append((sentence, link.group(1) if link else ''))
    return [(s, link) for s, link in out if len(_stems(s)) >= 2]


def context_matches(sentences, spec, count=CONTEXT_SHOWN):
    """[(draft id, [(share, sentence text, link), ...]), ...]: the living context sentences most of whose words,
    weighted by inverse frequency among the sentences, a draft claim's summary and assessment contain.

    The character error thin-tail spec of 16 October 2026 scored 0.21 or less against every registered claim
    while the Working context already said "Sparse weights give h_w(K) >= h(K)/s", the result its first two parts
    restate; measured on the context of that day, this share ranks that sentence first, at 0.62."""
    frequency = {}
    for sentence, _ in sentences:
        for stem in _stems(sentence):
            frequency[stem] = frequency.get(stem, 0) + 1
    weight = {stem: math.log(1 + len(sentences) / seen) for stem, seen in frequency.items()}
    out = []
    for claim in spec.get('claims', []):
        mine = _stems(claim.get('summary', '') + ' ' + claim.get('assessment', ''))
        scored = []
        for sentence, link in sentences:
            stems = _stems(sentence)
            total = sum(weight[s] for s in stems)
            share = sum(weight[s] for s in stems & mine) / total if total else 0.0
            text = ' '.join(strip_tags(sentence).split())
            scored.append((round(share, 2), text, link))
        out.append((claim['id'], sorted(scored, key=lambda row: -row[0])[:count]))
    return out


# The recorded classes of a notebook's objects, from its claim-classes.json (beside the notebook; none, no
# listing): a class's object words in a new claim's summary, or in a next attempt's text, list the notebook's
# proved claims whose hypothesis takes that class or one containing it.  18 October 2026: a ramp lemma was proved
# by a new chaining while lem:cellwise-lipschitz-split, the record's bound for functions Lipschitz on cells, gave it
# at once; every search had used the draft's own words.  The table is the notebook's, since class words carry one
# goal's meaning ("fixed in advance" means another thing in the pigeonhole notebooks; its reviewer, same day), and
# the listing keeps to the notebook's own claims for the same reason.
CLASS_SHOWN = 8
CLASS_STATUSES = ('working_proof', 'conditional', 'established')
QUANTIFIED = re.compile(r'\b(?:every|each|for all|for any|all)\b', re.I)
# words that open a conclusion; "<=" is not one, a quantifier's range using it ("every j with 1 <= j <= l_1")
RELATION = re.compile(r'\|\s*sum\b|\bhas\b|\bhave\b|\bthere (?:is|are)\b|\bsatisf\w*|\bgives?\b|\bmakes?\b')


def claim_id_pattern(registered):
    """Claim identifiers by the prefixes the registry uses (lem:, thm:, imp:, criterion: ...)."""
    prefixes = sorted({c['id'].split(':', 1)[0] for c in registered if ':' in c['id']}, key=len, reverse=True)
    return re.compile(r'\b(?:' + '|'.join(map(re.escape, prefixes)) + r'):[\w-]+', re.I) if prefixes else None


def class_table(notebook):
    """The notebook's class rows, or [] when it declares none."""
    path = pathlib.Path(notebook).parent / 'claim-classes.json'
    return json.loads(path.read_text())['classes'] if path.exists() else []


def notebook_marker(notebook):
    """The part of a record's URL that names this side notebook (records cite .../branches/NAME/#entry-...), or None
    for the main notebook, whose records carry no such part."""
    parts = pathlib.Path(notebook).resolve().parts
    return f'branches/{parts[-2]}/' if len(parts) > 2 and parts[-3] == 'branches' else None


def hypothesis_part(summary, ids):
    """The part of a registered summary read as its hypothesis, cited claim ids removed: the first colon-ended
    segment that quantifies an object, up to the first word that opens a conclusion (RELATION).  Summaries open
    with a setting ("For X_1..X_N i.i.d. uniform ..., with probability tending to one:") before their quantified
    objects, so the first colon alone hid most of the bounds (its reviewer, 18 October 2026); a conclusion may name
    a class only to bound it (Lip(G on Q) in a cellwise sum).  A heuristic: a conditional conclusion written
    inside the segment ("if ... then ... <= C") is read as hypothesis, the replay's false listings of two
    reductions (research/provenance/framework/class-tool-search-judgement-20261018.txt).  Two more limits, untested
    on the record: a hypothesis phrased with a conclusion word ("every G whose cells have ...") is cut early, and a
    setting that itself quantifies ("for every fixed kappa > 0, with probability tending to one: every union ...") is
    taken for the hypothesis (its reviewer, 18 October 2026)."""
    return split_summary(summary, ids)[0]


def split_summary(summary, ids):
    """(hypothesis part, the rest of the summary after it): the rest is where a class's "conclusion" is sought, so
    that "cost <= C" in a hypothesis does not pass for a bound (its reviewer, 18 October 2026)."""
    plain = ids.sub(' ', summary) if ids else summary
    segments = plain.split(':')
    index = next((i for i, s in enumerate(segments) if QUANTIFIED.search(s)), 0)
    head, *tail = RELATION.split(segments[index], 1)
    found = RELATION.search(segments[index])
    rest = (segments[index][found.start():] if found else '') + ':' + ':'.join(segments[index + 1:])
    return head.strip().lower(), rest


def object_classes(text, table, ids=None):
    """The names of the table's classes whose object words the text contains, with every class containing them."""
    plain = (ids.sub(' ', text) if ids else text).lower()
    found = [row['name'] for row in table if re.search(row['object'], plain, re.I)]
    within = {row['name']: row.get('within', []) for row in table}
    out, todo = [], list(found)
    while todo:
        name = todo.pop(0)
        if name not in out:
            out.append(name)
            todo.extend(within.get(name, []))
    return out


def class_listing(registered, text, table, marker, own=(), limit=CLASS_SHOWN):
    """[(class, [(registered id, summary start), ...], total), ...]: for each class the text's object is in, the
    notebook's proved claims (their record names MARKER) whose hypothesis takes the class, the newest LIMIT of them;
    TOTAL counts them all.  A reading list in the words of the object's class: each is applied to the object before
    a new method is drafted (AGENTS.md), and the finisher asks the entry to name each (resemblance_coverage)."""
    ids = claim_id_pattern(registered)
    rows = {row['name']: row for row in table}
    local = [c for c in registered if c['id'] not in own and c.get('mathematical_status') in CLASS_STATUSES
             and marker in json.dumps(c.get('record'))]
    out = []
    parts = {c['id']: split_summary(c.get('summary', ''), ids) for c in local}
    for name in object_classes(text, table, ids):
        # a row's optional "conclusion" keeps the listing to claims concluding the kind of bound the class asks
        conclusion = rows[name].get('conclusion')
        hits = [(c['id'], c.get('summary', '')[:120]) for c in local
                if re.search(rows[name]['hypothesis'], parts[c['id']][0], re.I)
                and (not conclusion or re.search(conclusion, parts[c['id']][1], re.I))]
        if hits:
            out.append((name, hits[-limit:], len(hits)))
    return out


def class_bounds(registered, spec, table, marker, limit=CLASS_SHOWN):
    """[(draft id, class, rows, total), ...]: class_listing for each claim of the spec, by its summary."""
    own = {claim['id'] for claim in spec.get('claims', [])}
    return [(claim['id'], name, rows, total) for claim in spec.get('claims', [])
            for name, rows, total in class_listing(registered, claim.get('summary', ''), table, marker, own, limit)]


def class_replay(registered, table, marker):
    """Lines listing, for every proved claim of the notebook taken as a one-claim spec against the claims
    registered before it, each class it fires and the claims listed, for judging by hand, and the counts."""
    local = {c['id'] for c in registered if marker in json.dumps(c.get('record'))}
    lines, fired = [], 0
    for index, claim in enumerate(registered):
        if claim['id'] not in local:
            continue
        found = class_listing(registered[:index], claim.get('summary', ''), table, marker)
        if found:
            fired += 1
            lines.append(f'{claim["id"]}: ' + '; '.join(f'{name} ({total}): ' + ', '.join(i for i, _ in rows)
                                                       for name, rows, total in found))
    lines.append(f'{fired} of {len(local)} claims of {marker} fire a class, each against the claims registered '
                 f'before it; {len(table)} classes in the table.')
    return lines


SCHEMA = ROOT / 'research' / 'claims' / 'schema.json'
# spec field -> the schema's enumeration it must belong to ($defs path)
SPEC_ENUMS = {'status': ('claim', 'mathematical_status'), 'category': ('significance', 'category'),
              'novelty': ('significance', 'novelty')}
RELATION_ENUM = ('relationship', 'type')


def spec_value_problems(spec, schema=None):
    """The spec's values that registration would refuse by the registry schema's enumerations: each claim's status,
    category and novelty and each relationship's type.  Registration found them only after the entry was appended
    (16 October 2026: "computation" as a category), so the run made when the spec is first drafted reports them."""
    defs = json.loads((schema or SCHEMA).read_text())['$defs']
    allowed = lambda where: [v for v in defs[where[0]]['properties'][where[1]]['enum'] if v is not None]
    found = []
    for item in spec.get('claims', []):
        for field, where in SPEC_ENUMS.items():
            if field in item and item[field] not in allowed(where):
                found.append(f'{item.get("id", "?")}: {field} {item[field]!r} is not one of {", ".join(allowed(where))}')
    for edge in spec.get('relationships', []):
        if len(edge) > 1 and edge[1] not in allowed(RELATION_ENUM):
            found.append(f'{edge[0]} -> {edge[2] if len(edge) > 2 else "?"}: relationship {edge[1]!r} is not one of '
                         + ', '.join(allowed(RELATION_ENUM)))
    return found


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('spec', nargs='?')
    parser.add_argument('--count', type=int, default=5)
    parser.add_argument('--registry', default=str(DEFAULT_REGISTRY))
    parser.add_argument('--notebook', help='notebook file whose queue is compared (default: the selected one)')
    parser.add_argument('--text', help='print only the class listing for this text (a next attempt, a Smallest '
                                       'case), before any spec exists')
    parser.add_argument('--replay', action='store_true', help='print only the class listing of every proved claim '
                                                              'of the notebook against the claims before it')
    args = parser.parse_args(argv)
    registered = json.loads(pathlib.Path(args.registry).read_text())['claims']
    if args.text is not None or args.replay:
        import notebooks
        notebook = (notebooks.notebook_file(args.notebook) if args.notebook
                    else ROOT / notebooks.selected()['source'])
        table, marker = class_table(notebook), notebook_marker(notebook)
        if not table or not marker:
            print(f'No class listing: {pathlib.Path(notebook).parent / "claim-classes.json"} '
                  + ('does not exist.' if not table else 'belongs to the main notebook, whose records name no branch.'))
            return 0
        if args.replay:
            print('\n'.join(class_replay(registered, table, marker)))
            return 0
        # the pre-spec run is optional (no check requires it); it is logged with the record searches
        if args.registry == str(DEFAULT_REGISTRY):
            log_run(['--text', args.text[:200]])
        found = class_listing(registered, args.text, table, marker)
        for name, rows, total in found:
            print(f'The text\'s object is in the recorded class "{name}"; {total} proved claims of this notebook '
                  'read as taking it as a hypothesis (a heuristic reading): apply each to the object before '
                  'drafting a new method'
                  + (f' (the newest {len(rows)} shown)' if total > len(rows) else ''))
            for other, start in rows:
                print(f'  {other}: {start}')
        print(f'{len(found)} class listings; classes named by the text: '
              + (', '.join(object_classes(args.text, table, claim_id_pattern(registered))) or 'none'))
        return 0
    if not args.spec:
        parser.error('a spec is needed unless --text or --replay is given')
    spec = json.loads(pathlib.Path(args.spec).read_text())
    if args.registry == str(DEFAULT_REGISTRY):       # a run on the record: logged for the finisher, as searches are
        log_run([claim['id'] for claim in spec.get('claims', [])])
    problems = spec_value_problems(spec)
    for problem in problems:
        print('Spec value registration would refuse: ' + problem)
    print(f'{len(registered)} registered claims compared; registration refuses a score of {SIMILAR_AT} or more '
          'unless the spec relates the two.')
    related = {tuple(edge[:1] + edge[2:3]) for edge in spec.get('relationships', [])}
    for ident, found in resemblances(registered, spec, args.count):
        print(f'{ident}:')
        for score, other, start in found:
            mark = ' (related in the spec)' if (ident, other) in related or (other, ident) in related else ''
            print(f'  {score:.2f} {other}{mark}: {start}')
        if found:
            # 16 October 2026: a listed claim was a more general version of the new one, unread as such.
            print('  Read each listed statement and say in the entry whether it is a more general version of '
                  'this claim (fewer hypotheses, the same conclusion) or a special case of it.')
            # 17 October 2026: a listed lemma, read only for generality, already answered the entry's next
            # attempt for one of its cases.
            print('  Then apply each to the entry\'s next attempt and its Smallest case: write under Own statements '
                  'what it already decides there, or that it decides nothing.')
    found_siblings = siblings(registered, spec)
    for related_id, rows in found_siblings:
        print(f'Registered beside {related_id}, which the spec relates (same record entry), and not related in '
              'the spec: read each; one may already imply a claim of the spec')
        for other, start in rows:
            print(f'  {other}: {start}')
    print(f'{sum(len(rows) for _, rows in found_siblings)} sibling claims listed for '
          f'{len(found_siblings)} related claims with siblings.')
    if args.notebook or args.registry == str(DEFAULT_REGISTRY):
        import lead_queue
        if args.notebook:
            import notebooks
            notebook = notebooks.notebook_file(args.notebook)
        else:
            import notebooks
            notebook = ROOT / notebooks.selected()['source']
        text = notebook.read_text()
        table, marker = class_table(notebook), notebook_marker(notebook)
        found_classes = class_bounds(registered, spec, table, marker) if table and marker else []
        for ident, name, rows, total in found_classes:
            print(f'{ident}: its object is in the recorded class "{name}"; {total} proved claims of this notebook '
                  'read as taking that class as a hypothesis (a heuristic reading): apply each to the object '
                  'before drafting a new method, and name each in the entry (the finisher checks naming)'
                  + (f' (the newest {len(rows)} shown)' if total > len(rows) else ''))
            for other, start in rows:
                print(f'  {other}: {start}')
        if table and marker:
            print(f'{len(found_classes)} class listings for {len(spec.get("claims", []))} claims, from '
                  f'{sum(marker in json.dumps(c.get("record")) for c in registered)} registered claims of {marker}.')
        else:
            print('No class listing: the notebook declares no claim-classes.json, or is the main notebook.')
        for ident, rows in context_matches(context_sentences(text), spec):
            print(f'{ident}: nearest Working mathematical context sentences (read each; a result stated there is '
                  'not new):')
            for share, sentence, link in rows:
                print(f'  {share:.2f} {sentence[:200]}' + (f' [{link}]' if link else ''))
        found = lead_queue.parse_tree(text)
        nodes = found[1] if found else []
        count = sum(1 + len(n.children) for n in nodes)
        matches = queued_matches(nodes, spec)
        print(f'{count} queued items compared; a share of {QUEUED_AT} or more of an item\'s words is listed.')
        for share, ident, queued in matches:
            print(f'  {share:.2f} {ident} ~ queued {queued}: read the item; if the claim answers it, close it '
                  'in this entry\'s follow-up list')
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
